"""Tests E2E de la entidad ``profesores``.

Cubre: CRUD, autorización por perfil, PATCH self-service vs admin,
validación de filtros y body. Atraviesa router → service → repository
→ db (fake SQLite del conftest).
"""

from tests.conftest import (
    crear_usuario_db,
    crear_perfil_profesor,
    crear_perfil_estudiante,
    login_como,
)


# ─── POST /profesores ──────────────────────────────────────────────

def test_admin_crea_profesor(client, admin):
    usuario = crear_usuario_db(email="nuevo@test.com", dni=44444444)
    resp = client.post("/profesores/", json={
        "usuario_id": usuario["id"],
        "legajo": 700001,
        "titulo": "Ing. Sistemas",
        "departamento": "Informática",
        "fecha_ingreso": "2020-03-01",
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["profesor"]["legajo"] == 700001
    assert body["profesor"]["usuario_id"] == usuario["id"]


def test_no_admin_no_puede_crear_profesor(client, alumno_logueado):
    otro = crear_usuario_db(email="otro@test.com", dni=44444445)
    resp = client.post("/profesores/", json={
        "usuario_id": otro["id"],
        "legajo": 700002,
        "titulo": "X", "departamento": "Y", "fecha_ingreso": "2020-03-01",
    })
    assert resp.status_code == 403


def test_crear_profesor_usuario_inexistente(client, admin):
    resp = client.post("/profesores/", json={
        "usuario_id": 9999,
        "legajo": 700003,
        "titulo": "X", "departamento": "Y", "fecha_ingreso": "2020-03-01",
    })
    assert resp.status_code == 404


def test_crear_profesor_legajo_duplicado(client, admin):
    usuario1 = crear_usuario_db(email="u1@test.com", dni=55555551)
    usuario2 = crear_usuario_db(email="u2@test.com", dni=55555552)
    crear_perfil_profesor(usuario1["id"], legajo=700004)
    resp = client.post("/profesores/", json={
        "usuario_id": usuario2["id"],
        "legajo": 700004,  # mismo legajo
        "titulo": "X", "departamento": "Y", "fecha_ingreso": "2020-03-01",
    })
    assert resp.status_code == 409


def test_crear_profesor_segundo_perfil_para_mismo_usuario(client, admin):
    usuario = crear_usuario_db(email="dup@test.com", dni=55555553)
    crear_perfil_profesor(usuario["id"], legajo=700005)
    resp = client.post("/profesores/", json={
        "usuario_id": usuario["id"],
        "legajo": 700006,
        "titulo": "X", "departamento": "Y", "fecha_ingreso": "2020-03-01",
    })
    assert resp.status_code == 409


def test_crear_profesor_fecha_futura_invalida(client, admin):
    usuario = crear_usuario_db(email="fut@test.com", dni=55555554)
    resp = client.post("/profesores/", json={
        "usuario_id": usuario["id"],
        "legajo": 700007,
        "titulo": "X", "departamento": "Y", "fecha_ingreso": "2999-01-01",
    })
    assert resp.status_code == 400


def test_crear_profesor_body_incompleto(client, admin):
    resp = client.post("/profesores/", json={"legajo": 1})
    assert resp.status_code == 400


# ─── GET /profesores ───────────────────────────────────────────────

def test_listar_profesores_paginado(client, admin):
    u1 = crear_usuario_db(email="p1@test.com", dni=66666661)
    u2 = crear_usuario_db(email="p2@test.com", dni=66666662)
    crear_perfil_profesor(u1["id"], legajo=800001, departamento="Mat")
    crear_perfil_profesor(u2["id"], legajo=800002, departamento="Inf")

    resp = client.get("/profesores/")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 2
    assert len(body["profesores"]) == 2


def test_listar_profesores_filtra_por_departamento(client, admin):
    u1 = crear_usuario_db(email="d1@test.com", dni=66666663)
    u2 = crear_usuario_db(email="d2@test.com", dni=66666664)
    crear_perfil_profesor(u1["id"], legajo=800003, departamento="Matemática")
    crear_perfil_profesor(u2["id"], legajo=800004, departamento="Informática")

    resp = client.get("/profesores/?departamento=Matem")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["profesores"][0]["departamento"] == "Matemática"


def test_listar_profesores_filtro_invalido(client, admin):
    resp = client.get("/profesores/?nombre=Juan")
    assert resp.status_code == 400


def test_listar_profesores_vacio_devuelve_204(client, admin):
    resp = client.get("/profesores/")
    assert resp.status_code == 204


# ─── GET /profesores/me ────────────────────────────────────────────

def test_me_devuelve_perfil_propio_si_es_docente(client, docente_logueado):
    resp = client.get("/profesores/me")
    assert resp.status_code == 200
    assert resp.get_json()["usuario_id"] == docente_logueado["usuario"]["id"]


def test_me_devuelve_404_si_no_es_docente(client, admin):
    resp = client.get("/profesores/me")
    assert resp.status_code == 404


# ─── GET /profesores/<id> ──────────────────────────────────────────

def test_get_profesor_por_id_como_admin(client, admin):
    user = crear_usuario_db(email="x@test.com", dni=77777771)
    prof = crear_perfil_profesor(user["id"], legajo=900001)
    resp = client.get(f"/profesores/{prof['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["legajo"] == 900001


def test_get_profesor_por_id_como_docente_ok(client, docente_logueado):
    resp = client.get(f"/profesores/{docente_logueado['profesor']['id']}")
    assert resp.status_code == 200


def test_get_profesor_por_id_como_alumno_403(client, alumno_logueado):
    user_doc = crear_usuario_db(email="prof@test.com", dni=77777772)
    prof = crear_perfil_profesor(user_doc["id"], legajo=900002)
    resp = client.get(f"/profesores/{prof['id']}")
    assert resp.status_code == 403


def test_get_profesor_id_invalido(client, admin):
    resp = client.get("/profesores/abc")
    assert resp.status_code == 400


def test_get_profesor_no_encontrado(client, admin):
    resp = client.get("/profesores/9999")
    assert resp.status_code == 404


# ─── PATCH /profesores/<id> ────────────────────────────────────────

def test_patch_admin_puede_cambiar_legajo(client, admin):
    user = crear_usuario_db(email="patch1@test.com", dni=88888881)
    prof = crear_perfil_profesor(user["id"], legajo=900010)
    resp = client.patch(f"/profesores/{prof['id']}", json={"legajo": 900099})
    assert resp.status_code == 200
    assert resp.get_json()["profesor"]["legajo"] == 900099


def test_patch_self_puede_cambiar_titulo(client, docente_logueado):
    resp = client.patch(
        f"/profesores/{docente_logueado['profesor']['id']}",
        json={"titulo": "Doctor"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["profesor"]["titulo"] == "Doctor"


def test_patch_self_NO_puede_cambiar_legajo(client, docente_logueado):
    resp = client.patch(
        f"/profesores/{docente_logueado['profesor']['id']}",
        json={"legajo": 999999},
    )
    assert resp.status_code == 403


def test_patch_de_otro_profesor_como_docente_403(client, docente_logueado):
    otro_user = crear_usuario_db(email="otro_doc@test.com", dni=88888882)
    otro_prof = crear_perfil_profesor(otro_user["id"], legajo=900011)
    resp = client.patch(f"/profesores/{otro_prof['id']}", json={"titulo": "X"})
    assert resp.status_code == 403


def test_patch_campo_invalido(client, admin):
    user = crear_usuario_db(email="patch2@test.com", dni=88888883)
    prof = crear_perfil_profesor(user["id"], legajo=900012)
    resp = client.patch(f"/profesores/{prof['id']}", json={"foo": "bar"})
    assert resp.status_code == 400


def test_patch_body_vacio(client, admin):
    user = crear_usuario_db(email="patch3@test.com", dni=88888884)
    prof = crear_perfil_profesor(user["id"], legajo=900013)
    resp = client.patch(f"/profesores/{prof['id']}", json={})
    assert resp.status_code == 400


def test_patch_legajo_duplicado(client, admin):
    u1 = crear_usuario_db(email="d1@test.com", dni=88888885)
    u2 = crear_usuario_db(email="d2@test.com", dni=88888886)
    crear_perfil_profesor(u1["id"], legajo=900020)
    prof2 = crear_perfil_profesor(u2["id"], legajo=900021)
    resp = client.patch(f"/profesores/{prof2['id']}", json={"legajo": 900020})
    assert resp.status_code == 409


# ─── DELETE /profesores/<id> ───────────────────────────────────────

def test_delete_soft_como_admin(client, admin):
    user = crear_usuario_db(email="del@test.com", dni=99999900)
    prof = crear_perfil_profesor(user["id"], legajo=910001)
    resp = client.delete(f"/profesores/{prof['id']}")
    assert resp.status_code == 204
    # Verificamos que activo pasó a False
    resp_get = client.get(f"/profesores/{prof['id']}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["activo"] == 0  # SQLite guarda BOOLEAN como 0/1


def test_delete_no_admin_403(client, docente_logueado):
    resp = client.delete(f"/profesores/{docente_logueado['profesor']['id']}")
    assert resp.status_code == 403


# ─── Sin token: 401 en todo ────────────────────────────────────────

def test_sin_token_da_401(client):
    resp = client.get("/profesores/")
    assert resp.status_code == 401


# ─── Multi-perfil: un docente que también es estudiante ────────────

def test_docente_que_tambien_es_estudiante_accede_a_profesores_me(client):
    user = crear_usuario_db(email="multi@test.com", dni=11000011)
    prof = crear_perfil_profesor(user["id"], legajo=920001)
    crear_perfil_estudiante(user["id"], padron=110001, carrera="Sistemas")
    login_como(client, user, ["docente", "alumno"])

    resp_prof = client.get("/profesores/me")
    assert resp_prof.status_code == 200
    assert resp_prof.get_json()["id"] == prof["id"]

    resp_est = client.get("/estudiantes/me")
    assert resp_est.status_code == 200
    assert resp_est.get_json()["padron"] == 110001
