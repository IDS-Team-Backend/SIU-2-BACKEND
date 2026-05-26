"""Tests E2E de los endpoints de /cursos.

Cubre CRUD, filtros, y la regla de que un curso queda definido por la
tupla (materia_id, nombre, anio, cuatrimestre): no puede haber dos
cursos con esos mismos cuatro campos.
"""

from tests._factories import crear_materia, crear_curso


# ─── GET /cursos ─────────────────────────────────────────────────────────

def test_listar_cursos_vacio_da_204(client, admin):
    resp = client.get("/cursos/")
    assert resp.status_code == 204


def test_listar_cursos_devuelve_todos(client, admin):
    materia = crear_materia()
    crear_curso(materia_id=materia["id"], nombre="C1")
    crear_curso(materia_id=materia["id"], nombre="C2")
    resp = client.get("/cursos/")
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 2


def test_listar_cursos_filtra_por_materia(client, admin):
    m1 = crear_materia()
    m2 = crear_materia()
    crear_curso(materia_id=m1["id"], nombre="C-M1")
    crear_curso(materia_id=m2["id"], nombre="C-M2")
    resp = client.get(f"/cursos/?materia_id={m1['id']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["cursos"][0]["nombre"] == "C-M1"


def test_listar_cursos_filtra_por_anio_y_cuatrimestre(client, admin):
    materia = crear_materia()
    crear_curso(materia_id=materia["id"], nombre="2023-1", anio=2023, cuatrimestre=1)
    crear_curso(materia_id=materia["id"], nombre="2024-2", anio=2024, cuatrimestre=2)
    resp = client.get("/cursos/?anio=2024&cuatrimestre=2")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["cursos"][0]["nombre"] == "2024-2"


# ─── POST /cursos ────────────────────────────────────────────────────────

def test_admin_crea_curso(client, admin):
    materia = crear_materia()
    resp = client.post("/cursos/", json={
        "materia_id": materia["id"], "nombre": "Curso X",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 201
    assert resp.get_json()["curso"]["nombre"] == "Curso X"


def test_no_admin_no_puede_crear_curso(client, alumno_logueado):
    materia = crear_materia()
    resp = client.post("/cursos/", json={
        "materia_id": materia["id"], "nombre": "X",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 403


def test_crear_curso_materia_inexistente(client, admin):
    resp = client.post("/cursos/", json={
        "materia_id": 9999, "nombre": "X",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 404


def test_crear_curso_falta_campo(client, admin):
    resp = client.post("/cursos/", json={"nombre": "X"})
    assert resp.status_code == 400


def test_crear_curso_cuatrimestre_invalido(client, admin):
    materia = crear_materia()
    resp = client.post("/cursos/", json={
        "materia_id": materia["id"], "nombre": "X",
        "anio": 2024, "cuatrimestre": 3,  # solo 1 o 2
    })
    assert resp.status_code == 400


def test_crear_curso_anio_anterior_a_2000(client, admin):
    materia = crear_materia()
    resp = client.post("/cursos/", json={
        "materia_id": materia["id"], "nombre": "X",
        "anio": 1999, "cuatrimestre": 1,
    })
    assert resp.status_code == 400


def test_crear_curso_duplicado(client, admin):
    materia = crear_materia()
    crear_curso(materia_id=materia["id"], nombre="Único", anio=2024, cuatrimestre=1)
    resp = client.post("/cursos/", json={
        "materia_id": materia["id"], "nombre": "Único",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 409


# ─── GET /cursos/<id> ────────────────────────────────────────────────────

def test_get_curso_por_id(client, admin):
    curso = crear_curso(nombre="Test")
    resp = client.get(f"/cursos/{curso['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["nombre"] == "Test"


def test_get_curso_no_encontrado(client, admin):
    resp = client.get("/cursos/9999")
    assert resp.status_code == 404


def test_get_curso_id_invalido(client, admin):
    resp = client.get("/cursos/abc")
    assert resp.status_code == 400


# ─── PUT /cursos/<id> ────────────────────────────────────────────────────

def test_put_curso_como_admin(client, admin):
    curso = crear_curso(nombre="Viejo")
    resp = client.put(f"/cursos/{curso['id']}", json={
        "materia_id": curso["materia_id"], "nombre": "Nuevo",
        "anio": 2024, "cuatrimestre": 2,
    })
    assert resp.status_code == 200
    assert resp.get_json()["curso"]["nombre"] == "Nuevo"


def test_put_curso_no_admin_403(client, alumno_logueado):
    curso = crear_curso()
    resp = client.put(f"/cursos/{curso['id']}", json={
        "materia_id": curso["materia_id"], "nombre": "X",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 403


def test_put_curso_inexistente_404(client, admin):
    materia = crear_materia()
    resp = client.put("/cursos/9999", json={
        "materia_id": materia["id"], "nombre": "X",
        "anio": 2024, "cuatrimestre": 1,
    })
    assert resp.status_code == 404


# ─── DELETE /cursos/<id> ─────────────────────────────────────────────────

def test_delete_curso_como_admin(client, admin):
    curso = crear_curso()
    resp = client.delete(f"/cursos/{curso['id']}")
    assert resp.status_code == 204
    resp_get = client.get(f"/cursos/{curso['id']}")
    assert resp_get.status_code == 404


def test_delete_curso_no_admin_403(client, alumno_logueado):
    curso = crear_curso()
    resp = client.delete(f"/cursos/{curso['id']}")
    assert resp.status_code == 403


def test_delete_curso_inexistente_404(client, admin):
    resp = client.delete("/cursos/9999")
    assert resp.status_code == 404
