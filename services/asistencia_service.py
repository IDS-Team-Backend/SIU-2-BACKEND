from datetime import datetime, timedelta

import repositories.asistencia_repository as db
from repositories import cursos_repository, estudiantes_repository
import repositories.estudiante_curso_repository as estudiante_curso_db
import repositories.curso_docentes_repository as curso_docentes_db
import repositories.profesores_repository as profesores_repository
from constants import ADMIN
from utils import auth_validator as auth
from utils.error_handlers import NotFoundError, UnauthorizedError, ValidationError


ASISTENCIA_ESTADOS_VALIDOS = {"presente", "ausente", "tarde", "justificada"}
MINUTOS_TOLERANCIA_TARDE = 15


def _serializar_valor(valor):
	if isinstance(valor, datetime):
		return valor.isoformat(sep=" ", timespec="seconds")
	if isinstance(valor, dict):
		return {clave: _serializar_valor(item) for clave, item in valor.items()}
	if isinstance(valor, list):
		return [_serializar_valor(item) for item in valor]
	return valor


def _validar_clase_existe(clase_id):
	if not isinstance(clase_id, int) or clase_id <= 0:
		raise ValidationError("El ID de la clase debe ser un entero positivo.")

	clase = db.obtener_clase_por_id(clase_id)
	if not clase:
		raise NotFoundError("Clase no encontrada.")

	return clase


def _obtener_estudiante_por_usuario_id(usuario_id):
	from repositories import estudiantes_repository
	estudiante = estudiantes_repository.obtener_estudiante_por_usuario_id(usuario_id)
	if not estudiante:
		raise NotFoundError("El usuario no tiene un perfil estudiante activo.")
	return estudiante


def _validar_estado_asistencia(estado):
	if not isinstance(estado, str) or not estado.strip():
		raise ValidationError("El estado de asistencia es obligatorio.")

	estado = estado.strip().lower()
	if estado not in ASISTENCIA_ESTADOS_VALIDOS:
		raise ValidationError(
			f"Estado de asistencia inválido. Estados válidos: {', '.join(sorted(ASISTENCIA_ESTADOS_VALIDOS))}"
		)
	return estado


def _validar_permiso_docente_sobre_clase(clase):
	if auth.usuario_es(ADMIN):
		return

	docente = profesores_repository.obtener_profesor_por_usuario_id(auth.obtener_usuario_id())
	if not docente:
		raise UnauthorizedError("No tenés un perfil docente activo.")

	if not curso_docentes_db.docente_pertenece_activamente_a_curso(docente["id"], clase["curso_id"]):
		raise UnauthorizedError("No tenés permisos para gestionar esta clase.")


# ──────────────────────────────────────────────
# Escaneo de QR
# ──────────────────────────────────────────────

def escanear_qr(token, clase_id):
	if not isinstance(token, str) or not token.strip():
		raise ValidationError("El campo 'token' es obligatorio.")
	if not isinstance(clase_id, int) or clase_id <= 0:
		raise ValidationError("El campo 'clase_id' debe ser un entero positivo.")

	estudiante = estudiantes_repository.obtener_estudiante_por_token_qr(token.strip())
	if not estudiante:
		raise ValidationError("Token inválido.")

	clase = _validar_clase_existe(clase_id)

	if datetime.now() > clase["fecha_hora_fin"]:
		raise ValidationError("No se puede registrar asistencia: la clase ya finalizó.")

	inscripcion = estudiante_curso_db.obtener_estudiante_curso_por_estudiante_curso(
		estudiante["id"], clase["curso_id"]
	)
	if not inscripcion or inscripcion.get("estado") != "activo":
		raise ValidationError("El alumno no está inscripto activamente en este curso.")

	if db.obtener_asistencia_por_alumno_y_clase(estudiante["id"], clase_id):
		raise ValidationError("Asistencia ya registrada.")

	estado = (
		"tarde"
		if datetime.now() > clase["fecha_hora_inicio"] + timedelta(minutes=MINUTOS_TOLERANCIA_TARDE)
		else "presente"
	)

	db.upsert_asistencia(clase_id, estudiante["id"], estado)

	return {
		"asistencia": _serializar_valor({
			"alumno_id": estudiante["id"],
			"nombre": estudiante["nombre"],
			"apellido": estudiante["apellido"],
			"padron": estudiante["padron"],
			"clase_id": clase_id,
			"estado": estado,
			"fecha_registro": datetime.now(),
		})
	}


# ──────────────────────────────────────────────
# Listado y edición de asistencias (docente/admin)
# ──────────────────────────────────────────────

