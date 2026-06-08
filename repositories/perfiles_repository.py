import db
from constants import ADMIN, DOCENTE, ALUMNO


def obtener_perfiles_de_usuario(usuario_id):
    perfiles = []

    # 1. Usuarios: Ya migrado al nuevo sistema
    fila = db.execute_query(
        "SELECT es_admin FROM usuarios WHERE id = %s AND deleted_at IS NULL",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["es_admin"]:
        perfiles.append(ADMIN)

    # 2. Profesores: Lo dejo con 'activo = TRUE' hasta que migremos la tabla
    # (Si ya corriste el ALTER TABLE en tu base, cambialo a 'deleted_at IS NULL')
    fila = db.execute_query(
        "SELECT COUNT(*) AS total FROM profesores WHERE usuario_id = %s AND activo = TRUE",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["total"] > 0:
        perfiles.append(DOCENTE)

    # 3. Estudiantes: ACÁ ESTABA EL ERROR. Ya migrado al nuevo sistema
    fila = db.execute_query(
        "SELECT COUNT(*) AS total FROM estudiantes WHERE usuario_id = %s AND deleted_at IS NULL",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["total"] > 0:
        perfiles.append(ALUMNO)

    return perfiles
