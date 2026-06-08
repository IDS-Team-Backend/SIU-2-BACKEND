# Errores genéricos de validación
ERROR_CODE_INVALID_BODY      = "invalid.body"
ERROR_CODE_INVALID_TYPE      = "invalid.type"
ERROR_CODE_INVALID_MIN_VALUE = "invalid.min.value"
ERROR_CODE_INVALID_MAX_VALUE = "invalid.max.value"
ERROR_CODE_INVALID_EMAIL     = "invalid.email"

# ── Roles de usuario ──────────────────────────────────────────────────────────
ADMIN    = "admin"
DOCENTE  = "docente"
ALUMNO   = "alumno"
AYUDANTE = "ayudante"

# ── Dominio de clases ─────────────────────────────────────────────────────────
# ATENCIÓN: cualquier cambio aquí debe reflejarse en schema.sql también.

ESTADOS_CLASE = [   # índice 0 = default
    "pendiente",
    "suspendida",
    "en curso",
    "finalizada",
]

TIPOS_CLASE = [     # para el cronograma
    "teorica",
    "practica",
]

MODALIDADES_CLASE = [
    "Virtual",
    "Presencial",
]

# ── Dominio de entregas ───────────────────────────────────────────────────────
# ATENCIÓN: cualquier cambio aquí debe reflejarse en schema.sql también.

ESTADOS_ENTREGA = [   # índice 0 = default
    "entregado",
    "tarde",
    "rehacer",
]
