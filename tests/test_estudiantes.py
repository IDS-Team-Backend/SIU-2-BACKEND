"""Tests E2E de los endpoints de /estudiantes.

Cubre el CRUD completo, los filtros del listado, /estudiantes/me, y
las reglas particulares del PATCH self-service: un alumno sólo puede
modificar su propio perfil y sólo el campo "carrera".
"""

from tests._factories import (
    crear_usuario,
    crear_estudiante,
)
from tests.conftest import login_como


# ─── GET /estudiantes ────────────────────────────────────────────────────

def test_listar_estudiantes_vacio_da_204(client, admin):
    resp = client.get("/estudiantes/")
    assert resp.status_code == 204


def test_listar_estudiantes_paginado(client, admin):
    u1 = crear_usuario(email="e1@test.com", dni=60000001)
    u2 = crear_usuario(email="e2@test.com", dni=60000002)
    crear_estudiante(u1["id"], padron=200001, carrera="Informática")
    crear_estudiante(u2["id"], padron=200002, carrera="Sistemas")

    resp = client.get("/estudiantes/")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 2
    assert len(body["estudiantes"]) == 2


def test_listar_estudiantes_filtra_por_carrera(client, admin):
    u1 = crear_usuario(email="c1@test.com", dni=60000003)
    u2 = crear_usuario(email="c2@test.com", dni=60000004)
    crear_estudiante(u1["id"], padron=200003, carrera="Informática")
    crear_estudiante(u2["id"], padron=200004, carrera="Matemática")

    resp = client.get("/estudiantes/?carrera=Inform")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["total"] == 1
    assert body["estudiantes"][0]["carrera"] == "Informática"


def test_listar_estudiantes_filtro_invalido_da_400(client, admin):
    resp = client.get("/estudiantes/?nombre=Pedro")
    assert resp.status_code == 400


# ─── POST /estudiantes ───────────────────────────────────────────────────

