import db
from config import ADMIN, DOCENTE, ALUMNO


def obtener_perfiles_de_usuario(usuario_id):
    perfiles = []

    fila = db.execute_query(
        "SELECT es_admin FROM usuarios WHERE id = %s",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["es_admin"]:
        perfiles.append(ADMIN)

    fila = db.execute_query(
        "SELECT COUNT(*) AS total FROM profesores WHERE usuario_id = %s AND activo = TRUE",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["total"] > 0:
        perfiles.append(DOCENTE)

    fila = db.execute_query(
        "SELECT COUNT(*) AS total FROM estudiantes WHERE usuario_id = %s AND activo = TRUE",
        (usuario_id,),
        un_solo_valor=True,
    )
    if fila and fila["total"] > 0:
        perfiles.append(ALUMNO)

    return perfiles
