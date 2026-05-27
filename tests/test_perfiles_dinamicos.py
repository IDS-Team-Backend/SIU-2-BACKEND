"""Tests del sistema de perfiles dinámicos.

Cubre:
- ``perfiles_repository.obtener_perfiles_de_usuario`` calcula desde las
  3 fuentes (es_admin, profesores activos, estudiantes activos).
- Soft-delete (``activo=FALSE``) saca el perfil de la lista.
- ``GET /auth/me/perfiles`` recalcula en vivo, no usa el JWT.
- ``@requiere_roles`` autoriza por intersección con ``perfiles[]`` del JWT.
"""

import repositories.perfiles_repository as perfiles_db

from tests.conftest import (
    crear_usuario_db,
    crear_perfil_estudiante,
    crear_perfil_profesor,
    login_como,
)


# ─── obtener_perfiles_de_usuario (unit-ish sobre el repo) ──────────

def test_perfiles_usuario_sin_perfiles_es_lista_vacia(client):
    user = crear_usuario_db(email="vacio@test.com", dni=10000001)
    perfiles = perfiles_db.obtener_perfiles_de_usuario(user["id"])
    assert perfiles == []


def test_perfiles_admin_devuelve_solo_admin(client):
    user = crear_usuario_db(email="ad@test.com", dni=10000002, es_admin=True)
    perfiles = perfiles_db.obtener_perfiles_de_usuario(user["id"])
    assert perfiles == ["admin"]


def test_perfiles_solo_estudiante(client):
    user = crear_usuario_db(email="es@test.com", dni=10000003)
    crear_perfil_estudiante(user["id"], padron=120001)
    assert perfiles_db.obtener_perfiles_de_usuario(user["id"]) == ["alumno"]


def test_perfiles_solo_docente(client):
    user = crear_usuario_db(email="do@test.com", dni=10000004)
    crear_perfil_profesor(user["id"], legajo=520001)
    assert perfiles_db.obtener_perfiles_de_usuario(user["id"]) == ["docente"]


def test_perfiles_admin_docente_estudiante_simultaneos(client):
    user = crear_usuario_db(email="todo@test.com", dni=10000005, es_admin=True)
    crear_perfil_estudiante(user["id"], padron=120002)
    crear_perfil_profesor(user["id"], legajo=520002)
    perfiles = perfiles_db.obtener_perfiles_de_usuario(user["id"])
    assert set(perfiles) == {"admin", "docente", "alumno"}


def test_perfiles_inactivos_no_aparecen(client):
    """Un estudiante/profesor con activo=FALSE pierde el perfil."""
    import repositories.estudiantes_repository as estudiantes_db
    import repositories.profesores_repository as profesores_db

    user = crear_usuario_db(email="inact@test.com", dni=10000006)
    est = crear_perfil_estudiante(user["id"], padron=120003)
    prof = crear_perfil_profesor(user["id"], legajo=520003)

    assert set(perfiles_db.obtener_perfiles_de_usuario(user["id"])) == {"alumno", "docente"}

    estudiantes_db.eliminar_estudiante(est["id"])
    assert perfiles_db.obtener_perfiles_de_usuario(user["id"]) == ["docente"]

    profesores_db.eliminar_profesor(prof["id"])
    assert perfiles_db.obtener_perfiles_de_usuario(user["id"]) == []


# ─── GET /auth/me/perfiles ─────────────────────────────────────────

def test_get_mis_perfiles_devuelve_lista_desde_db(client):
    user = crear_usuario_db(email="me1@test.com", dni=20000001, es_admin=True)
    crear_perfil_estudiante(user["id"], padron=130001)
    login_como(client, user, ["admin", "alumno"])

    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 200
    perfiles = resp.get_json()["perfiles"]
    assert set(perfiles) == {"admin", "alumno"}


def test_get_mis_perfiles_recalcula_aunque_jwt_este_desactualizado(client):
    """Si el JWT lleva perfiles viejos pero el admin agregó nuevos perfiles
    después del login, /auth/me/perfiles refleja la realidad de la DB."""
    user = crear_usuario_db(email="me2@test.com", dni=20000002)
    # JWT con perfiles=[] (estado al login)
    login_como(client, user, [])

    # Después del login, le agregan perfil profesor
    crear_perfil_profesor(user["id"], legajo=530001)

    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 200
    assert resp.get_json()["perfiles"] == ["docente"]


def test_get_mis_perfiles_sin_token_da_401(client):
    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 401


# ─── @requiere_roles: intersección con perfiles del JWT ────────────

