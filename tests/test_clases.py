"""Tests E2E de los endpoints de /clases.

El módulo de clases es el más complejo del backend, así que el archivo
es largo. Cubre:

- CRUD básico (GET listar, GET por id, POST, PUT, PATCH, DELETE).
- Soft delete vía ``deleted_at`` (no ``activo``).
- Estados de la clase y endpoint GET /clases/estados.
- Reglas de permisos por rol: un docente sólo puede crear clases
  asignándose a sí mismo y sólo puede modificar/eliminar sus propias
  clases; el admin puede todo.
- Validación de fechas (no en el pasado, no entre días distintos, fin
  posterior al inicio).
- Detección de clases superpuestas para un mismo profesor.

Las fechas se generan dinámicamente (siempre en el futuro) porque el
validator del backend rechaza fechas en el pasado: hardcodear "2024..."
haría que los tests fallen con el correr del tiempo.
"""

from datetime import datetime, timedelta

from tests._factories import (
    crear_usuario,
    crear_profesor,
    crear_curso,
    crear_clase,
)
from tests.conftest import login_como


def _fechas_futuras(dias_adelante=2, hora_inicio=10, hora_fin=12):
    """Tupla (inicio, fin) en formato ISO para un día futuro."""
    dia = datetime.now().date() + timedelta(days=dias_adelante)
    base = datetime.combine(dia, datetime.min.time())
    inicio = base.replace(hour=hora_inicio).strftime("%Y-%m-%d %H:%M:%S")
    fin = base.replace(hour=hora_fin).strftime("%Y-%m-%d %H:%M:%S")
    return inicio, fin


# ─── GET /clases/estados ─────────────────────────────────────────────────

def test_get_estados_clase(client, admin):
    resp = client.get("/clases/estados")
    assert resp.status_code == 200
    nombres = {e["nombre"] for e in resp.get_json()["estados"]}
    assert nombres == {"pendiente", "suspendida", "en curso", "finalizada"}


# ─── GET /clases ─────────────────────────────────────────────────────────

def test_listar_clases_vacio(client, admin):
    resp = client.get("/clases/")
    assert resp.status_code == 200
    assert resp.get_json()["clases"] == []


def test_listar_clases_devuelve_no_eliminadas(client, admin):
    clase = crear_clase()
    resp = client.get("/clases/")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.get_json()["clases"]]
    assert clase["id"] in ids


def test_listar_clases_filtra_por_status(client, admin):
    c1 = crear_clase(status="pendiente")
    c2 = crear_clase(status="suspendida")
    resp = client.get("/clases/?status=pendiente")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.get_json()["clases"]]
    assert c1["id"] in ids
    assert c2["id"] not in ids


def test_listar_clases_filtro_invalido(client, admin):
    resp = client.get("/clases/?nombre=Lab")
    assert resp.status_code == 400


def test_listar_clases_activa_false_solo_admin(client, docente_logueado):
    """``activa=false`` lista las clases borradas; sólo admin puede pedirlo."""
    resp = client.get("/clases/?activa=false")
    assert resp.status_code == 400


# ─── POST /clases ────────────────────────────────────────────────────────

def test_admin_crea_clase(client, admin):
    """El admin puede asignar cualquier profesor."""
    user_doc = crear_usuario(email="doc@test.com", dni=70000010)
    prof = crear_profesor(user_doc["id"])
    curso = crear_curso()
    inicio, fin = _fechas_futuras()
    resp = client.post("/clases/", json={
        "nombre": "Clase 1",
        "profesor_id": prof["id"],
        "curso_id": curso["id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
        "tema": "Intro",
    })
    assert resp.status_code == 201
    assert resp.get_json()["clase"]["nombre"] == "Clase 1"


def test_docente_solo_puede_asignarse_a_si_mismo(client, docente_logueado):
    """Un docente NO puede asignar a otro profesor como titular."""
    otro_user = crear_usuario(email="o@test.com", dni=70000011)
    otro_prof = crear_profesor(otro_user["id"])
    curso = crear_curso()
    inicio, fin = _fechas_futuras()
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": otro_prof["id"],
        "curso_id": curso["id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 400


def test_alumno_no_puede_crear_clase(client, alumno_logueado):
    curso = crear_curso()
    inicio, fin = _fechas_futuras()
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": 1,
        "curso_id": curso["id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 403


def test_crear_clase_falta_campo(client, admin):
    resp = client.post("/clases/", json={"nombre": "X"})
    assert resp.status_code == 400


def test_crear_clase_fecha_pasada(client, admin):
    user_doc = crear_usuario(email="d2@test.com", dni=70000012)
    prof = crear_profesor(user_doc["id"])
    curso = crear_curso()
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": prof["id"],
        "curso_id": curso["id"],
        "fecha_hora_inicio": "2020-01-01 10:00:00",
        "fecha_hora_fin": "2020-01-01 12:00:00",
    })
    assert resp.status_code == 400


def test_crear_clase_fin_antes_que_inicio(client, admin):
    user_doc = crear_usuario(email="d3@test.com", dni=70000013)
    prof = crear_profesor(user_doc["id"])
    curso = crear_curso()
    inicio, fin = _fechas_futuras(hora_inicio=14, hora_fin=10)  # fin < inicio
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": prof["id"],
        "curso_id": curso["id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 400


def test_crear_clase_dias_distintos(client, admin):
    user_doc = crear_usuario(email="d4@test.com", dni=70000014)
    prof = crear_profesor(user_doc["id"])
    curso = crear_curso()
    manana = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
    pasado = (datetime.now().date() + timedelta(days=2)).strftime("%Y-%m-%d")
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": prof["id"],
        "curso_id": curso["id"],
        "fecha_hora_inicio": f"{manana} 22:00:00",
        "fecha_hora_fin": f"{pasado} 02:00:00",
    })
    assert resp.status_code == 400


