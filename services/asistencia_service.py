from datetime import datetime, timedelta
from uuid import uuid4

from clients.email_client import enviar_email_qr
import repositories.asistencia_repository as db
from repositories import cursos_repository, estudiantes_repository
import repositories.curso_docentes_repository as curso_docentes_db
import repositories.curso_usuarios_repository as curso_usuarios_db
import repositories.profesores_repository as profesores_repository
from config import ADMIN
from utils import auth_validator as auth
from utils.error_handlers import NotFoundError, UnauthorizedError, ValidationError


ASISTENCIA_ESTADOS_VALIDOS = {"presente", "ausente", "tarde", "justificada"}
EXPIRACION_QR_HORAS = 2
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
		raise NotFoundError("Clase no encontrada")

	return clase


def _obtener_estudiante_por_usuario_id(usuario_id):
	estudiante = estudiantes_repository.obtener_estudiante_por_usuario_id(usuario_id)
	if not estudiante or not estudiante.get("activo"):
		raise NotFoundError("El usuario no tiene un perfil estudiante activo.")
	return estudiante


def _validar_estado_asistencia(estado):
	if not isinstance(estado, str) or not estado.strip():
		raise ValidationError("El estado de asistencia es obligatorio.")

	estado = estado.strip().lower()
	if estado not in ASISTENCIA_ESTADOS_VALIDOS:
		raise ValidationError(
			f"Estado de asistencia invalido. Estados válidos: {', '.join(sorted(ASISTENCIA_ESTADOS_VALIDOS))}"
		)
	return estado

def _obtener_alumnos_inscriptos_a_clase(clase_id):
	clase = _validar_clase_existe(clase_id)
	alumnos = db.obtener_alumnos_inscriptos_de_curso(clase["curso_id"])
	return clase, alumnos


def _validar_permiso_docente_sobre_clase(clase):
	if auth.usuario_es(ADMIN):
		return

	docente = profesores_repository.obtener_profesor_por_usuario_id(auth.obtener_usuario_id())
	if not docente or not docente.get("activo"):
		raise UnauthorizedError("No tenés un perfil docente activo.")

	if not curso_docentes_db.docente_pertenece_activamente_a_curso(docente["id"], clase["curso_id"]):
		raise UnauthorizedError("No tenés permisos para gestionar esta clase.")


def generar_qrs_de_asistencia(clase_id):
	clase, alumnos = _obtener_alumnos_inscriptos_a_clase(clase_id)
	_validar_permiso_docente_sobre_clase(clase)

	if not alumnos:
		raise ValidationError("No hay alumnos inscriptos en el curso de la clase.")

	expiracion = datetime.now() + timedelta(hours=EXPIRACION_QR_HORAS)
	qrs = []
	notificaciones = []

	for alumno in alumnos:
		token = str(uuid4())
		qrs.append((clase_id, alumno["alumno_id"], token, expiracion))
		notificaciones.append(
			{
				"email": alumno["email"],
				"nombre": alumno["nombre"],
				"apellido": alumno["apellido"],
				"clase": clase["nombre"],
				"expiracion": expiracion,
				"token": token,
			}
		)

	db.guardar_qrs(clase_id, qrs)

	for notificacion in notificaciones:
		print(
			f"[ASISTENCIA] QR generado para {notificacion['nombre']} {notificacion['apellido']} ({notificacion['email']}) en la clase {notificacion['clase']}. token: {token}",
			flush=True,
		)

		enviar_email_qr(
			to="ffernandez.joaco@gmail.com",
			subject=f"QR de Asistencia - {notificacion['clase']}",
			nombre_alumno=notificacion["nombre"],
			apellido_alumno=notificacion["apellido"],
			clase_nombre=notificacion["clase"],
			token=notificacion["token"],
			expiracion=notificacion["expiracion"],
		)

	return 


def escanear_qr(token):
	if not isinstance(token, str) or not token.strip():
		raise ValidationError("El campo 'token' es obligatorio.")

	qr = db.consumir_qr_por_token(token.strip())
	if not qr:
		raise ValidationError("Token inválido o expirado.")

	if qr.get("ya_consumido"):
		raise ValidationError("El token ya fue escaneado.")

	if qr.get("expirado"):
		raise ValidationError("Token inválido o expirado.")
	
	estado_asistencia = ""
	if datetime.now() > qr["fecha_hora_inicio"] + timedelta(minutes=MINUTOS_TOLERANCIA_TARDE):
		estado_asistencia = "tarde"
	else:
		estado_asistencia = "presente"
		

	db.upsert_asistencia(qr["clase_id"], qr["alumno_id"], estado_asistencia)

	return {
		"asistencia": _serializar_valor(
			{
				"alumno_id": qr["alumno_id"],
				"nombre": qr["nombre"],
				"apellido": qr["apellido"],
				"padron": qr["padron"],
				"clase_id": qr["clase_id"],
				"estado": estado_asistencia,
				"fecha_registro": datetime.now(),
			}
		)
	}


def obtener_asistencias_por_clase(clase_id):
	clase = _validar_clase_existe(clase_id)
	_validar_permiso_docente_sobre_clase(clase)
	asistencias = db.obtener_asistencias_de_clase(clase_id)

	return {
		"total": len(asistencias),
		"asistencias": [
			_serializar_valor(
				{
					"usuario_id": asistencia["usuario_id"],
					"nombre": asistencia["nombre"],
					"apellido": asistencia["apellido"],
					"padron": asistencia["padron"],
					"estado": asistencia["estado"],
					"fecha_registro": asistencia["fecha_registro"],
				}
			)
			for asistencia in asistencias
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


def obtener_mis_asistencias(curso_id):
	if not isinstance(curso_id, int) or curso_id <= 0:
		raise ValidationError("El ID del curso debe ser un entero positivo.")

	curso = cursos_repository.obtener_curso_por_id(curso_id)
	if not curso:
		raise NotFoundError("Curso no encontrado")

	usuario_id = auth.obtener_usuario_id()
	estudiante = _obtener_estudiante_por_usuario_id(usuario_id)

	inscripcion = curso_usuarios_db.obtener_por_usuario_curso(usuario_id, curso_id)
	if not inscripcion or inscripcion.get("estado") != "activo":
		raise ValidationError("El alumno no está inscripto activamente en este curso.")

	asistencias = db.obtener_asistencias_del_alumno_en_curso(curso_id, estudiante["id"])
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


