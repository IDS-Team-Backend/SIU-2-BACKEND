"""Tests E2E de los endpoints de autenticación.

Cubre POST /auth/signup, POST /auth/login y GET /auth/me/perfiles.

Recordá: en el conftest parcheamos ``validar_token`` para que NO
exija cookie en /auth/signup ni /auth/login (sin ese parche, el
``app.before_request`` global devuelve 401 antes de llegar al
handler). Los tests asumen ese parche.
"""

from tests._factories import crear_usuario, crear_estudiante, crear_profesor
from tests.conftest import login_como


# ─── POST /auth/signup ───────────────────────────────────────────────────

def test_signup_crea_usuario_y_setea_cookie(client):
    resp = client.post("/auth/signup", json={
        "nombre": "Tomás",
        "apellido": "Vargas",
        "email": "tomas.vargas@gmail.com",
        "dni": 40123456,
        "password": "secreto123",
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["usuario"]["email"] == "tomas.vargas@gmail.com"
    # La cookie de sesión tiene que venir en la respuesta.
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "access_token_cookie" in set_cookie


def test_signup_dominio_email_no_permitido(client):
    resp = client.post("/auth/signup", json={
        "nombre": "X", "apellido": "Y",
        "email": "x@yahoo.com",   # yahoo.com no está en DOMINIOS_EMAIL_PERMITIDOS
        "dni": 40123457, "password": "secreto123",
    })
    assert resp.status_code == 400


def test_signup_dni_invalido(client):
    resp = client.post("/auth/signup", json={
        "nombre": "X", "apellido": "Y",
        "email": "x@gmail.com",
        "dni": 123,   # menos de 8 dígitos
        "password": "secreto123",
    })
    assert resp.status_code == 400


def test_signup_password_corta(client):
    resp = client.post("/auth/signup", json={
        "nombre": "X", "apellido": "Y",
        "email": "x@gmail.com",
        "dni": 40123458,
        "password": "abc",   # menos de 6
    })
    assert resp.status_code == 400


def test_signup_dni_duplicado(client):
    crear_usuario(email="a@gmail.com", dni=40123459)
    resp = client.post("/auth/signup", json={
        "nombre": "X", "apellido": "Y",
        "email": "otro@gmail.com",
        "dni": 40123459,
        "password": "secreto123",
    })
    assert resp.status_code == 400  # auth_service usa ValidationError, no DuplicateError


def test_signup_email_duplicado(client):
    crear_usuario(email="ocupado@gmail.com", dni=40123460)
    resp = client.post("/auth/signup", json={
        "nombre": "X", "apellido": "Y",
        "email": "ocupado@gmail.com",
        "dni": 40123461,
        "password": "secreto123",
    })
    assert resp.status_code == 400


# ─── POST /auth/login ────────────────────────────────────────────────────

def test_login_ok_setea_cookie(client):
    crear_usuario(email="login@gmail.com", dni=41000001, password="miclave123")
    resp = client.post("/auth/login", json={
        "dni": 41000001,
        "password": "miclave123",
    })
    assert resp.status_code == 200
    assert resp.get_json()["mensaje"] == "Sesión iniciada correctamente"
    assert "access_token_cookie" in resp.headers.get("Set-Cookie", "")


def test_login_password_incorrecto(client):
    crear_usuario(email="login2@gmail.com", dni=41000002, password="correcta123")
    resp = client.post("/auth/login", json={
        "dni": 41000002,
        "password": "equivocada",
    })
    assert resp.status_code == 400


def test_login_dni_inexistente(client):
    resp = client.post("/auth/login", json={
        "dni": 99999999,
        "password": "loquesea",
    })
    assert resp.status_code == 404


def test_login_dni_no_entero(client):
    resp = client.post("/auth/login", json={
        "dni": "no-soy-numero",
        "password": "x",
    })
    assert resp.status_code == 400


# ─── GET /auth/me/perfiles ───────────────────────────────────────────────
#
# La cobertura más profunda de este endpoint está en
# ``test_perfiles_dinamicos.py``. Acá sólo el caso happy path y el 401.

def test_me_perfiles_devuelve_lista_de_perfiles(client):
    user = crear_usuario(email="me@gmail.com", dni=42000001, es_admin=True)
    crear_estudiante(user["id"])
    crear_profesor(user["id"])
    login_como(client, user, ["admin", "docente", "alumno"])

    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 200
    assert set(resp.get_json()["perfiles"]) == {"admin", "docente", "alumno"}


def test_me_perfiles_sin_cookie_da_401(client):
    resp = client.get("/auth/me/perfiles")
    assert resp.status_code == 401
