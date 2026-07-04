# -*- coding: utf-8 -*-
# Este archivo contiene las funciones para generar reportes en formato PDF de manera automática.
# Diseña las tablas, tipografía y colores corporativos (Flat Design) de cada reporte contable exportado.

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def _get_styles():
    # Define la tipografía, tamaño y color de las letras para los títulos y subtítulos del reporte.
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor("#111827"),
        alignment=1,
        spaceAfter=20
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor("#4B5563"),
        alignment=1,
        spaceAfter=20
    )
    return title_style, subtitle_style

def _crear_tabla(datos, col_widths=None):
    # Dibuja y da formato visual a una tabla en el archivo PDF (agrega bordes grises y filas con colores alternados).
    t = Table(datos, colWidths=col_widths, repeatRows=1)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#10B981")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#FFFFFF")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#374151")),
    ])
    
    # Alternar colores de fila
    for i in range(1, len(datos)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F9FAFB"))
            
    t.setStyle(style)
    return t

def exportar_diario_pdf(filepath, datos):
    # Genera un documento PDF vertical con la lista de asientos y transacciones registradas en el Libro Diario.
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    title_style, sub_style = _get_styles()
    
    story = []
    story.append(Paragraph("AuraBooks - Libro Diario", title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
    
    table_data = [["Fecha", "Asiento", "Concepto / Cuenta", "Debe", "Haber"]]
    
    for row in datos:
        table_data.append([
            row.get("fecha", ""),
            row.get("asiento_id", ""),
            row.get("concepto", ""),
            row.get("debe", ""),
            row.get("haber", "")
        ])
        
    t = _crear_tabla(table_data, col_widths=[70, 50, 240, 80, 80])
    
    # Alinear montos a la derecha
    t.setStyle(TableStyle([
        ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
    ]))
    
    story.append(t)
    doc.build(story)


def exportar_mayor_pdf(filepath, cuenta_nombre, datos):
    # Genera un documento PDF vertical con el historial detallado de movimientos de una única cuenta (Libro Mayor).
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    title_style, sub_style = _get_styles()
    
    story = []
    story.append(Paragraph(f"Libro Mayor: {cuenta_nombre}", title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
    
    table_data = [["Fecha", "Concepto", "Debe", "Haber", "Saldo"]]
    
    for row in datos:
        table_data.append([
            row.get("fecha", ""),
            row.get("concepto", ""),
            row.get("debe", ""),
            row.get("haber", ""),
            row.get("saldo", "")
        ])
        
    t = _crear_tabla(table_data, col_widths=[70, 210, 80, 80, 80])
    
    # Alinear montos a la derecha
    t.setStyle(TableStyle([
        ('ALIGN', (2, 1), (4, -1), 'RIGHT'),
    ]))
    
    story.append(t)
    doc.build(story)


def exportar_hoja_trabajo_pdf(filepath, filas, totales):
    # Genera una hoja de cálculo contable (Hoja de Trabajo) en PDF de formato horizontal (apaisado)
    # debido a la gran cantidad de columnas (12 columnas de sumas, saldos y cuentas).
    # Usar landscape para hoja de trabajo porque tiene muchas columnas
    doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
    title_style, sub_style = _get_styles()
    
    story = []
    story.append(Paragraph("Hoja de Trabajo (12 Columnas)", title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
    
    # Header complejo (2 filas combinadas lógicamente en la tabla)
    table_data = [
        ["Cuenta Contable", "Sumas", "", "Saldos", "", "Ajustes", "", "Saldos Ajustados", "", "Resultados", "", "Balance G.", ""],
        ["", "Debe", "Haber", "Debe", "Haber", "Debe", "Haber", "Debe", "Haber", "Gasto", "Ingreso", "Activo", "Pas+Pat"]
    ]
    
    def fmt(val):
        return f"{val:,.2f}" if val != 0 else "-"
        
    for fila in filas:
        table_data.append([
            fila["cuenta"],
            fmt(fila["sum_d"]), fmt(fila["sum_h"]),
            fmt(fila["sal_d"]), fmt(fila["sal_h"]),
            fmt(fila["aju_d"]), fmt(fila["aju_h"]),
            fmt(fila["aju_sal_d"]), fmt(fila["aju_sal_h"]),
            fmt(fila["res_d"]), fmt(fila["res_h"]),
            fmt(fila["bg_d"]), fmt(fila["bg_h"])
        ])
        
    # Fila de totales
    table_data.append([
        "SUMAS IGUALES",
        fmt(totales["sum_d"]), fmt(totales["sum_h"]),
        fmt(totales["sal_d"]), fmt(totales["sal_h"]),
        fmt(totales["aju_d"]), fmt(totales["aju_h"]),
        fmt(totales["aju_sal_d"]), fmt(totales["aju_sal_h"]),
        fmt(totales["res_d"]), fmt(totales["res_h"]),
        fmt(totales["bg_d"]), fmt(totales["bg_h"])
    ])
    
    t = _crear_tabla(table_data)
    
    # Personalizar la tabla para la cabecera doble y alinear todo a la derecha
    extra_style = [
        ('SPAN', (0, 0), (0, 1)), # Span Cuenta
        ('SPAN', (1, 0), (2, 0)), # Span Sumas
        ('SPAN', (3, 0), (4, 0)), # Span Saldos
        ('SPAN', (5, 0), (6, 0)), # Span Ajustes
        ('SPAN', (7, 0), (8, 0)), # Span Ajustados
        ('SPAN', (9, 0), (10, 0)), # Span Resultados
        ('SPAN', (11, 0), (12, 0)), # Span Balance
        ('ALIGN', (1, 2), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 0), (-1, -1), 7), # Letra más pequeña para que quepa todo
        ('FONTSIZE', (0, 0), (-1, 1), 8),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Totales en negrita
    ]
    t.setStyle(TableStyle(extra_style))
    
    story.append(t)
    doc.build(story)


def exportar_estados_financieros_pdf(filepath, titulo, datos_tabla):
    # Genera reportes financieros oficiales (como el Balance General o Estado de Resultados)
    # en PDF, formateando con negritas y fondo gris las líneas de sumas totales.
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    title_style, sub_style = _get_styles()
    
    story = []
    story.append(Paragraph(titulo, title_style))
    story.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
    
    # datos_tabla es una lista de listas [[concepto, monto, es_total]]
    table_data = []
    
    for row in datos_tabla:
        concepto = row[0]
        monto = row[1]
        
        table_data.append([
            concepto,
            monto
        ])
        
    t = _crear_tabla(table_data, col_widths=[350, 120])
    
    # Personalizar estilos según si es total o no
    extra_style = [
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]
    
    for i, row in enumerate(datos_tabla):
        if len(row) > 2 and row[2] == True: # es_total
            extra_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
            extra_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.HexColor("#111827")))
            extra_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#E5E7EB")))
            
    t.setStyle(TableStyle(extra_style))
    
    story.append(t)
    doc.build(story)
