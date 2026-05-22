from flask import request

import db
from utils.error_handlers import ValidationError


PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_MAX = 100


def desde_request():
    page = request.args.get("page", default=1, type=int)
    page_size = request.args.get("page_size", default=PAGE_SIZE_DEFAULT, type=int)

    if page is None or page < 1:
        raise ValidationError("'page' debe ser un entero >= 1.")
    if page_size is None or page_size < 1 or page_size > PAGE_SIZE_MAX:
        raise ValidationError(
            f"'page_size' debe ser un entero entre 1 y {PAGE_SIZE_MAX}."
        )

    offset = (page - 1) * page_size
    return page, page_size, offset


def ejecutar(query, params, order_by, page_size, offset):
    """Ejecuta una query paginada en una sola ida a la DB.

    query: SELECT base, sin ORDER BY, sin LIMIT/OFFSET.
    params: tupla/lista de parámetros del WHERE del query base.
    order_by: cláusula de orden (ej. 'e.id ASC'). Se concatena como string,
              así que debe venir hardcodeada por el repo — nunca user input.
    """
    sql = f"""
        SELECT base.*, COUNT(*) OVER() AS _total
        FROM ({query}) AS base
        ORDER BY {order_by}
        LIMIT %s OFFSET %s
    """
    filas = db.execute_query(sql, tuple(params) + (page_size, offset))
    if not filas:
        return [], 0

    total = filas[0]["_total"]
    for f in filas:
        f.pop("_total", None)
    return filas, total
