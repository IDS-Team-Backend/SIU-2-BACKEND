from datetime import datetime

import db


def obtener_clase_por_id(clase_id):
	query = """
		SELECT
			c.id,
			c.nombre,
			c.profesor_id,
			c.curso_id,
			c.fecha_hora_inicio,
			c.fecha_hora_fin,
			c.tema,
			c.status,
			c.deleted_at,
			c.created_at,
			cu.nombre AS curso_nombre
		FROM clases c
		INNER JOIN cursos cu ON cu.id = c.curso_id
		WHERE c.id = %s AND c.deleted_at IS NULL
	"""
	return db.execute_query(query, (clase_id,), un_solo_valor=True)


def obtener_alumnos_inscriptos_de_curso(curso_id):
	query = """
		SELECT
			e.id AS alumno_id,
			e.usuario_id,
			e.padron,
			e.carrera,
			e.anio_ingreso,
			e.activo,
			u.nombre,
			u.apellido,
			u.email,
			u.dni
		FROM curso_usuarios cu
		INNER JOIN estudiantes e ON e.usuario_id = cu.usuario_id
		INNER JOIN usuarios u ON u.id = e.usuario_id
		WHERE cu.curso_id = %s
		  AND cu.estado = 'activo'
		  AND e.activo = TRUE
		  AND u.activo = TRUE
		ORDER BY u.apellido ASC, u.nombre ASC, e.id ASC
	"""
	return db.execute_query(query, (curso_id,)) or []


def guardar_qrs(clase_id, qrs):
	conn = db.get_connection()
	cursor = None
	try:
		cursor = conn.cursor(dictionary=True)
		query = """
			INSERT INTO qr_asistencia (clase_id, alumno_id, token, expiracion)
			VALUES (%s, %s, %s, %s)
			ON DUPLICATE KEY UPDATE
				token = VALUES(token),
				expiracion = VALUES(expiracion)
		"""
		cursor.executemany(query, qrs)
		conn.commit()
		return cursor.rowcount
	except Exception as e:
		if conn:
			conn.rollback()
		raise Exception(f"Error al guardar QRs de asistencia: {e}") from e
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()


def obtener_qr_por_token(token):
	query = """
		SELECT
			qa.clase_id,
			qa.alumno_id,
			e.padron,
			u.nombre,
			u.apellido,
			c.fecha_hora_inicio,
			qa.expiracion
		FROM qr_asistencia qa
		INNER JOIN clases c ON c.id = qa.clase_id
		INNER JOIN estudiantes e ON e.id = qa.alumno_id
		INNER JOIN usuarios u ON u.id = e.usuario_id
		WHERE qa.token = %s
	"""
	return db.execute_query(query, (token,), un_solo_valor=True)


def upsert_asistencia(clase_id, alumno_id, estado):
	query = """
		INSERT INTO asistencias (clase_id, alumno_id, estado)
		VALUES (%s, %s, %s)
		ON DUPLICATE KEY UPDATE estado = VALUES(estado)
	"""
	return db.execute_query(query, (clase_id, alumno_id, estado), modifica_db=True)


def obtener_asistencias_de_clase(clase_id):
	query = """
		SELECT
			e.id AS alumno_id,
			e.usuario_id,
			e.padron,
			u.nombre,
			u.apellido,
			a.estado,
			a.fecha_registro
		FROM curso_usuarios cu
		INNER JOIN estudiantes e ON e.usuario_id = cu.usuario_id
		INNER JOIN usuarios u ON u.id = e.usuario_id
		LEFT JOIN asistencias a
			ON a.clase_id = %s
		   AND a.alumno_id = e.id
		INNER JOIN clases c ON c.id = %s AND c.curso_id = cu.curso_id
		WHERE cu.estado = 'activo'
		  AND e.activo = TRUE
		  AND u.activo = TRUE
		  AND c.deleted_at IS NULL
		ORDER BY u.apellido ASC, u.nombre ASC, e.id ASC
	"""
	return db.execute_query(query, (clase_id, clase_id)) or []


def bulk_upsert_asistencias(clase_id, asistencias):
	conn = db.get_connection()
	cursor = None
	try:
		cursor = conn.cursor(dictionary=True)
		query = """
			INSERT INTO asistencias (clase_id, alumno_id, estado)
			VALUES (%s, %s, %s)
			ON DUPLICATE KEY UPDATE estado = VALUES(estado)
		"""
		data = [(clase_id, asistencia["alumno_id"], asistencia["estado"]) for asistencia in asistencias]
		cursor.executemany(query, data)
		conn.commit()
		return cursor.rowcount
	except Exception as e:
		if conn:
			conn.rollback()
		raise Exception(f"Error al actualizar asistencias: {e}") from e
	finally:
		if cursor:
			cursor.close()
		if conn:
			conn.close()


def obtener_asistencias_del_alumno_en_curso(curso_id, alumno_id):
	query = """
		SELECT
			c.id AS clase_id,
			c.nombre AS clase_nombre,
			c.fecha_hora_inicio,
			COALESCE(a.estado, 'ausente') AS estado,
			a.fecha_registro
		FROM clases c
		LEFT JOIN asistencias a
			ON a.clase_id = c.id
		   AND a.alumno_id = %s
		WHERE c.curso_id = %s
		  AND c.deleted_at IS NULL
		  AND c.status = 'finalizada'
		ORDER BY c.fecha_hora_inicio ASC
	"""
	return db.execute_query(query, (alumno_id, curso_id)) or []
