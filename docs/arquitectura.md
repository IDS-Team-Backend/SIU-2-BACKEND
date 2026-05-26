# Guia para funcionamiento de la API 

## 1. Arquitectura en Capas (Router - Service - Repository)

En el TP se pide la separacion de responsabilidades. **Cada capa hace una sola cosa y no se mete en el trabajo de la otra.**

### Routers (Controladores)
* **Qué hace:** Es la puerta de entrada. Recibe la petición HTTP, extrae los parámetros (ej. `request.args.get()`), le pasa todos los datos a la siguiente capa `Service` y devuelve la respuesta final con su respectivo código HTTP (200, 400, 500).
* **Reglas:** **NO** lleva lógica de negocio _(no valida ni hace nada con los datos)_, ni sentencias SQL.
* **Formato de respuesta:** Los routers reciben los 'datos crudos' y debe devolver diccionarios (ej. `{"resultados": {...}}`) con su debido codigo HTTP

### Services (Lógica de la API)
* **Qué hace:** Contiene toda la logica. Valida que los datos tengan sentido (ej. que fechas no sean imposibles, que el límite no sea negativo). Si algo está mal, levanta un error (ej. `raise ValidationError o NotFoundError`). Si todo está bien, pasa los datos a la siguiente capa, el `Repository`.
* **Reglas:** **NO** sabe nada de HTTP (no usa `request`, ni `jsonify`, ni códigos de estado) y **NO** tiene SQL.

### Repositories (Capa de persistencia)
* **Qué hace:** Es la capa de *persistencia*, osea que es la unica capa que habla con la base de datos. Recibe parámetros validados del Service, arma la query y devuelve los datos crudos.
* **Reglas:** **Solo** se encarga de hacer las querys

---

## 2. Autenticación y Control de Accesos (JWT y Roles)

Para proteger los endpoints de la API y controlar qué usuario puede hacer qué acción, implementamos un sistema basado en tokens JWT (guardados en cookies) y roles de usuario.

### 🔒 Validación General de Tokens (`before_request`)
Si querés que **toda una ruta completa** (un Blueprint) requiera que el usuario esté logueado, tenés que registrar la función `validar_token_global` al principio de tu router utilizando `before_request`.

> ⚠️ **REGLA DE ORO:** Pasá la función únicamente por su nombre, **sin paréntesis `()`**. Si ponés los paréntesis, la función se ejecutará al arrancar el servidor y romperá la aplicación por falta de contexto de petición HTTP.

### 👮 Control por Roles específicos (`@requiere_roles`)
Cuando un endpoint deba ser exclusivo para ciertos tipos de usuarios, debés agregarle nuestro decorador personalizado `@requiere_roles("nombre_rol")`.

> 🚨 **MUY IMPORTANTE (Orden de los decoradores):** En Python, los decoradores se ejecutan de abajo hacia arriba. Por lo tanto, el decorador de ruta de Flask (`@bp.route`) **SIEMPRE debe ir primero (arriba de todo)**, y tu decorador de roles debe ir inmediatamente abajo. Si los ponés al revés, Flask ignorará la validación de roles.

### 📋 Listado de Roles Disponibles
El sistema mapea internamente los IDs de la base de datos con los siguientes strings que debés usar en los decoradores:

| ID Rol | Nombre del Rol (Usar en el decorador) |
| :---: | :--- |
| **`1`** | `"admin"` |
| **`2`** | `"docente"` |
| **`3`** | `"alumno"` |
| **`4`** | `"ayudante"` |

### 📝 Ejemplo de implementación en un Router:
```python
from flask import Blueprint, jsonify, g
from utils.auth_validator import validar_token_global, requiere_roles

materias_bp = Blueprint("materias", __name__)

# 1. PROTECCIÓN GLOBAL: Aplica a todas las rutas de este archivo (SIN paréntesis)
materias_bp.before_request(validar_token_global)

# CASO A: Accesible por CUALQUIER usuario logueado (No lleva decorador extra)
@materias_bp.route("/", methods=["GET"])
def listar_materias():
    # Podés acceder a los datos del usuario logueado usando el objeto global 'g'
    id_usuario = g.usuario.get("id")
    return jsonify({"materias": ["Análisis II", "Física I"]}), 200

# CASO B: Accesible SOLO por el rol Administrador (Ojo al orden de decoradores)
@materias_bp.route("/crear", methods=["POST"])  # <- 1° El de Flask
@requiere_roles("admin")                        # <- 2° El de Roles
def crear_materia():
    return jsonify({"mensaje": "Materia creada por el Administrador."}), 201

# CASO C: Accesible por MÚLTIPLES ROLES (Se pasan separados por comas)
@materias_bp.route("/notas", methods=["PUT"])
@requiere_roles("admin", "docente") 
def cargar_notas():
    return jsonify({"mensaje": "Notas cargadas correctamente."}), 200
```

