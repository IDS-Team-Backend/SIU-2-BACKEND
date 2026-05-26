"""Stub de base de datos para los tests E2E.

Reemplaza ``db.execute_query`` (que en producción usa MySQL vía
``mysql.connector``) por una versión que ejecuta el mismo SQL contra una
base SQLite en memoria. Así los tests recorren el flujo completo
router → service → repository → ``db.execute_query`` sin necesidad de
levantar MySQL ni Docker.

Diferencias SQL que se traducen acá:

- MySQL usa ``%s`` como placeholder, SQLite usa ``?``.
- MySQL tiene ``NOW()``, SQLite usa ``CURRENT_TIMESTAMP``.

Si en el futuro algún repository usa una función MySQL-only nueva, hay
que agregar la traducción en ``_traducir_sql``.
"""

import sqlite3


# ─── Schema ──────────────────────────────────────────────────────────────
#
# Refleja ``backend/schema.sql`` pero adaptado a SQLite: ``INT
# AUTO_INCREMENT`` → ``INTEGER PRIMARY KEY AUTOINCREMENT``, ``BOOLEAN``
# se guarda como 0/1, los ``ENGINE=InnoDB`` y ``CHARACTER SET`` se
# omiten. Los ENUM de MySQL se modelan como TEXT con CHECK.

SCHEMA = [
    """CREATE TABLE materias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        codigo TEXT UNIQUE
    )""",

    """CREATE TABLE tipos_evaluacion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        es_grupal INTEGER NOT NULL DEFAULT 0
    )""",

    """CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        dni INTEGER NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        es_admin INTEGER NOT NULL DEFAULT 0,
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""",

    """CREATE TABLE estudiantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL UNIQUE,
        padron INTEGER NOT NULL UNIQUE,
        carrera TEXT NOT NULL,
        anio_ingreso INTEGER NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE profesores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL UNIQUE,
        legajo INTEGER NOT NULL UNIQUE,
        titulo TEXT NOT NULL,
        departamento TEXT NOT NULL,
        fecha_ingreso TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE cursos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        materia_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        anio INTEGER NOT NULL,
        cuatrimestre INTEGER NOT NULL,
        FOREIGN KEY (materia_id) REFERENCES materias(id)
    )""",

    """CREATE TABLE curso_usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso_id INTEGER NOT NULL,
        usuario_id INTEGER NOT NULL,
        estado TEXT NOT NULL DEFAULT 'activo',
        fecha_inscripcion TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (curso_id, usuario_id),
        FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE evaluaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso_id INTEGER NOT NULL,
        tipo_evaluacion_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        fecha TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
        FOREIGN KEY (tipo_evaluacion_id) REFERENCES tipos_evaluacion(id)
    )""",

    """CREATE TABLE equipos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso_id INTEGER NOT NULL,
        evaluacion_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        evaluacion_id INTEGER NOT NULL,
        alumno_id INTEGER,
        equipo_id INTEGER,
        nota REAL NOT NULL,
        observaciones TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (evaluacion_id) REFERENCES evaluaciones(id) ON DELETE CASCADE,
        FOREIGN KEY (alumno_id) REFERENCES estudiantes(id),
        FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE equipo_integrantes (
        equipo_id INTEGER NOT NULL,
        alumno_id INTEGER NOT NULL,
        PRIMARY KEY (equipo_id, alumno_id),
        FOREIGN KEY (equipo_id) REFERENCES equipos(id) ON DELETE CASCADE,
        FOREIGN KEY (alumno_id) REFERENCES estudiantes(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE clases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        profesor_id INTEGER NOT NULL,
        curso_id INTEGER NOT NULL,
        fecha_hora_inicio TEXT NOT NULL,
        fecha_hora_fin TEXT NOT NULL,
        tema TEXT,
        status TEXT NOT NULL DEFAULT 'pendiente',
        deleted_at TEXT DEFAULT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (profesor_id) REFERENCES profesores(id),
        FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE qr_asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clase_id INTEGER NOT NULL,
        token TEXT NOT NULL UNIQUE,
        expiracion TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (clase_id) REFERENCES clases(id) ON DELETE CASCADE
    )""",

    """CREATE TABLE asistencias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clase_id INTEGER NOT NULL,
        alumno_id INTEGER NOT NULL,
        fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (clase_id, alumno_id),
        FOREIGN KEY (clase_id) REFERENCES clases(id) ON DELETE CASCADE,
        FOREIGN KEY (alumno_id) REFERENCES estudiantes(id)
    )""",

    """CREATE TABLE materiales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curso_id INTEGER NOT NULL,
        titulo TEXT NOT NULL,
        archivo_url TEXT NOT NULL,
        subido_por INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE,
        FOREIGN KEY (subido_por) REFERENCES usuarios(id) ON DELETE SET NULL
    )""",

    """CREATE TABLE logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        accion TEXT NOT NULL,
        endpoint TEXT,
        metodo TEXT,
        detalle TEXT,
        fecha TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
    )""",
]


# Orden de borrado: empezar por las tablas hijas para no violar FKs.
TABLAS_EN_ORDEN_DE_BORRADO = (
    "logs",
    "materiales",
    "asistencias",
    "qr_asistencia",
    "clases",
    "equipo_integrantes",
    "notas",
    "equipos",
    "evaluaciones",
    "curso_usuarios",
    "cursos",
    "profesores",
    "estudiantes",
    "usuarios",
    "tipos_evaluacion",
    "materias",
)


# La conexión vive durante toda la sesión de tests; se resetean filas
# entre tests con ``reset()``.
_conn = None


def _traducir_sql(query):
    """Adapta sintaxis MySQL a SQLite.

    El código de producción usa placeholders ``%s`` y la función
    ``NOW()``. SQLite no entiende ninguno de los dos. Esta traducción
    es deliberadamente simple: si en el futuro aparece otra diferencia,
    se agrega acá y listo.
    """
    return query.replace("%s", "?").replace("NOW()", "CURRENT_TIMESTAMP")


def fake_execute_query(query, params=(), modifica_db=False, un_solo_valor=False):
    """Versión de ``db.execute_query`` para tests.

    Mantiene la misma firma y los mismos contratos que la función real
    para que los repositorios funcionen sin saber que están corriendo
    contra SQLite.
    """
    sql = _traducir_sql(query)
    cur = _conn.cursor()
    cur.execute(sql, tuple(params))

    if not modifica_db:
        filas = [dict(fila) for fila in cur.fetchall()]
        if un_solo_valor:
            return filas[0] if filas else None
        return filas

    _conn.commit()
    if query.strip().upper().startswith("INSERT"):
        return cur.lastrowid
    return cur.rowcount


def init():
    """Crea la conexión y aplica el schema. Idempotente."""
    global _conn
    if _conn is not None:
        return
    _conn = sqlite3.connect(":memory:", check_same_thread=False)
    _conn.row_factory = sqlite3.Row
    _conn.execute("PRAGMA foreign_keys = ON")
    for sentencia in SCHEMA:
        _conn.execute(sentencia)
    _conn.commit()


def reset():
    """Borra todas las filas y resetea los autoincrement.

    Se ejecuta entre tests para que cada uno arranque con la DB vacía
    sin pagar el costo de recrear el schema.
    """
    for tabla in TABLAS_EN_ORDEN_DE_BORRADO:
        _conn.execute(f"DELETE FROM {tabla}")
        _conn.execute("DELETE FROM sqlite_sequence WHERE name = ?", (tabla,))
    _conn.commit()
