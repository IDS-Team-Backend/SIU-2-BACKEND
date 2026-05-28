from fpdf import FPDF


def configurar_pdf(pdf, titulo):
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, titulo, ln=True, align="C")
    pdf.ln(8)


def header_tabla(pdf, headers, widths):
    pdf.set_fill_color(220, 220, 220)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_font("Arial", "B", 10)
    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], 1, 0, "C", True)

    pdf.ln()

def crear_pdf_alumnos(data_alumnos):
    pdf = FPDF()
    configurar_pdf(pdf, "Listado de Alumnos")
    headers = [
        "Padron",
        "Apellido y Nombre",
        "Carrera",
        "Email"
    ]
    widths = [25, 65, 55, 45]
    header_tabla(pdf, headers, widths)
    pdf.set_font("Arial", "", 9)
    fill = False
    for alu in data_alumnos:
        if fill:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        nombre = f"{alu['apellido']}, {alu['nombre']}"
        pdf.cell(25, 8, str(alu['padron']), 1, 0, "C", fill)
        pdf.cell(65, 8, nombre[:35], 1, 0, "L", fill)
        pdf.cell(55, 8, alu['carrera'][:30], 1, 0, "L", fill)
        pdf.cell(45, 8, alu['email'][:28], 1, 0, "L", fill)
        pdf.ln()
        fill = not fill
    return pdf.output(dest="S")

def crear_pdf_estadisticas(data_stats):
    pdf = FPDF()
    configurar_pdf(pdf, "Metricas de Aprobacion")
    for row in data_stats:
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 11)
        titulo = (
            f"{row['evaluacion_titulo']} "
            f"({row['tipo_evaluacion']})"
        )
        pdf.cell(190, 10, titulo, 1, 1, "L", True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(
            95,
            8,
            f"Cantidad de notas: {row['total_notas']}",
            1
        )
        pdf.cell(
            95,
            8,
            f"Promedio: {row['nota_promedio']}",
            1
        )
        pdf.ln()
        pdf.cell(
            95,
            8,
            f"Aprobados: {row['aprobados']}",
            1
        )
        pdf.cell(
            95,
            8,
            f"Desaprobados: {row['desaprobados']}",
            1
        )
        pdf.ln(12)
        total = row['aprobados'] + row['desaprobados']
        if total > 0:
            aprobados_w = (
                150 * row['aprobados'] / total
            )
            desaprobados_w = (
                150 * row['desaprobados'] / total
            )
            x = pdf.get_x()
            y = pdf.get_y()
            # Verde
            pdf.set_fill_color(160, 160, 160)
            pdf.rect(x, y, aprobados_w, 8, "F")
            # Gris claro
            pdf.set_fill_color(220, 220, 220)
            pdf.rect(
                x + aprobados_w,
                y,
                desaprobados_w,
                8,
                "F"
            )
            pdf.ln(15)
    return pdf.output(dest="S")

def crear_pdf_equipos(data_equipos):
    pdf = FPDF("P", "mm", "A4")
    configurar_pdf(pdf, "Listado General de Equipos")
    headers = [
        "Nro Grupo",
        "Nombre Grupo",
        "Integrantes",
        "Tutor"
    ]

    widths = [25, 60, 80, 25]
    header_tabla(pdf, headers, widths)
    pdf.set_font("Arial", "", 9)
    for idx, eq in enumerate(data_equipos, start=1):
        integrantes = []
        if eq['integrantes']:
            integrantes = eq['integrantes'].split(" | ")
        altura = max(8, len(integrantes) * 7)
        y_inicial = pdf.get_y()
        if idx % 2 == 0:
            pdf.set_fill_color(245, 245, 245)
        else:
            pdf.set_fill_color(255, 255, 255)
        # nombre equipo
        pdf.multi_cell(
            widths[0],
            altura,
            str(idx),
            1,
            "C",
            True
        )
        x = pdf.get_x()
        y = y_inicial
        pdf.set_xy(10 + widths[0], y)
        # nombre equipo
        pdf.multi_cell(
            widths[1],
            altura,
            eq['equipo_nombre'] or "N/A",
            1,
            "C",
            True
        )

        pdf.set_xy(
            10 + widths[0] + widths[1],
            y
        )
        # integrantes
        texto_integrantes = "\n".join(integrantes)
        if not texto_integrantes:
            texto_integrantes = "Sin integrantes"
        pdf.multi_cell(
            widths[2],
            7,
            texto_integrantes,
            1,
            "L",
            True
        )
        altura_real = pdf.get_y() - y
        pdf.set_xy(
            10 + widths[0] + widths[1] + widths[2],
            y
        )
        # tutor
        pdf.multi_cell(
            widths[3],
            altura_real,
            eq.get('tutor', '-')[:15],
            1,
            "C",
            True
        )
    return pdf.output(dest="S")