def test_crear_clase_curso_inexistente(client, admin):
    user_doc = crear_usuario(email="d5@test.com", dni=70000015)
    prof = crear_profesor(user_doc["id"])
    inicio, fin = _fechas_futuras()
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": prof["id"],
        "curso_id": 9999,
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 404


def test_crear_clase_profesor_inexistente(client, admin):
    curso = crear_curso()
    inicio, fin = _fechas_futuras()
    resp = client.post("/clases/", json={
        "nombre": "X",
        "profesor_id": 9999,
        "curso_id": curso["id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 404


def test_crear_clase_superpuesta(client, admin):
    """No se pueden tener dos clases del mismo profesor pisándose."""
    user_doc = crear_usuario(email="sup@test.com", dni=70000016)
    prof = crear_profesor(user_doc["id"])
    curso = crear_curso()
    inicio, fin = _fechas_futuras(hora_inicio=10, hora_fin=12)
    # Primera clase: 10-12
    resp1 = client.post("/clases/", json={
        "nombre": "Primera",
        "profesor_id": prof["id"], "curso_id": curso["id"],
        "fecha_hora_inicio": inicio, "fecha_hora_fin": fin,
    })
    assert resp1.status_code == 201
    # Segunda: 11-13 (se superpone en 11-12)
    inicio2, fin2 = _fechas_futuras(hora_inicio=11, hora_fin=13)
    resp2 = client.post("/clases/", json={
        "nombre": "Segunda",
        "profesor_id": prof["id"], "curso_id": curso["id"],
        "fecha_hora_inicio": inicio2, "fecha_hora_fin": fin2,
    })
    assert resp2.status_code == 400


# ─── GET /clases/<id> ────────────────────────────────────────────────────

def test_get_clase_por_id(client, admin):
    clase = crear_clase()
    resp = client.get(f"/clases/{clase['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["clase"]["id"] == clase["id"]


def test_get_clase_inexistente_404(client, admin):
    resp = client.get("/clases/9999")
    assert resp.status_code == 404


# ─── PUT /clases/<id> ────────────────────────────────────────────────────

def test_put_clase_como_admin(client, admin):
    clase = crear_clase()
    inicio, fin = _fechas_futuras(dias_adelante=10, hora_inicio=14, hora_fin=16)
    resp = client.put(f"/clases/{clase['id']}", json={
        "nombre": "Renombrada",
        "profesor_id": clase["profesor_id"],
        "curso_id": clase["curso_id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 200
    assert resp.get_json()["clase"]["nombre"] == "Renombrada"


def test_docente_no_puede_modificar_clase_de_otro(client, docente_logueado):
    """El docente logueado intenta modificar una clase de otro profesor."""
    otro_user = crear_usuario(email="ot@test.com", dni=70000020)
    otro_prof = crear_profesor(otro_user["id"])
    clase = crear_clase(profesor_id=otro_prof["id"])
    inicio, fin = _fechas_futuras(dias_adelante=20)
    resp = client.put(f"/clases/{clase['id']}", json={
        "nombre": "X",
        "profesor_id": otro_prof["id"],
        "curso_id": clase["curso_id"],
        "fecha_hora_inicio": inicio,
        "fecha_hora_fin": fin,
    })
    assert resp.status_code == 400


# ─── PATCH /clases/<id> ──────────────────────────────────────────────────

def test_patch_clase_cambia_tema(client, admin):
    clase = crear_clase()
    resp = client.patch(f"/clases/{clase['id']}", json={"tema": "Tema actualizado"})
    assert resp.status_code == 200
    assert resp.get_json()["clase"]["tema"] == "Tema actualizado"


def test_patch_clase_campo_invalido(client, admin):
    clase = crear_clase()
    resp = client.patch(f"/clases/{clase['id']}", json={"deleted_at": "2024-01-01"})
    assert resp.status_code == 400


# ─── DELETE /clases/<id> ─────────────────────────────────────────────────

def test_delete_clase_es_soft_delete(client, admin):
    """El borrado marca ``deleted_at``; la fila no desaparece."""
    clase = crear_clase()
    resp = client.delete(f"/clases/{clase['id']}")
    assert resp.status_code == 204
    # Como no-admin no la encuentra (filtra deleted_at IS NULL)...
    # ...pero acá somos admin y SÍ podemos verla.
    resp_get = client.get(f"/clases/{clase['id']}")
    assert resp_get.status_code == 200
    assert resp_get.get_json()["clase"]["deleted_at"] is not None


def test_delete_clase_docente_solo_la_propia(client, docente_logueado):
    """Un docente no puede borrar una clase de otro profesor."""
    otro_user = crear_usuario(email="og@test.com", dni=70000030)
    otro_prof = crear_profesor(otro_user["id"])
    clase = crear_clase(profesor_id=otro_prof["id"])
    resp = client.delete(f"/clases/{clase['id']}")
    assert resp.status_code == 400


def test_delete_clase_finalizada_solo_admin(client, docente_logueado):
    """Las clases finalizadas no se pueden modificar/eliminar salvo admin."""
    # La clase está asignada al docente logueado para descartar el otro 403.
    clase = crear_clase(
        profesor_id=docente_logueado["profesor"]["id"],
        status="finalizada",
    )
    resp = client.delete(f"/clases/{clase['id']}")
    assert resp.status_code == 400


def test_delete_clase_inexistente_404(client, admin):
    resp = client.delete("/clases/9999")
    assert resp.status_code == 404
