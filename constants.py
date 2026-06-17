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

# Set canónico de roles del staff. Se usa para que todos los perfiles del staff
# (admin/docente y los roles de cátedra, que entran por docente) tengan los
# mismos permisos en los endpoints de gestión.
ROLES_STAFF = (ADMIN, DOCENTE, AYUDANTE)

# ── Dominio de clases ─────────────────────────────────────────────────────────
# ATENCIÓN: cualquier cambio aquí debe reflejarse en schema.sql también.

ESTADOS_CLASE = [   # índice 0 = default
    "pendiente",
    "suspendida",
    "en curso",
    "finalizada",
]

# Ciclo de vida de la cursada. El orden define las transiciones válidas
# (solo se avanza/retrocede de a un paso). Índice 0 = default.
# ATENCIÓN: reflejar cualquier cambio en el ENUM de cursos.estado en schema.sql.
ESTADOS_CURSO = [
    "abierta",
    "inscripcion_cerrada",
    "periodo_evaluativo",
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
