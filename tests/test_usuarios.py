"""Tests E2E de los endpoints de /usuarios.

Recorre router → service → repository → SQLite stub. Cubre el CRUD,
los filtros del listado, las validaciones de body y las reglas de
autorización (sólo un admin puede crear/asignar otro admin).
"""

from tests._factories import crear_usuario, crear_admin
from tests.conftest import login_como


# ─── GET /usuarios ───────────────────────────────────────────────────────

def test_listar_usuarios_devuelve_204_si_vacio(client, admin):
    # El fixture admin crea 1 usuario; lo "ocultamos" filtrando por nombre
    # que no existe.
    resp = client.get("/usuarios/?nombre=inexistente")
    assert resp.status_code == 204


def test_listar_usuarios_devuelve_todos(client, admin):
    crear_usuario(email="u1@test.com", dni=50000001)
    crear_usuario(email="u2@test.com", dni=50000002)
    resp = client.get("/usuarios/")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 3   # admin + u1 + u2
    assert len(body["usuarios"]) == 3


def test_listar_usuarios_filtra_por_nombre(client, admin):
    crear_usuario(nombre="María", email="mar@test.com", dni=50000003)
    crear_usuario(nombre="Pedro", email="ped@test.com", dni=50000004)
    resp = client.get("/usuarios/?nombre=Mar")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["usuarios"][0]["nombre"] == "María"


def test_listar_usuarios_filtra_por_es_admin(client, admin):
    crear_usuario(email="u@test.com", dni=50000005)
    resp = client.get("/usuarios/?es_admin=true")
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 1


def test_listar_usuarios_sin_token_da_401(client):
    resp = client.get("/usuarios/")
    assert resp.status_code == 401


# ─── POST /usuarios ──────────────────────────────────────────────────────

def test_crear_usuario_como_admin(client, admin):
    resp = client.post("/usuarios/", json={
        "nombre": "Nuevo", "apellido": "User",
        "email": "nuevo@test.com",
        "dni": 51000001, "password": "secreto123",
    })
    assert resp.status_code == 201
    assert resp.get_json()["usuario"]["email"] == "nuevo@test.com"
    # Location header de REST
    assert resp.headers.get("Location", "").startswith("/usuarios/")


def test_crear_usuario_falta_campo_da_400(client, admin):
    resp = client.post("/usuarios/", json={"nombre": "X"})
    assert resp.status_code == 400


def test_crear_usuario_email_duplicado(client, admin):
    crear_usuario(email="dup@test.com", dni=51000002)
    resp = client.post("/usuarios/", json={
        "nombre": "X", "apellido": "Y",
        "email": "dup@test.com",
        "dni": 51000003, "password": "secreto123",
    })
    assert resp.status_code == 409


def test_crear_usuario_dni_duplicado(client, admin):
    crear_usuario(email="orig@test.com", dni=51000004)
    resp = client.post("/usuarios/", json={
        "nombre": "X", "apellido": "Y",
        "email": "otro@test.com",
        "dni": 51000004, "password": "secreto123",
    })
    assert resp.status_code == 409


def test_alumno_no_puede_crear_admin(client, alumno_logueado):
    """Sólo un admin puede asignar es_admin=True a otro usuario."""
    resp = client.post("/usuarios/", json={
        "nombre": "X", "apellido": "Y",
        "email": "intento@test.com",
        "dni": 51000005, "password": "secreto123",
        "es_admin": True,
    })
    assert resp.status_code == 403


def test_admin_puede_crear_otro_admin(client, admin):
    resp = client.post("/usuarios/", json={
        "nombre": "Otro", "apellido": "Admin",
        "email": "admin2@test.com",
        "dni": 51000006, "password": "secreto123",
        "es_admin": True,
    })
    assert resp.status_code == 201
    assert resp.get_json()["usuario"]["es_admin"] == 1


# ─── GET /usuarios/{id} ──────────────────────────────────────────────────

def test_get_usuario_por_id(client, admin):
    user = crear_usuario(email="get@test.com", dni=52000001)
    resp = client.get(f"/usuarios/{user['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["email"] == "get@test.com"


def test_get_usuario_no_encontrado(client, admin):
    resp = client.get("/usuarios/9999")
    assert resp.status_code == 404


def test_get_usuario_id_invalido(client, admin):
    resp = client.get("/usuarios/abc")
    assert resp.status_code == 400


# ─── PUT /usuarios/{id} ──────────────────────────────────────────────────

def test_put_usuario_reemplaza_campos(client, admin):
    user = crear_usuario(email="put@test.com", dni=53000001)
    resp = client.put(f"/usuarios/{user['id']}", json={
        "nombre": "Nuevo Nombre", "apellido": "Nuevo Apellido",
        "email": "putnew@test.com",
        "dni": 53000099, "activo": True,
    })
    assert resp.status_code == 204
    # Verificamos que efectivamente cambió
    resp_get = client.get(f"/usuarios/{user['id']}")
    assert resp_get.get_json()["email"] == "putnew@test.com"


def test_put_usuario_email_duplicado(client, admin):
    crear_usuario(email="ocupado@test.com", dni=53000002)
    a_modificar = crear_usuario(email="libre@test.com", dni=53000003)
    resp = client.put(f"/usuarios/{a_modificar['id']}", json={
        "nombre": "X", "apellido": "Y",
        "email": "ocupado@test.com",   # ya existe
        "dni": 53000003, "activo": True,
    })
    assert resp.status_code == 409


# ─── DELETE /usuarios/{id} ───────────────────────────────────────────────

def test_delete_usuario_como_admin_es_soft_delete(client, admin):
    user = crear_usuario(email="del@test.com", dni=54000001)
    resp = client.delete(f"/usuarios/{user['id']}")
    assert resp.status_code == 204
    # Soft delete: el usuario sigue existiendo pero activo=0
    resp_get = client.get(f"/usuarios/{user['id']}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["activo"] == 0


def test_delete_usuario_no_admin_da_403(client, alumno_logueado):
    otro = crear_usuario(email="otro@test.com", dni=54000002)
    resp = client.delete(f"/usuarios/{otro['id']}")
    assert resp.status_code == 403


def test_delete_usuario_inexistente_da_404(client, admin):
    resp = client.delete("/usuarios/9999")
    assert resp.status_code == 404
