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
    return pdf.output(dest='S').encode('latin-1')

def crear_pdf_estadisticas(data_stats):
    pdf = FPDF()
    pdf.add_page()
    
    # Título Principal
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Estadisticas del Curso", ln=True, align="C")
    pdf.ln(5)

    # --- 1. Promedio por Evaluación ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Promedio por Evaluacion", ln=True)
    
    for row in data_stats.get('promedio_por_evaluacion', []):
        pdf.set_fill_color(230, 230, 230)
        pdf.set_font("Arial", "B", 11)
        titulo = f"{row.get('evaluacion_titulo', '')} ({row.get('tipo_evaluacion', '')})"
        pdf.cell(190, 10, titulo, 1, 1, "L", True)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(95, 8, f"Cantidad de notas: {row.get('total_notas', 0)}", 1)
        pdf.cell(95, 8, f"Promedio: {row.get('nota_promedio', 0)}", 1)
        pdf.ln()
        
        aprobados = row.get('aprobados', 0)
        desaprobados = row.get('desaprobados', 0)
        
        pdf.cell(95, 8, f"Aprobados: {aprobados}", 1)
        pdf.cell(95, 8, f"Desaprobados: {desaprobados}", 1)
        pdf.ln(12)
        
        # Gráfico de barras de aprobación
        total = aprobados + desaprobados
        if total > 0:
            aprobados_w = 150 * float(aprobados) / float(total)
            desaprobados_w = 150 * float(desaprobados) / float(total)
            x, y = pdf.get_x(), pdf.get_y()
            
            pdf.set_fill_color(160, 160, 160) 
            pdf.rect(x, y, aprobados_w, 8, "F")
            pdf.set_fill_color(220, 220, 220)
            pdf.rect(x + aprobados_w, y, desaprobados_w, 8, "F")
            pdf.ln(12)

    pdf.ln(5)

    # --- 2. Promedio por Tipo ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "2. Promedio por Tipo de Evaluacion", ln=True)
    pdf.set_font("Arial", "", 10)
    for row in data_stats.get('promedio_por_tipo', []):
        pdf.cell(95, 8, f"Tipo: {row.get('nombre', 'N/A')}", 1)
        pdf.cell(95, 8, f"Promedio: {row.get('promedio', 0)}", 1, ln=True)

    pdf.ln(8)

    # --- 3. Distribución de Notas ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "3. Distribucion de Notas", ln=True)
    pdf.set_font("Arial", "", 10)
    for row in data_stats.get('distribucion_notas', []):
        pdf.cell(95, 8, f"Nota (Piso): {row.get('rango', 'N/A')}", 1)
        pdf.cell(95, 8, f"Cantidad de Alumnos: {row.get('cantidad', 0)}", 1, ln=True)

    pdf.ln(8)

    # --- 4. Estado de Cursada ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "4. Estado de Cursada", ln=True)
    pdf.set_font("Arial", "", 10)
    for row in data_stats.get('estado_cursada', []):
        estado = str(row.get('estado', 'N/A')).capitalize()
        pdf.cell(95, 8, f"Estado: {estado}", 1)
        pdf.cell(95, 8, f"Alumnos: {row.get('cantidad', 0)}", 1, ln=True)

    pdf.ln(8)

    # --- 5. Asistencia por Clase ---
    pdf.add_page() 
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "5. Porcentaje de Asistencia por Clase", ln=True)
    pdf.set_font("Arial", "", 10)
    for row in data_stats.get('asistencia_por_clase', []):
        pdf.cell(140, 8, f"Clase: {row.get('nombre', 'N/A')}", 1)
        pdf.cell(50, 8, f"Asistencia: {row.get('porcentaje', 0)}%", 1, ln=True, align="R")
        
    return pdf.output(dest='S').encode('latin-1')

def crear_pdf_equipos(data_equipos):
    pdf = FPDF("P", "mm", "A4")
    configurar_pdf(pdf, "Listado General de Equipos")

    headers = [
        "Nro Grupo",
        "Nombre Grupo",
        "Integrantes"
    ]

    # 25 + 60 + 80 + 25 = 190
    # mantenemos 190 mm totales
    widths = [25, 60, 105]

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

        # Número de grupo
        pdf.multi_cell(
            widths[0],
            altura,
            str(idx),
            1,
            "C",
            True
        )

        y = y_inicial

        # Nombre del grupo
        pdf.set_xy(10 + widths[0], y)
        pdf.multi_cell(
            widths[1],
            altura,
            eq['equipo_nombre'] or "N/A",
            1,
            "C",
            True
        )

        # Integrantes
        pdf.set_xy(
            10 + widths[0] + widths[1],
            y
        )

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
        pdf.set_y(max(y + altura, pdf.get_y()))
        pdf.set_x(10)

    return pdf.output(dest='S').encode('latin-1')