---

## 3. Funciones Generales y Utilidades

### `db.py` -> `execute_query()`
Para no repetir el código de abrir conexión, crear cursor, atrapar errores, hacer `commit()` y cerrar conexión en cada función del Repository, usamos una función centralizada: `execute_query()`.

**¿Cómo se usa?**
```python
# Argumentos obligatorios
execute_query(query, params)

# Para un SELECT común:
resultados = execute_query("SELECT * FROM tabla WHERE id = %s", (id_item,))

# Para un SELECT que devuelve una sola fila:
resultado = execute_query("SELECT COUNT(*) as total FROM tabla", un_solo_valor=True)

# Para un INSERT/UPDATE (hace commit automático y devuelve el ID insertado):
nuevo_id = execute_query("INSERT INTO tabla (nombre) VALUES (%s)", (nombre,), modifica_db=True)
```

---

## 4. Configuración de Base de Datos 

Utilizamos **MySQL** como motor de base de datos. Para vincular la API con tu server local, sigue estos pasos:

1. **Configuración de Credenciales:** Dirígete al archivo `db.py` y modifica la variable `password` (y cualquier otro parámetro como `user` o `host` si fuera necesario) con las credenciales de tu servidor local.
2. **Instalación del Motor:** Si aún no tienes MySQL, puedes descargar el instalador oficial desde [este enlace](https://dev.mysql.com/downloads/installer/).

---

## 5. Manejo de Errores

Todos los errores que pueden aparecer estan definidos en *utils/error_handlers.py*. Por eso no hace falta los try/except en los routers, ya que se manejan automaticamente. ej: `raise ValidationError("'X' campo esta mal")`<br> 
Los errores que estan definidos son:
* **ValidationError:** Devuelve status 400 (`BAD_REQUEST`)
* **UnauthorizedError:** Devuelve status 401 (`UNAUTHORIZED`). Se lanza cuando no hay token o expiró.
* **ForbiddenError:** Devuelve status 403 (`FORBIDDEN`). Se lanza cuando el token es válido pero el rol no tiene permisos.
* **NotFoundError:** Devuelve status 404 (`NOT_FOUND`)
* **Exception:** Devuelve status 500 (`INTERNAL_ERROR`). Este no hace falta hacer un raise, ya que cubre cualquier error posible 

---

## 6. Constantes globales
**VALORES GLOBALES Y CONSTANTES** se definen en `'/config.py'`. Por ejemplo la asignacion de roles, el nombre utilizado de cada uno con sus respectivos ids que definen su creacion en la base de datos.
```python
ROLES = {
    "admin": 1,
    "docente": 2,
    "alumno": 3,
    "ayudante": 4
}

DOMINIOS_EMAIL_PERMITIDOS = [  # en caso de que solo se permitan emails institucionales 
    "fiuba.edu.ar",
    "alumnos.fiuba.edu.ar"
]
```
---
## 7. Buenas Practicas para Git 

Para poder entender el historial entre todos, podemos seguir estas recomendaciones:

### Commits Atómicos (Un cambio = Un commit)
No hacer un unico commit gigante con todo lo que hiciste 
* **Mal:** Un solo commit llamado "Proyecto terminado" con 15 archivos modificados.
* **Bien:** Varios commits pequeños como "crear tabla usuarios", "validar fechas en service", "ajustar diseño de links".

*Hacer commits frecuentes facilita encontrar errores y permite volver atrás en un cambio específico sin perder el resto del trabajo.*

### Formato de Mensajes (Conventional Commits)
Usemos prefijos para identificar que tipo de cambio se hizo. <br> El formato es: `prefijo: desc corta`.

| Prefijo | Cuándo usarlo |
| :--- | :--- |
| **`feat:`** | Cuando agregas una nueva funcionalidad (ej. un nuevo endpoint). |
| **`fix:`** | Cuando corriges un error o bug. |
| **`refactor:`** | Cuando cambias el código para mejorarlo pero sin agregar ninguna funcionalidad nueva |
| **`docs:`** | Cambios solo en la documentación (README, comentarios, guías). |
| **`chore:`** | Tareas de mantenimiento (instalar librerías, actualizar el `.gitignore`, modificar `seed.py`). |
| **`test:`** | Cuando agregas o corriges pruebas unitarias. |

**Ejemplo:** `feat: agregar filtro por materia en el listado de alumnos`