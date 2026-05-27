# API Documentation - SIU2 Backend

## Autenticación

Todas las rutas requieren autenticación mediante JWT en cookie:

```text
access_token_cookie
```

---

# Evaluaciones

## Obtener evaluaciones

```http
GET /evaluaciones
```

### Roles permitidos

- profesor
- ayudante

### Query Params

| Parámetro | Tipo | Descripción |
|---|---|---|
| curso_id | int | Filtrar por curso |
| tipo_evaluacion_id | int | Filtrar por tipo |
| titulo | string | Filtrar por título |
| activo | bool | Filtrar activas/inactivas |

### Ejemplo

```http
GET /evaluaciones?curso_id=1&activo=true
```

### Response 200

```json
{
  "evaluaciones": [
    {
      "id": 1,
      "curso_id": 1,
      "tipo_evaluacion_id": 2,
      "tipo_evaluacion": "TP",
      "titulo": "TP1",
      "descripcion": "Trabajo práctico",
      "fecha": "2026-06-01",
      "es_grupal": true,
      "activo": true
    }
  ],
  "total": 1
}
```

---

## Obtener evaluación por ID

```http
GET /evaluaciones/<id>
```

### Roles permitidos

- profesor
- ayudante

### Response 200

```json
{
  "id": 1,
  "curso_id": 1,
  "tipo_evaluacion_id": 2,
  "tipo_evaluacion": "TP",
  "titulo": "TP1",
  "descripcion": "Trabajo práctico",
  "fecha": "2026-06-01",
  "es_grupal": true,
  "activo": true
}
```

---

## Crear evaluación

```http
POST /evaluaciones
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "curso_id": 1,
  "tipo_evaluacion_id": 2,
  "titulo": "TP1",
  "descripcion": "Trabajo práctico integrador",
  "fecha": "2026-06-01"
}
```

### Response 201

```json
{
  "message": "Evaluación creada exitosamente",
  "evaluacion": {
    "id": 1
  }
}
```

---

## Reemplazar evaluación

```http
PUT /evaluaciones/<id>
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "curso_id": 1,
  "tipo_evaluacion_id": 2,
  "titulo": "TP1 actualizado",
  "descripcion": "Nueva descripción",
  "fecha": "2026-06-15",
  "activo": true
}
```

### Response

```http
204 No Content
```

---

## Eliminar evaluación (soft delete)

```http
DELETE /evaluaciones/<id>
```

### Roles permitidos

- profesor

### Response

```http
204 No Content
```

---

# Equipos

## Obtener equipos

```http
GET /equipos
```

### Roles permitidos

- profesor
- ayudante

### Query Params

| Parámetro | Tipo |
|---|---|
| evaluacion_id | int |
| nombre | string |
| activo | bool |

### Ejemplo

```http
GET /equipos?evaluacion_id=1
```

### Response 200

```json
{
  "equipos": [
    {
      "id": 1,
      "evaluacion_id": 1,
      "nombre": "Equipo 1",
      "activo": true
    }
  ],
  "total": 1
}
```

---

## Obtener equipo por ID

```http
GET /equipos/<id>
```

### Roles permitidos

- profesor
- ayudante

### Response 200

```json
{
  "id": 1,
  "evaluacion_id": 1,
  "nombre": "Equipo 1",
  "activo": true
}
```

---

## Crear equipo

```http
POST /equipos
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "evaluacion_id": 1,
  "nombre": "Equipo 1"
}
```

### Response 201

```json
{
  "message": "Equipo creado exitosamente",
  "equipo": {
    "id": 1
  }
}
```

---

## Reemplazar equipo

```http
PUT /equipos/<id>
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "nombre": "Equipo Backend",
  "activo": true
}
```

### Response

```http
204 No Content
```

---

## Eliminar equipo (soft delete)

```http
DELETE /equipos/<id>
```

### Roles permitidos

- profesor

### Response

```http
204 No Content
```

---

# Integrantes de Equipo

## Obtener integrantes

```http
GET /equipo-integrantes
```

### Roles permitidos

- profesor
- ayudante

### Query Params

| Parámetro | Tipo |
|---|---|
| equipo_id | int |
| alumno_id | int |

### Ejemplo

```http
GET /equipo-integrantes?equipo_id=1
```

### Response 200

```json
{
  "integrantes": [
    {
      "equipo_id": 1,
      "alumno_id": 3,
      "nombre": "Juan",
      "apellido": "Perez",
      "email": "juan@fiuba.edu.ar"
    }
  ],
  "total": 1
}
```

---

## Agregar integrante

```http
POST /equipo-integrantes
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "equipo_id": 1,
  "alumno_id": 3
}
```

### Response 201

```json
{
  "message": "Integrante agregado exitosamente",
  "integrante": {
    "equipo_id": 1,
    "alumno_id": 3
  }
}
```

---

## Eliminar integrante

```http
DELETE /equipo-integrantes/<equipo_id>/<alumno_id>
```

### Roles permitidos

- profesor
- ayudante

### Response

```http
204 No Content
```

---

# Notas

## Obtener notas

```http
GET /notas
```

### Roles permitidos

- profesor
- ayudante

### Query Params

| Parámetro | Tipo |
|---|---|
| evaluacion_id | int |
| alumno_id | int |
| equipo_id | int |

### Ejemplo

```http
GET /notas?evaluacion_id=1
```

### Response 200

```json
{
  "notas": [
    {
      "id": 1,
      "evaluacion_id": 1,
      "equipo_id": 1,
      "nota": 8
    }
  ],
  "total": 1
}
```

---

## Obtener nota por ID

```http
GET /notas/<id>
```

### Roles permitidos

- profesor
- ayudante

### Response 200

```json
{
  "id": 1,
  "evaluacion_id": 1,
  "equipo_id": 1,
  "nota": 8
}
```

---

## Crear nota

```http
POST /notas
```

### Roles permitidos

- profesor
- ayudante

---

## Nota individual

### Body

```json
{
  "evaluacion_id": 2,
  "alumno_id": 3,
  "nota": 7
}
```

---

## Nota grupal

### Body

```json
{
  "evaluacion_id": 1,
  "equipo_id": 1,
  "nota": 9
}
```

### Response 201

```json
{
  "message": "Nota creada exitosamente",
  "nota": {
    "id": 1
  }
}
```

---

## Reemplazar nota

```http
PATCH /notas/<id>
```

### Roles permitidos

- profesor
- ayudante

### Body

```json
{
  "nota": 10
}
```

### Response

```http
204 No Content
```

---

## Eliminar nota

```http
DELETE /notas/<id>
```

### Roles permitidos

- profesor

### Response

```http
204 No Content
```

---

# Soft Delete

Las entidades:

- usuarios
- evaluaciones
- equipos

utilizan soft delete mediante el campo:

```text
activo
```

Las entidades:

- notas
- integrantes

utilizan delete físico.

---