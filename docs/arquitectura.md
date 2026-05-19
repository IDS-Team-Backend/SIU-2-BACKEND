#  Guia para funcionamiento de la API 


##  1. Arquitectura en Capas (Router - Service - Repository)

En el TP se pide la separacion de responsabilidades. **Cada capa hace una sola cosa y no se mete en el trabajo de la otra.**

###  Routers (Controladores)
* **Qué hace:** Es la puerta de entrada. Recibe la petición HTTP, extrae los parámetros (ej. `request.args.get()`), le pasa todos los datos a la siguiente capa `Service` y devuelve la respuesta final con su respectivo código HTTP (200, 400, 500).
* **Reglas:**  **NO** lleva lógica de negocio _(no valida ni hace nada con los datos)_, ni sentencias SQL.
* **Formato de respuesta:** Los routers reciben los 'datos crudos' y debe devolver diccionarios (ej. `["resultados": {...}]`) con su debido codigo HTTP

### Services (Lógica de la API)
* **Qué hace:** Contiene toda la logica. Valida que los datos tengan sentido (ej. que fechas no sean imposibles, que el límite no sea negativo). Si algo está mal, levanta un error (ej. `raise ValidationError o NotFoundError`). Si todo está bien, pasa los datos a la siguiente capa, el `Repository`.
* **Reglas:**  **NO** sabe nada de HTTP (no usa `request`, ni `jsonify`, ni códigos de estado) y **NO** tiene SQL.

### Repositories (Capa de persistencia)
* **Qué hace:** Es la capa de *persistencia*, osea que es la unica capa que habla con la base de datos. Recibe parámetros validados del Service, arma la query y devuelve los datos crudos.
* **Reglas:**  **Solo** se encarga de hacer las querys

---

##  3. Funciones Generales y Utilidades

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
* **NotFoundError:** Devuelve status 404 (`NOT_FOUND`)
* **Exception:** Devuelve status 500 (`INTERNAL_ERROR`). Este no hace falta hacer un raise, ya que cubre cualquier error posible 

---

## 6. Buenas Practicas para Git 

Para poder entender el historial entre todos, podemos seguir estas recomendaciones:

### Commits Atómicos (Un cambio = Un commit)
No hacer un unico commit gigante con todo lo que hiciste 
* **Mal:** Un solo commit llamado "Proyecto terminado" con 15 archivos modificados.
* **Bien:** Varios commits pequeños como "crear tabla usuarios", "validar fechas en service", "ajustar diseño de links".

*Hacer commits frecuentes facilita encontrar errores y permite volver atrás en un cambio específico sin perder el resto del trabajo.*

###  Formato de Mensajes (Conventional Commits)
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
