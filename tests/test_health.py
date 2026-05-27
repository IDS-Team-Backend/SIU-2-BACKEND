"""Tests de los endpoints /health.

Hoy varios blueprints (equipos, asistencia, materiales, logs,
reportes, email) sólo exponen ``GET /<recurso>/health`` y todavía no
tienen lógica de negocio. Acá verificamos que responden 200 y que
``app.before_request(validar_token)`` se les aplica.
"""

import pytest


RECURSOS = ("equipos", "asistencia", "materiales", "logs", "reportes", "email")


@pytest.mark.parametrize("recurso", RECURSOS)
def test_health_devuelve_200_con_token(client, admin, recurso):
    resp = client.get(f"/{recurso}/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["resource"] == recurso


@pytest.mark.parametrize("recurso", RECURSOS)
def test_health_sin_token_da_401(client, recurso):
    """El ``before_request`` global aplica a todos los blueprints."""
    resp = client.get(f"/{recurso}/health")
    assert resp.status_code == 401
