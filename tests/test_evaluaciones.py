"""Tests E2E de los endpoints de /evaluaciones.

Cubre el CRUD básico. /evaluaciones es accesible sólo por DOCENTE y
AYUDANTE (ni admin ni alumno entran al GET/POST/PUT). El DELETE es
sólo DOCENTE y es soft (activo=false).
"""

from tests._factories import (
    crear_usuario,
    crear_profesor,
    crear_curso,
    crear_tipo_evaluacion,
    crear_evaluacion,
)
from tests.conftest import login_como


# ─── Fixture local: docente + curso + tipo, ya listos ────────────────────

def _setup_para_evaluacion(client):
    """Crea un docente logueado, un curso y un tipo de evaluación.

    Esto reduce ruido en cada test: muchos endpoints de
    /evaluaciones requieren todo ese andamiaje sólo para llegar al
    caso bajo prueba."""
    user = crear_usuario(email="doc@test.com", dni=70000001)
    crear_profesor(user["id"])
    login_como(client, user, ["docente"])
    curso = crear_curso()
    tipo = crear_tipo_evaluacion(nombre="Parcial")
    return user, curso, tipo


# ─── GET /evaluaciones ───────────────────────────────────────────────────

def test_listar_evaluaciones_vacio_da_204(client):
    _setup_para_evaluacion(client)
    resp = client.get("/evaluaciones/")
    assert resp.status_code == 204


def test_listar_evaluaciones_devuelve_todas(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"], titulo="E1")
    crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"], titulo="E2")
    resp = client.get("/evaluaciones/")
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 2


def test_listar_evaluaciones_filtra_por_curso(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    otro_curso = crear_curso()
    crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"], titulo="A")
    crear_evaluacion(curso_id=otro_curso["id"], tipo_evaluacion_id=tipo["id"], titulo="B")
    resp = client.get(f"/evaluaciones/?curso_id={curso['id']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["evaluaciones"][0]["titulo"] == "A"


def test_admin_no_puede_listar_evaluaciones(client, admin):
    """El endpoint pide DOCENTE o AYUDANTE, admin no entra."""
    resp = client.get("/evaluaciones/")
    assert resp.status_code == 403


def test_alumno_no_puede_listar_evaluaciones(client, alumno_logueado):
    resp = client.get("/evaluaciones/")
    assert resp.status_code == 403


# ─── POST /evaluaciones ──────────────────────────────────────────────────

def test_crear_evaluacion_como_docente(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    resp = client.post("/evaluaciones/", json={
        "curso_id": curso["id"],
        "tipo_evaluacion_id": tipo["id"],
        "titulo": "Primer Parcial",
        "fecha": "2024-06-15",
        "descripcion": "Unidades 1-3",
    })
    assert resp.status_code == 201
    assert resp.get_json()["evaluacion"]["titulo"] == "Primer Parcial"


def test_crear_evaluacion_falta_titulo(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    resp = client.post("/evaluaciones/", json={
        "curso_id": curso["id"],
        "tipo_evaluacion_id": tipo["id"],
        "fecha": "2024-06-15",
    })
    assert resp.status_code == 400


def test_crear_evaluacion_falta_fecha(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    resp = client.post("/evaluaciones/", json={
        "curso_id": curso["id"],
        "tipo_evaluacion_id": tipo["id"],
        "titulo": "X",
    })
    assert resp.status_code == 400


# ─── GET /evaluaciones/<id> ──────────────────────────────────────────────

def test_get_evaluacion_por_id(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    ev = crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"], titulo="GET")
    resp = client.get(f"/evaluaciones/{ev['id']}")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["titulo"] == "GET"
    # El service hace JOIN con tipos_evaluacion: debe traer `es_grupal`.
    assert "es_grupal" in body


def test_get_evaluacion_inexistente_404(client):
    _setup_para_evaluacion(client)
    resp = client.get("/evaluaciones/9999")
    assert resp.status_code == 404


def test_get_evaluacion_id_invalido(client):
    _setup_para_evaluacion(client)
    resp = client.get("/evaluaciones/abc")
    assert resp.status_code == 400


# ─── PUT /evaluaciones/<id> ──────────────────────────────────────────────

def test_put_evaluacion_actualiza(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    ev = crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"], titulo="Viejo")
    resp = client.put(f"/evaluaciones/{ev['id']}", json={
        "curso_id": curso["id"],
        "tipo_evaluacion_id": tipo["id"],
        "titulo": "Nuevo",
        "fecha": "2024-07-01",
        "activo": True,
    })
    assert resp.status_code == 204
    resp_get = client.get(f"/evaluaciones/{ev['id']}")
    assert resp_get.get_json()["titulo"] == "Nuevo"


def test_put_evaluacion_falta_activo(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    ev = crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"])
    resp = client.put(f"/evaluaciones/{ev['id']}", json={
        "curso_id": curso["id"],
        "tipo_evaluacion_id": tipo["id"],
        "titulo": "X",
        "fecha": "2024-07-01",
    })
    assert resp.status_code == 400


# ─── DELETE /evaluaciones/<id> ───────────────────────────────────────────

def test_delete_evaluacion_es_soft(client):
    _, curso, tipo = _setup_para_evaluacion(client)
    ev = crear_evaluacion(curso_id=curso["id"], tipo_evaluacion_id=tipo["id"])
    resp = client.delete(f"/evaluaciones/{ev['id']}")
    assert resp.status_code == 204
    # El soft delete deja la fila con activo=0; sigue visible vía GET.
    resp_get = client.get(f"/evaluaciones/{ev['id']}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["activo"] == 0


def test_delete_evaluacion_inexistente_404(client):
    _setup_para_evaluacion(client)
    resp = client.delete("/evaluaciones/9999")
    assert resp.status_code == 404


# ─── Sin token: 401 ──────────────────────────────────────────────────────

def test_evaluaciones_sin_token_da_401(client):
    resp = client.get("/evaluaciones/")
    assert resp.status_code == 401
