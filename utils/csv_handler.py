from utils.error_handlers import ValidationError


def leer_csv(archivo_file, columnas_requeridas=None):
    """Lee un CSV subido (FileStorage de Flask) y devuelve una lista de dicts,
    una por fila, con las columnas del encabezado como claves.

    Si se pasa `columnas_requeridas`, valida que estén todas presentes.
    Lanza ValidationError ante archivo vacío o columnas faltantes.

    OJO: separa por coma sin desescapar. Asume que los valores no traen comas.
    """
    if not archivo_file:
        raise ValidationError("No se proporcionó ningún archivo")

    # utf-8-sig descarta el BOM que mete Excel al exportar
    contenido = archivo_file.read().decode("utf-8-sig")
    lineas = contenido.splitlines()
    if not lineas:
        return []

    columnas = lineas[0].split(",")

    if columnas_requeridas:
        faltantes = set(columnas_requeridas) - set(columnas)
        if faltantes:
            cols = "', '".join(sorted(faltantes))
            raise ValidationError(
                f"El archivo debe contener las columnas '{cols}'"
            )

    filas = []
    for linea in lineas[1:]:
        if not linea.strip():
            continue
        valores = linea.split(",")
        fila = {
            col: valores[i] if i < len(valores) else ""
            for i, col in enumerate(columnas)
        }
        filas.append(fila)

    return filas


def generar_csv(filas, columnas, encabezados=None):
    """Genera un CSV en memoria a partir de una lista de dicts y devuelve bytes
    listos para io.BytesIO + send_file (igual que el pdf_generator).

    `columnas` define qué claves se exportan y en qué orden. Las claves que no
    estén en una fila salen vacías.
    `encabezados` (opcional) reemplaza los títulos de la primera fila; si no se
    pasa, se usan los nombres de `columnas`.

    OJO: concatena directo, sin escapar. Asume que los valores no traen comas
    ni saltos de línea.
    """
    titulos = encabezados if encabezados else columnas

    lineas = [",".join(str(t) for t in titulos)]
    for fila in filas:
        lineas.append(",".join(str(fila.get(c, "")) for c in columnas))

    texto = "\n".join(lineas)

    # BOM utf-8-sig para que Excel abra bien los acentos
    return texto.encode("utf-8-sig")