def test_admin_crea_estudiante(client, admin):
    usuario = crear_usuario(email="nuevo@test.com", dni=61000001)
    resp = client.post("/estudiantes/", json={
        "usuario_id": usuario["id"],
        "padron": 300001,
        "carrera": "Informática",
        "anio_ingreso": 2024,
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["estudiante"]["padron"] == 300001


def test_no_admin_no_puede_crear_estudiante(client, docente_logueado):
    otro = crear_usuario(email="x@test.com", dni=61000002)
    resp = client.post("/estudiantes/", json={
        "usuario_id": otro["id"], "padron": 300002,
        "carrera": "Inf", "anio_ingreso": 2024,
    })
    assert resp.status_code == 403


def test_crear_estudiante_usuario_inexistente(client, admin):
    resp = client.post("/estudiantes/", json={
        "usuario_id": 9999, "padron": 300003,
        "carrera": "Inf", "anio_ingreso": 2024,
    })
    assert resp.status_code == 404


def test_crear_estudiante_padron_duplicado(client, admin):
    u1 = crear_usuario(email="a@test.com", dni=61000003)
    u2 = crear_usuario(email="b@test.com", dni=61000004)
    crear_estudiante(u1["id"], padron=300010)
    resp = client.post("/estudiantes/", json={
        "usuario_id": u2["id"], "padron": 300010,
        "carrera": "Inf", "anio_ingreso": 2024,
    })
    assert resp.status_code == 409


def test_crear_segundo_perfil_estudiante_para_mismo_usuario(client, admin):
    user = crear_usuario(email="dup@test.com", dni=61000005)
    crear_estudiante(user["id"], padron=300020)
    resp = client.post("/estudiantes/", json={
        "usuario_id": user["id"], "padron": 300021,
        "carrera": "Inf", "anio_ingreso": 2024,
    })
    assert resp.status_code == 409


def test_crear_estudiante_anio_ingreso_invalido(client, admin):
    user = crear_usuario(email="anio@test.com", dni=61000006)
    resp = client.post("/estudiantes/", json={
        "usuario_id": user["id"], "padron": 300030,
        "carrera": "Inf", "anio_ingreso": 1800,  # antes de 1900
    })
    assert resp.status_code == 400


def test_crear_estudiante_body_incompleto(client, admin):
    resp = client.post("/estudiantes/", json={"padron": 1})
    assert resp.status_code == 400


# ─── GET /estudiantes/me ─────────────────────────────────────────────────

def test_me_devuelve_perfil_propio(client, alumno_logueado):
    resp = client.get("/estudiantes/me")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["usuario_id"] == alumno_logueado["usuario"]["id"]


def test_me_404_si_no_es_estudiante(client, admin):
    resp = client.get("/estudiantes/me")
    assert resp.status_code == 404


# ─── GET /estudiantes/<id> ───────────────────────────────────────────────

def test_get_estudiante_por_id_como_admin(client, admin):
    user = crear_usuario(email="g@test.com", dni=62000001)
    est = crear_estudiante(user["id"], padron=400001)
    resp = client.get(f"/estudiantes/{est['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["padron"] == 400001


def test_get_estudiante_por_id_como_docente_ok(client, docente_logueado):
    user = crear_usuario(email="g2@test.com", dni=62000002)
    est = crear_estudiante(user["id"], padron=400002)
    resp = client.get(f"/estudiantes/{est['id']}")
    assert resp.status_code == 200


def test_get_estudiante_por_id_como_alumno_403(client, alumno_logueado):
    """ADMIN o DOCENTE; un alumno no puede ver el perfil de otro."""
    user = crear_usuario(email="otr@test.com", dni=62000003)
    est = crear_estudiante(user["id"], padron=400003)
    resp = client.get(f"/estudiantes/{est['id']}")
    assert resp.status_code == 403


def test_get_estudiante_id_invalido(client, admin):
    resp = client.get("/estudiantes/abc")
    assert resp.status_code == 400


# ─── PUT /estudiantes/<id> ───────────────────────────────────────────────

def test_put_estudiante_como_admin(client, admin):
    user = crear_usuario(email="p@test.com", dni=63000001)
    est = crear_estudiante(user["id"], padron=500001)
    resp = client.put(f"/estudiantes/{est['id']}", json={
        "padron": 500099, "carrera": "Nueva", "anio_ingreso": 2023, "activo": True,
    })
    assert resp.status_code == 204


def test_put_estudiante_como_alumno_403(client, alumno_logueado):
    resp = client.put(
        f"/estudiantes/{alumno_logueado['estudiante']['id']}",
        json={"padron": 1, "carrera": "X", "anio_ingreso": 2024, "activo": True},
    )
    assert resp.status_code == 403


# ─── PATCH /estudiantes/<id> ─────────────────────────────────────────────

def test_patch_admin_puede_cambiar_padron(client, admin):
    user = crear_usuario(email="pat@test.com", dni=64000001)
    est = crear_estudiante(user["id"], padron=600001)
    resp = client.patch(f"/estudiantes/{est['id']}", json={"padron": 600099})
    assert resp.status_code == 200
    assert resp.get_json()["estudiante"]["padron"] == 600099


def test_patch_alumno_puede_cambiar_su_carrera(client, alumno_logueado):
    resp = client.patch(
        f"/estudiantes/{alumno_logueado['estudiante']['id']}",
        json={"carrera": "Nueva carrera"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["estudiante"]["carrera"] == "Nueva carrera"


def test_patch_alumno_NO_puede_cambiar_padron(client, alumno_logueado):
    """Self-service: el alumno sólo puede tocar `carrera`."""
    resp = client.patch(
        f"/estudiantes/{alumno_logueado['estudiante']['id']}",
        json={"padron": 999999},
    )
    assert resp.status_code == 403


def test_patch_alumno_no_puede_modificar_a_otro(client, alumno_logueado):
    otro_user = crear_usuario(email="o@test.com", dni=64000002)
    otro_est = crear_estudiante(otro_user["id"], padron=600010)
    resp = client.patch(f"/estudiantes/{otro_est['id']}", json={"carrera": "X"})
    assert resp.status_code == 403


def test_patch_campo_no_permitido(client, admin):
    user = crear_usuario(email="cp@test.com", dni=64000003)
    est = crear_estudiante(user["id"], padron=600020)
    resp = client.patch(f"/estudiantes/{est['id']}", json={"foo": "bar"})
    assert resp.status_code == 400


def test_patch_body_vacio(client, admin):
    user = crear_usuario(email="vac@test.com", dni=64000004)
    est = crear_estudiante(user["id"], padron=600030)
    resp = client.patch(f"/estudiantes/{est['id']}", json={})
    assert resp.status_code == 400


def test_patch_padron_duplicado(client, admin):
    u1 = crear_usuario(email="d1@test.com", dni=64000005)
    u2 = crear_usuario(email="d2@test.com", dni=64000006)
    crear_estudiante(u1["id"], padron=600040)
    e2 = crear_estudiante(u2["id"], padron=600041)
    resp = client.patch(f"/estudiantes/{e2['id']}", json={"padron": 600040})
    assert resp.status_code == 409


# ─── DELETE /estudiantes/<id> ────────────────────────────────────────────

def test_delete_estudiante_soft(client, admin):
    user = crear_usuario(email="del@test.com", dni=65000001)
    est = crear_estudiante(user["id"], padron=700001)
    resp = client.delete(f"/estudiantes/{est['id']}")
    assert resp.status_code == 204
    # Sigue existiendo pero activo=0
    resp_get = client.get(f"/estudiantes/{est['id']}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["activo"] == 0


def test_delete_estudiante_no_admin_403(client, alumno_logueado):
    resp = client.delete(f"/estudiantes/{alumno_logueado['estudiante']['id']}")
    assert resp.status_code == 403


def test_delete_estudiante_inexistente_404(client, admin):
    resp = client.delete("/estudiantes/9999")
    assert resp.status_code == 404
