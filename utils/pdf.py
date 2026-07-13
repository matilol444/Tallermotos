from pathlib import Path
from datetime import datetime
import os
import subprocess
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generar_pdf_presupuesto(presupuesto_data, salida=None):
    if salida is None:
        base_dir = Path(__file__).resolve().parent.parent
        salida = base_dir / "presupuestos" / f"presupuesto_{presupuesto_data['id']}.pdf"

    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(salida), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Taller de Motos", styles['Title']))
    story.append(Paragraph("Presupuesto", styles['Heading2']))
    story.append(Spacer(1, 0.3 * cm))

    fecha = presupuesto_data.get('fecha') or datetime.now().strftime('%d/%m/%Y')
    story.append(Paragraph(f"N° Presupuesto: {presupuesto_data.get('id', '-')}", styles['Heading4']))
    story.append(Paragraph(f"Fecha: {fecha}", styles['BodyText']))
    story.append(Spacer(1, 0.3 * cm))

    datos_cliente = [
        [Paragraph("Cliente", styles['Heading4']), Paragraph(presupuesto_data.get('cliente_nombre', '-'), styles['BodyText'])],
        [Paragraph("Teléfono", styles['Heading4']), Paragraph(presupuesto_data.get('cliente_telefono', '-'), styles['BodyText'])],
        [Paragraph("Dirección", styles['Heading4']), Paragraph(presupuesto_data.get('cliente_direccion', '-'), styles['BodyText'])],
    ]
    tabla_cliente = Table(datos_cliente, colWidths=[3 * cm, 11 * cm])
    tabla_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(Paragraph("Datos del cliente", styles['Heading4']))
    story.append(tabla_cliente)
    story.append(Spacer(1, 0.4 * cm))

    datos_moto = [
        [Paragraph("Marca", styles['Heading4']), Paragraph(presupuesto_data.get('moto_marca', '-'), styles['BodyText'])],
        [Paragraph("Modelo", styles['Heading4']), Paragraph(presupuesto_data.get('moto_modelo', '-'), styles['BodyText'])],
        [Paragraph("Patente", styles['Heading4']), Paragraph(presupuesto_data.get('moto_patente', '-'), styles['BodyText'])],
        [Paragraph("Kilómetros", styles['Heading4']), Paragraph(str(presupuesto_data.get('moto_kilometros', '-')), styles['BodyText'])],
    ]
    tabla_moto = Table(datos_moto, colWidths=[3 * cm, 11 * cm])
    tabla_moto.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(Paragraph("Datos de la moto", styles['Heading4']))
    story.append(tabla_moto)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Descripción del trabajo", styles['Heading4']))
    story.append(Paragraph(presupuesto_data.get('descripcion', '-'), styles['BodyText']))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Repuestos", styles['Heading4']))
    story.append(Paragraph(presupuesto_data.get('repuestos', '-'), styles['BodyText']))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Mano de obra", styles['Heading4']))
    story.append(Paragraph(presupuesto_data.get('mano_obra', '-'), styles['BodyText']))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph(f"Total: ${presupuesto_data.get('total', 0):.2f}", styles['Heading3']))
    story.append(Paragraph(f"Estado: {presupuesto_data.get('estado', '-')}", styles['BodyText']))

    doc.build(story)

    if sys.platform.startswith('linux'):
        try:
            subprocess.Popen(["xdg-open", str(salida)])
        except Exception:
            pass
    elif sys.platform == "darwin":
        try:
            subprocess.Popen(["open", str(salida)])
        except Exception:
            pass
    elif os.name == "nt":
        try:
            os.startfile(str(salida))
        except Exception:
            pass

    return str(salida)
