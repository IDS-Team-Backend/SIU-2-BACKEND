from fpdf import FPDF

def crear_pdf_alumnos(data_alumnos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Listado de Alumnos Filtrados", ln=True, align="C")
    pdf.ln(10)
    
    # Encabezados
    pdf.set_font("Arial", "B", 10)
    pdf.cell(25, 8, "Padrón", 1)
    pdf.cell(65, 8, "Apellido y Nombre", 1)
    pdf.cell(60, 8, "Carrera", 1)
    pdf.cell(40, 8, "Email", 1)
    pdf.ln()
    
    # Filas
    pdf.set_font("Arial", "", 9)
    for alu in data_alumnos:
        nombre_completo = f"{alu['apellido']}, {alu['nombre']}"
        pdf.cell(25, 7, str(alu['padron']), 1)
        pdf.cell(65, 7, nombre_completo[:32], 1)
        pdf.cell(60, 7, alu['carrera'][:30], 1)
        pdf.cell(40, 7, alu['email'][:22], 1)
        pdf.ln()
        
    return pdf.output(dest='S')


def crear_pdf_estadisticas(data_stats):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Métricas de Aprobación", ln=True, align="C")
    pdf.ln(10)
    
    for row in data_stats:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Evaluación: {row['evaluacion_titulo']} ({row['tipo_evaluacion']})", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"  - Cantidad de Notas: {row['total_notas']}", ln=True)
        pdf.cell(0, 6, f"  - Nota Promedio: {row['nota_promedio']}", ln=True)
        pdf.cell(0, 6, f"  - Alumnos Aprobados: {row['aprobados']}", ln=True)
        pdf.cell(0, 6, f"  - Alumnos Desaprobados: {row['desaprobados']}", ln=True)
        
        # Gráfico de barras simple dibujado con celdas de color nativas
        total = row['aprobados'] + row['desaprobados']
        if total > 0:
            pct_aprobados = row['aprobados'] / total
            pdf.ln(2)
            # Rectángulo verde (Aprobados)
            pdf.set_fill_color(46, 204, 113)
            pdf.rect(15, pdf.get_y(), 100 * pct_aprobados, 5, "F")
            # Rectángulo rojo (Desaprobados)
            pdf.set_fill_color(231, 76, 60)
            pdf.rect(15 + (100 * pct_aprobados), pdf.get_y(), 100 * (1 - pct_aprobados), 5, "F")
            pdf.ln(8)
        else:
            pdf.ln(4)
            
    return pdf.output(dest='S')


def crear_pdf_equipos(data_equipos):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Listado General de Equipos", ln=True, align="C")
    pdf.ln(10)
    
    for eq in data_equipos:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 7, f"Equipo: {eq['equipo_nombre']} ({eq['evaluacion_contexto']})", ln=True)
        pdf.set_font("Arial", "", 9)
        
        if eq['integrantes']:
            integrantes = eq['integrantes'].split(' | ')
            for integrante in integrantes:
                pdf.cell(0, 5, f"  * {integrante}", ln=True)
        else:
            pdf.cell(0, 5, "  * Sin integrantes asignados.", ln=True)
        pdf.ln(4)
        
    return pdf.output(dest='S')