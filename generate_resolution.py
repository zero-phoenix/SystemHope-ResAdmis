#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar la Resolución de Primera Instancia (R1) en formato Word auténtico.
Genera un archivo .docx REAL (ZIP OOXML), no un archivo de texto con extensión .docx
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from pathlib import Path

def crear_resolucion():
    # Crear documento nuevo
    doc = Document()

    # Configurar márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Propiedades del documento
    doc.core_properties.author = 'SECRETARIA TÉCNICA - INDECOPI'
    doc.core_properties.title = 'RESOLUCIÓN DE PRIMERA INSTANCIA (R1) - ADM 0001-2026-CC1'

    # ENCABEZADO
    header = doc.add_paragraph()
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run('SECRETARIA TÉCNICA DE LA COMISIÓN\nDE PROTECCIÓN AL CONSUMIDOR 1')
    run.font.italic = True
    run.font.bold = True
    run.font.size = Pt(11)

    # Espacio
    doc.add_paragraph()

    # TABLA METADATA
    table = doc.add_table(rows=5, cols=2)
    table.style = 'Light Grid Accent 1'

    cells = table.rows
    cells[0].cells[0].text = 'EXPEDIENTE'
    cells[0].cells[1].text = '0001-2026/CC1'
    cells[1].cells[0].text = 'DENUNCIANTE'
    cells[1].cells[1].text = 'EUFEMIA ESTEPA MARTINEZ MORENO DE ROMERO'
    cells[2].cells[0].text = 'DENUNCIADO'
    cells[2].cells[1].text = 'INTERSEGURO COMPAÑÍA DE SEGUROS S.A.'
    cells[3].cells[0].text = 'ASUNTO'
    cells[3].cells[1].text = 'Rechazo injustificado de cobertura de seguro de vida'
    cells[4].cells[0].text = 'FECHA'
    cells[4].cells[1].text = 'Lima, 19 de julio de 2026'

    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)

    doc.add_paragraph()

    # I. HECHOS
    heading_i = doc.add_paragraph()
    run_i = heading_i.add_run('I. HECHOS')
    run_i.font.bold = True
    run_i.font.size = Pt(11)

    hechos_text = """Mediante escrito de denuncia del 19 de marzo de 2026, la señora Eufemia Estepa Martínez Moreno de Romero, identificada con DNI N° 06959880, con domicilio real en Calle Unión 0, Urb. Frente al Colegio, departamento de Lima, denunció a Interseguro Compañía de Seguros S.A., identificada con RUC N° 20382748566, con domicilio en Av. Javier Prado Este N° 492, piso 26, Torre Orquídeas, distrito de San Isidro, Lima, por presuntas infracciones a la Ley N° 29571 - Código de Protección y Defensa del Consumidor.

Conforme al Informe Policial N° 562-2025-REG.POL-LIMA/DIVPOL-CHO-DEPINCRICHOSICA, de fecha 24 de abril de 2025, el asegurado Leonardo Romero Martínez perdió la vida el 23 de marzo de 2025. Según las investigaciones policiales, el conductor de un vehículo de transporte público (mototaxi) lo habría abandonado en la vía pública en circunstancias no esclarecidas, sin que hasta la fecha se haya identificado al responsable ni al vehículo. Conforme a medios probatorios y audiovisuales, el asegurado habría sido abandonado aún con vida a escasos metros de una posta médica, siendo auxiliado varias horas después.

De acuerdo con las pericias y el certificado de necropsia, el asegurado se encontraba bajo los efectos del alcohol. La causa de muerte fue un paro cardíaco asociado a edema cerebral y daño pulmonar severo por asfixia, sin que se haya determinado con exactitud la causa inicial del deceso.

Con fecha 8 de septiembre de 2025, Interseguro emitió el informe N° GOT-SIN-90852-2025, correspondiente a la póliza N° 1760006823 (Producto: Vida Free), mediante el cual comunicó a los deudos que no se otorgaría la cobertura debido a que el asegurado se encontraba en estado de ebriedad. En consecuencia, se negó el pago del monto asegurado a la beneficiaria, quien es la madre del asegurado, pese a que este había designado dicha protección para salvaguardar la estabilidad económica familiar.

La denunciante alegó que la cláusula de exclusión por ebriedad resulta ambigua, al no distinguir expresamente entre los supuestos en los que el asegurado actúa como sujeto activo (quien genera el riesgo voluntariamente) o como sujeto pasivo (quien sufre las consecuencias del evento dañoso). En el presente caso, el asegurado no ocasionó directamente el evento dañoso, sino que fue colocado en una situación de vulnerabilidad por la conducta de un tercero."""

    for parrafo in hechos_text.split('\n\n'):
        p = doc.add_paragraph(parrafo)
        p_format = p.paragraph_format
        p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = 'Arial'

    doc.add_paragraph()

    # II. ANÁLISIS Y ADMISIÓN A TRÁMITE
    heading_ii = doc.add_paragraph()
    run_ii = heading_ii.add_run('II. ANÁLISIS Y ADMISIÓN A TRÁMITE')
    run_ii.font.bold = True
    run_ii.font.size = Pt(11)

    analisis_text = """La Secretaría Técnica de la Comisión de Protección al Consumidor 1, en ejercicio de sus facultades, considera que el hecho denunciado, consistente en que la compañía aseguradora habría rechazado de manera injustificada la cobertura del siniestro ocurrido el 23 de marzo de 2025, respecto del asegurado Leonardo Romero Martínez, pese a que este se encontraba en condición de sujeto pasivo de un hecho de terceros, involucraría una presunta afectación a sus expectativas de cobertura, quien no habría encontrado una correspondencia entre lo que esperaba recibir de parte de la aseguradora y lo que realmente recibió (rechazo injustificado). Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de idoneidad, tipificado en los artículos 18° y 19° del Código de Protección y Defensa del Consumidor.

Asimismo, la Secretaría Técnica, en ejercicio de sus facultades, considera que el hecho denunciado, consistente en que la compañía aseguradora no precisó claramente que la cláusula de exclusión por ebriedad aplicaría únicamente cuando el asegurado actúe como sujeto activo generador del riesgo, involucraría una presunta ambigüedad contractual. La falta de precisión sobre si la exclusión aplica también cuando el asegurado es víctima bajo efectos del alcohol genera una ambigüedad contractual, la cual, conforme a los principios de protección al consumidor (regla pro consumidor y contra proferentem), debe interpretarse en el sentido más favorable al asegurado. Por tanto, corresponde calificar el hecho como una presunta infracción al derecho a la información, tipificado en el artículo 1, numeral 1, literal b) y al artículo 2 del Código.

La conducta de Interseguro constituye publicidad engañosa y vulnera el deber de información, al no precisar claramente que la exclusión también aplicaría únicamente en casos donde el asegurado sea sujeto activo y genere el riesgo. Esto genera una interpretación abusiva del contrato y una evidente asimetría informativa en perjuicio del consumidor."""

    for parrafo in analisis_text.split('\n\n'):
        p = doc.add_paragraph(parrafo)
        p_format = p.paragraph_format
        p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = 'Arial'

    doc.add_paragraph()

    # III. REQUERIMIENTO DE INFORMACIÓN
    heading_iii = doc.add_paragraph()
    run_iii = heading_iii.add_run('III. REQUERIMIENTO DE INFORMACIÓN')
    run_iii.font.bold = True
    run_iii.font.size = Pt(11)

    requerimiento_intro = doc.add_paragraph(
        'A efectos de tener mayores elementos que sirvan para la resolución definitiva del presente caso, '
        'la Secretaría Técnica, en ejercicio de las facultades que la ley le confiere, requiere a Interseguro '
        'Compañía de Seguros S.A. que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día '
        'siguiente de la notificación de la presente resolución, cumpla con remitir:'
    )
    requerimiento_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # Items del requerimiento
    items_requerimiento = [
        'Copia íntegra de la Póliza N° 1760006823, incluyendo todas sus Condiciones Generales y Particulares;',
        'Copia del informe N° GOT-SIN-90852-2025 completo, con sustentación detallada de los fundamentos para el rechazo de cobertura;',
        'Historial completo de comunicaciones mantenidas con la beneficiaria, Eufemia Estepa Martínez Moreno de Romero, previas y posteriores al rechazo; y',
        'Documentación que sustente el análisis técnico-legal respecto de la interpretación de la cláusula de exclusión por ebriedad en relación a los conceptos de sujeto activo y sujeto pasivo del riesgo.'
    ]

    for idx, item in enumerate(items_requerimiento, 1):
        p = doc.add_paragraph(f'({chr(96+idx)})  {item}', style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = 'Arial'

    doc.add_paragraph()

    # IV. RESOLUCIÓN
    heading_iv = doc.add_paragraph()
    run_iv = heading_iv.add_run('IV. RESOLUCIÓN')
    run_iv.font.bold = True
    run_iv.font.size = Pt(11)

    # PRIMERO
    p = doc.add_paragraph()
    run_prim = p.add_run('PRIMERO: ')
    run_prim.font.bold = True
    p.add_run(
        'Admitir a trámite la denuncia interpuesta el 19 de marzo de 2026 por la señora Eufemia Estepa Martínez Moreno de Romero '
        'contra Interseguro Compañía de Seguros S.A., por las siguientes presuntas infracciones al Código de Protección y Defensa del Consumidor:'
    )
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    infraccion_items = [
        'Presunta infracción a los artículos 18° y 19° de la Ley N° 29571, Código de Protección y Defensa del Consumidor, en tanto la compañía aseguradora habría rechazado de manera injustificada la cobertura del siniestro ocurrido el 23 de marzo de 2025, respecto del asegurado Leonardo Romero Martínez, quien se encontraba en condición de sujeto pasivo de un hecho potencialmente delictivo (abandono en la vía pública).',
        'Presunta infracción al artículo 1, numeral 1, literal b) y al artículo 2 de la Ley N° 29571, Código de Protección y Defensa del Consumidor, en tanto la compañía aseguradora habría incurrido en falta de información clara al no precisar expresamente que la cláusula de exclusión por ebriedad aplicaría únicamente cuando el asegurado actúe como sujeto activo generador del riesgo, generando una ambigüedad contractual que vulnera el derecho a la información.'
    ]

    for idx, item in enumerate(infraccion_items, 1):
        p = doc.add_paragraph(f'({chr(96+idx)})  {item}', style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # SEGUNDO
    p = doc.add_paragraph()
    run_seg = p.add_run('SEGUNDO: ')
    run_seg.font.bold = True
    p.add_run(
        'Tener por ofrecidos los medios probatorios presentados en el escrito de denuncia del 19 de marzo de 2026, '
        'consistentes en: copia de Informe Policial N° 562-2025, copia del Certificado de Defunción, copia del Informe de la '
        'aseguradora N° GOT-SIN-90852-2025, copia de la Póliza de Seguro N° 1760006823, copias de DNI de las partes involucradas, '
        'y copias de archivos digitalizados, según lo especificado en la denuncia.'
    )
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # TERCERO
    p = doc.add_paragraph()
    run_ter = p.add_run('TERCERO: ')
    run_ter.font.bold = True
    p.add_run(
        'Requerir a Interseguro Compañía de Seguros S.A. que remita la documentación solicitada en la sección III del '
        'presente acto administrativo, conforme al plazo y requisitos establecidos, bajo apercibimiento de lo dispuesto '
        'en la legislación de procedimiento administrativo.'
    )
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # CUARTO
    p = doc.add_paragraph()
    run_cuar = p.add_run('CUARTO: ')
    run_cuar.font.bold = True
    p.add_run(
        'Correr traslado de la presente denuncia a Interseguro Compañía de Seguros S.A., para que comparezca y presente '
        'sus descargos en un plazo no mayor de cinco (5) días hábiles contados desde la notificación de esta resolución, '
        'de conformidad con lo dispuesto en el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, '
        'aprobada por Decreto Legislativo 807.'
    )
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # QUINTO
    p = doc.add_paragraph()
    run_quin = p.add_run('QUINTO: ')
    run_quin.font.bold = True
    p.add_run(
        'Requerir a la señora Eufemia Estepa Martínez Moreno de Romero e Interseguro Compañía de Seguros S.A. para que, '
        'dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciban la notificación en su bandeja de correo '
        'electrónico, efectúen la confirmación de recepción de la notificación remitida por este despacho a su correo electrónico, '
        'de conformidad con el segundo párrafo del numeral 4 del artículo 20 del Texto Único Ordenado de la Ley del Procedimiento '
        'Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación '
        'y notificarles conforme al numeral 1 del artículo 20 del citado cuerpo normativo.'
    )
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_paragraph()

    # FIRMA
    firma = doc.add_paragraph()
    firma.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_firma = firma.add_run('Lima, 19 de julio de 2026')
    run_firma.font.size = Pt(11)

    doc.add_paragraph()
    doc.add_paragraph()

    firma_final = doc.add_paragraph()
    firma_final.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_final = firma_final.add_run('_________________________________\nSECRETARIA TÉCNICA\nCOMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1')
    run_final.font.size = Pt(10)

    # Pie de página
    footer = doc.sections[0].footer
    footer_para = footer.paragraphs[0]
    footer_para.text = 'M-CPC-01/03'
    footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Guardar documento
    output_path = Path(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0001-2026-CC1_R1.docx')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Guardar REAL .docx (ZIP OOXML, no texto plano)
    doc.save(str(output_path))

    return output_path

if __name__ == '__main__':
    try:
        path = crear_resolucion()
        print(f"✓ Documento .docx auténtico creado en:")
        print(f"  {path}")
        print(f"\n✓ Tamaño: {path.stat().st_size} bytes")
        print(f"✓ Es archivo REAL .docx (ZIP OOXML)")
        print(f"✓ Puede abrirse en Microsoft Word sin errores")
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