def obtener_asistencias_por_clase(clase_id):
	clase = _validar_clase_existe(clase_id)
	_validar_permiso_docente_sobre_clase(clase)

	asistencias = db.obtener_asistencias_de_clase(clase_id)

	return {
		"total": len(asistencias),
		"asistencias": [
			_serializar_valor({
				"alumno_id": a["alumno_id"],
				"nombre": a["nombre"],
				"apellido": a["apellido"],
				"padron": a["padron"],
				"estado": a["estado"],
				"fecha_registro": a["fecha_registro"],
			})
			for a in asistencias
		],
	}


def actualizar_asistencias_manualmente(clase_id, asistencias):
	clase = _validar_clase_existe(clase_id)
	_validar_permiso_docente_sobre_clase(clase)

	if not isinstance(asistencias, list) or not asistencias:
		raise ValidationError("El campo 'asistencias' debe ser una lista no vacía.")

	alumnos_inscriptos = db.obtener_alumnos_inscriptos_de_curso(clase["curso_id"])
	alumnos_validos = {alumno["alumno_id"] for alumno in alumnos_inscriptos}
	payload = []
	vistos = set()

	for item in asistencias:
		if not isinstance(item, dict):
			raise ValidationError("Cada asistencia debe ser un objeto JSON válido.")

		alumno_id = item.get("alumno_id")
		estado = _validar_estado_asistencia(item.get("estado"))

		if not isinstance(alumno_id, int) or alumno_id <= 0:
			raise ValidationError("Cada 'alumno_id' debe ser un entero positivo.")

		if alumno_id not in alumnos_validos:
			raise ValidationError(f"El alumno_id {alumno_id} no pertenece al curso de la clase.")

		if alumno_id in vistos:
			raise ValidationError(f"El alumno_id {alumno_id} está duplicado en el cuerpo de asistencias.")

		vistos.add(alumno_id)
		payload.append({"alumno_id": alumno_id, "estado": estado})

	db.bulk_upsert_asistencias(clase_id, payload)


def obtener_asistencias_de_alumno_en_curso(curso_id, alumno_id):
	if not isinstance(curso_id, int) or curso_id <= 0:
		raise ValidationError("El ID del curso debe ser un entero positivo.")

	curso = cursos_repository.obtener_curso_por_id(curso_id)
	if not curso:
		raise NotFoundError("Curso no encontrado")

	asistencias = db.obtener_asistencias_del_alumno_en_curso(curso_id, alumno_id)
	total_clases = len(asistencias)

	conteo_estados = {estado: 0 for estado in ASISTENCIA_ESTADOS_VALIDOS}
	detalle = []

	for asistencia in asistencias:
		estado = asistencia["estado"] or "ausente"
		conteo_estados[estado] = conteo_estados.get(estado, 0) + 1
		detalle.append(
			{
				"clase_id": asistencia["clase_id"],
				"clase_nombre": asistencia["clase_nombre"],
				"fecha_hora_inicio": asistencia["fecha_hora_inicio"],
				"estado": estado,
				"fecha_registro": asistencia["fecha_registro"],
			}
		)

	presentes = conteo_estados.get("presente", 0)
	tarde = conteo_estados.get("tarde", 0)
	porcentaje_asistencia = round(((presentes + tarde) / total_clases) * 100, 2) if total_clases else 0.0

	return {
		"asistencias": {
			"total_clases": total_clases,
			"presentes": presentes,
			"tarde": tarde,
			"ausentes": conteo_estados.get("ausente", 0),
			"justificadas": conteo_estados.get("justificada", 0),
			"porcentaje_asistencia": porcentaje_asistencia,
			"curso": curso["nombre"],
			"detalle": _serializar_valor(detalle),

		},
	}

def obtener_mis_asistencias(curso_id):
	if not isinstance(curso_id, int) or curso_id <= 0:
		raise ValidationError("El ID del curso debe ser un entero positivo.")

	usuario_id = auth.obtener_usuario_id()
	estudiante = _obtener_estudiante_por_usuario_id(usuario_id)

	inscripcion = estudiante_curso_db.obtener_estudiante_curso_por_estudiante_curso(
		estudiante["id"], curso_id
	)
	if not inscripcion or inscripcion.get("estado") != "activo":
		raise ValidationError("El alumno no está inscripto activamente en este curso.")

	return obtener_asistencias_de_alumno_en_curso(curso_id, estudiante["id"])


def obtener_mi_qr():
	usuario_id = auth.obtener_usuario_id()
	estudiante = _obtener_estudiante_por_usuario_id(usuario_id)

	if not estudiante.get("token_qr"):
		raise NotFoundError("No tenés un QR asignado aún.")

	return {"token_qr": estudiante["token_qr"]}