def test_requiere_roles_admin_acepta_admin(client):
    user = crear_usuario_db(email="r1@test.com", dni=21000001, es_admin=True)
    login_como(client, user, ["admin"])
    # POST /estudiantes/ requiere @requiere_roles(ADMIN)
    otro = crear_usuario_db(email="r1b@test.com", dni=21000002)
    resp = client.post("/estudiantes/", json={
        "usuario_id": otro["id"], "padron": 140001,
        "carrera": "X", "anio_ingreso": 2024,
    })
    assert resp.status_code == 201


def test_requiere_roles_admin_deniega_a_alumno(client):
    user = crear_usuario_db(email="r2@test.com", dni=21000003)
    crear_perfil_estudiante(user["id"], padron=140002)
    login_como(client, user, ["alumno"])
    otro = crear_usuario_db(email="r2b@test.com", dni=21000004)
    resp = client.post("/estudiantes/", json={
        "usuario_id": otro["id"], "padron": 140003,
        "carrera": "X", "anio_ingreso": 2024,
    })
    assert resp.status_code == 403


def test_requiere_roles_acepta_si_hay_interseccion(client):
    """Un usuario con perfiles=[docente, alumno] pasa @requiere_roles(ADMIN, DOCENTE)."""
    user = crear_usuario_db(email="r3@test.com", dni=21000005)
    crear_perfil_estudiante(user["id"], padron=140004)
    prof = crear_perfil_profesor(user["id"], legajo=540001)
    login_como(client, user, ["docente", "alumno"])
    # GET /estudiantes/<id> requiere @requiere_roles(ADMIN, DOCENTE)
    est_propio = None
    import repositories.estudiantes_repository as estudiantes_db
    est_propio = estudiantes_db.obtener_estudiante_por_usuario_id(user["id"])
    resp = client.get(f"/estudiantes/{est_propio['id']}")
    assert resp.status_code == 200


def test_requiere_roles_deniega_si_no_hay_interseccion(client):
    """Un usuario con perfiles=[alumno] no pasa @requiere_roles(ADMIN, DOCENTE)."""
    user = crear_usuario_db(email="r4@test.com", dni=21000006)
    crear_perfil_estudiante(user["id"], padron=140005)
    login_como(client, user, ["alumno"])
    otro_user = crear_usuario_db(email="r4b@test.com", dni=21000007)
    import repositories.estudiantes_repository as estudiantes_db
    otro_est = estudiantes_db.crear_estudiante(otro_user["id"], 140006, "X", 2024)
    # GET /estudiantes/<id> requiere ADMIN o DOCENTE — alumno no entra.
    resp = client.get(f"/estudiantes/{otro_est['id']}")
    assert resp.status_code == 403


# ─── Flujo end-to-end multi-perfil ─────────────────────────────────

def test_flujo_multi_perfil_completo(client):
    """Admin crea usuario, le da los dos perfiles, el usuario opera con ambos."""
    # 1) Admin loguea
    admin = crear_usuario_db(email="adm@test.com", dni=22000001, es_admin=True)
    login_como(client, admin, ["admin"])

    # 2) Crea un usuario y le da perfil estudiante
    nuevo = crear_usuario_db(email="multi2@test.com", dni=22000002)
    resp = client.post("/estudiantes/", json={
        "usuario_id": nuevo["id"], "padron": 150001,
        "carrera": "Sistemas", "anio_ingreso": 2024,
    })
    assert resp.status_code == 201

    # 3) Y también perfil profesor
    resp = client.post("/profesores/", json={
        "usuario_id": nuevo["id"], "legajo": 560001,
        "titulo": "Lic. Sistemas", "departamento": "Inf",
        "fecha_ingreso": "2018-03-01",
    })
    assert resp.status_code == 201

    # 4) Loguea el usuario con multi-perfil
    login_como(client, nuevo, ["docente", "alumno"])

    # 5) Ve sus dos perfiles dinámicos
    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 200
    assert set(resp.get_json()["perfiles"]) == {"docente", "alumno"}

    # 6) Accede a /estudiantes/me
    resp = client.get("/estudiantes/me")
    assert resp.status_code == 200
    assert resp.get_json()["padron"] == 150001

    # 7) Accede a /profesores/me
    resp = client.get("/profesores/me")
    assert resp.status_code == 200
    assert resp.get_json()["legajo"] == 560001

    # 8) NO puede crear otros perfiles (no es admin)
    otro = crear_usuario_db(email="x@test.com", dni=22000099)
    resp = client.post("/estudiantes/", json={
        "usuario_id": otro["id"], "padron": 999,
        "carrera": "X", "anio_ingreso": 2024,
    })
    assert resp.status_code == 403
