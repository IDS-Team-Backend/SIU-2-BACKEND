"""Factories: helpers para crear datos de prueba.

Cada función inserta una fila vía el repository correspondiente (no
tocando la DB directamente) y devuelve el dict del recurso recién
creado. Los parámetros tienen defaults razonables para que cada test
sólo especifique lo que realmente le importa.

Las factories generan valores únicos automáticamente (DNI, padrón,
legajo, código de materia) usando un contador global, de modo que dos
llamadas seguidas sin argumentos no chocan por UNIQUE constraints.
"""

from datetime import datetime, timedelta

import repositories.usuarios_repository as usuarios_db
import repositories.estudiantes_repository as estudiantes_db
import repositories.profesores_repository as profesores_db
import repositories.materias_repository as materias_db
import repositories.cursos_repository as cursos_db
import repositories.clases_repository as clases_db
import repositories.evaluaciones_repository as evaluaciones_db
import db


# Contador para generar valores únicos sin colisiones entre llamadas.
_contador = 0


def _siguiente():
    global _contador
    _contador += 1
    return _contador


def reset_contador():
    """Resetea el contador entre tests. Lo llama el fixture de limpieza."""
    global _contador
    _contador = 0


# ─── Usuarios ────────────────────────────────────────────────────────────

def crear_usuario(nombre="Test", apellido="User", email=None, dni=None,
                  password="secret123", es_admin=False):
    """Crea un usuario. Si no se pasa ``email`` o ``dni``, genera valores
    únicos para evitar colisiones por UNIQUE constraints."""
    n = _siguiente()
    if email is None:
        email = f"user{n}@test.com"
    if dni is None:
        dni = 30_000_000 + n
    return usuarios_db.crear_usuario(nombre, apellido, email, dni, password, es_admin)


def crear_admin(email=None, dni=None):
    return crear_usuario(
        nombre="Admin", apellido="Test",
        email=email, dni=dni, es_admin=True,
    )


# ─── Perfiles (estudiante / profesor) ────────────────────────────────────

def crear_estudiante(usuario_id, padron=None, carrera="Informática",
                     anio_ingreso=2024):
    if padron is None:
        padron = 100_000 + _siguiente()
    return estudiantes_db.crear_estudiante(usuario_id, padron, carrera, anio_ingreso)


def crear_profesor(usuario_id, legajo=None, titulo="Ingeniero",
                   departamento="Informática", fecha_ingreso="2020-03-01"):
    if legajo is None:
        legajo = 500_000 + _siguiente()
    return profesores_db.crear_profesor(usuario_id, legajo, titulo, departamento, fecha_ingreso)


def crear_usuario_con_perfil_alumno(**kwargs_usuario):
    """Atajo: crea usuario + perfil estudiante y devuelve ambos.

    Útil en tests que necesitan un alumno listo para usar."""
    usuario = crear_usuario(**kwargs_usuario)
    estudiante = crear_estudiante(usuario["id"])
    return {"usuario": usuario, "estudiante": estudiante}


def crear_usuario_con_perfil_docente(**kwargs_usuario):
    """Atajo: crea usuario + perfil profesor y devuelve ambos."""
    usuario = crear_usuario(**kwargs_usuario)
    profesor = crear_profesor(usuario["id"])
    return {"usuario": usuario, "profesor": profesor}


# ─── Materias y cursos ───────────────────────────────────────────────────

def crear_materia(nombre=None, codigo=None):
    n = _siguiente()
    if nombre is None:
        nombre = f"Materia {n}"
    if codigo is None:
        codigo = f"MAT{n:04d}"
    return materias_db.crear_materia(nombre, codigo)


def crear_curso(materia_id=None, nombre=None, anio=2024, cuatrimestre=1):
    if materia_id is None:
        materia_id = crear_materia()["id"]
    if nombre is None:
        nombre = f"Curso {_siguiente()}"
    return cursos_db.crear_cursos(materia_id, nombre, anio, cuatrimestre)


# ─── Clases ──────────────────────────────────────────────────────────────

def _proxima_fecha_clase(dias_adelante=1, hora_inicio=10, hora_fin=12):
    """Genera un rango ``(inicio, fin)`` en el futuro, mismo día.

    El validator de clases rechaza fechas pasadas y rangos que cruzan
    medianoche, así que usamos siempre mañana + N por defecto."""
    dia = datetime.now().date() + timedelta(days=dias_adelante)
    inicio = datetime.combine(dia, datetime.min.time()).replace(hour=hora_inicio)
    fin = datetime.combine(dia, datetime.min.time()).replace(hour=hora_fin)
    fmt = "%Y-%m-%d %H:%M:%S"
    return inicio.strftime(fmt), fin.strftime(fmt)


def crear_clase(profesor_id=None, curso_id=None, nombre=None,
                fecha_hora_inicio=None, fecha_hora_fin=None,
                tema="Tema de prueba", status="pendiente"):
    """Crea una clase. Si faltan profesor/curso, los genera al vuelo.

    Las fechas se generan en el futuro y en horario válido, salvo que
    el test las provea explícitamente (por ejemplo, para probar
    superposiciones)."""
    if profesor_id is None:
        usuario = crear_usuario()
        profesor_id = crear_profesor(usuario["id"])["id"]
    if curso_id is None:
        curso_id = crear_curso()["id"]
    if nombre is None:
        nombre = f"Clase {_siguiente()}"
    if fecha_hora_inicio is None or fecha_hora_fin is None:
        inicio_default, fin_default = _proxima_fecha_clase(dias_adelante=_siguiente())
        fecha_hora_inicio = fecha_hora_inicio or inicio_default
        fecha_hora_fin = fecha_hora_fin or fin_default
    return clases_db.crear_clase(
        nombre, profesor_id, curso_id,
        fecha_hora_inicio, fecha_hora_fin,
        tema, status,
    )


# ─── Evaluaciones ────────────────────────────────────────────────────────

def crear_tipo_evaluacion(nombre=None, es_grupal=False):
    """Inserta un ``tipos_evaluacion``. Usamos SQL directo porque el
    backend no expone repository para esta tabla (los tests son los
    únicos que la siembran)."""
    if nombre is None:
        nombre = f"Tipo {_siguiente()}"
    nuevo_id = db.execute_query(
        "INSERT INTO tipos_evaluacion (nombre, es_grupal) VALUES (%s, %s)",
        (nombre, int(es_grupal)),
        modifica_db=True,
    )
    return {"id": nuevo_id, "nombre": nombre, "es_grupal": int(es_grupal)}


def crear_evaluacion(curso_id=None, tipo_evaluacion_id=None, titulo=None,
                     descripcion=None, fecha="2024-06-15"):
    if curso_id is None:
        curso_id = crear_curso()["id"]
    if tipo_evaluacion_id is None:
        tipo_evaluacion_id = crear_tipo_evaluacion()["id"]
    if titulo is None:
        titulo = f"Evaluación {_siguiente()}"
    return evaluaciones_db.crear_evaluacion(
        curso_id, tipo_evaluacion_id, titulo, descripcion, fecha,
    )
