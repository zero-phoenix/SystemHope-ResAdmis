#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para generar la Resolución ADM 0955-2026 en formato Word idéntico al PDF.
Expediente: 0955-2026/CC1
Denunciante: Eufemia Estefa Martínez Moreno de Romero (Señora Martínez)
Denunciado: Interseguro Compañía de Seguros S.A. (Interseguro)
Páginas: 6
Tamaño letra: 10pt Arial Narrow
Espaciado: simple
Pie de página: M-CPC-01/03
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from pathlib import Path


def agregar_pie_pagina(doc, texto):
    """Agrega pie de página a todas las secciones."""
    for section in doc.sections:
        footer = section.footer
        footer_para = footer.paragraphs[0]
        footer_para.text = texto
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in footer_para.runs:
            run.font.size = Pt(9)
            run.font.name = 'Arial Narrow'


def set_space_after_paragraph(paragraph, pt=0):
    """Establece espacio después de párrafo."""
    paragraph.paragraph_format.space_after = Pt(pt)


def set_space_before_paragraph(paragraph, pt=0):
    """Establece espacio antes de párrafo."""
    paragraph.paragraph_format.space_before = Pt(pt)


def crear_resolucion_955():
    """Crea la Resolución ADM 0955-2026 R1."""
    doc = Document()

    # Configurar márgenes
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Propiedades del documento
    doc.core_properties.author = 'SECRETARIA TÉCNICA - INDECOPI CPC1'
    doc.core_properties.title = 'RESOLUCIÓN ADM 0955-2026-CPC1-R1'

    # ENCABEZADO EN CADA PÁGINA
    def agregar_encabezado():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run('SECRETARIA TÉCNICA DE LA\nCOMISIÓN DE PROTECCIÓN AL CONSUMIDOR 1\nSEDE CENTRAL')
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
        set_space_after_paragraph(p, 6)

    agregar_encabezado()

    # TABLA DE DATOS
    table = doc.add_table(rows=7, cols=2)
    table.style = 'Light Grid Accent 1'

    # Llenar tabla
    datos = [
        ('EXPEDIENTE', '0955-2026/CC1'),
        ('DENUNCIANTE', 'EUFEMIA ESTEFA MARTÍNEZ MORENO DE ROMERO (SEÑORA\nMARTÍNEZ)'),
        ('DENUNCIADO', 'INTERSEGURO COMPAÑÍA DE SEGUROS S.A. (INTERSEGURO)'),
        ('MATERIAS', 'ADMISIÓN A TRÁMITE\nREQUERIMIENTO DE INFORMACIÓN'),
        ('RESOLUCIÓN', '1'),
        ('', ''),  # Fila en blanco
        ('', 'Lima, 20 de abril de 2026'),
    ]

    for i, (label, value) in enumerate(datos):
        table.rows[i].cells[0].text = label
        table.rows[i].cells[1].text = value
        for cell in table.rows[i].cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.name = 'Arial Narrow'

    set_space_after_paragraph(table.rows[-1].cells[1].paragraphs[0], 10)

    # I. HECHOS
    p = doc.add_paragraph()
    run = p.add_run('I. HECHOS')
    run.font.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # Punto 1
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0)
    run = p.add_run('1. ')
    run.font.bold = False
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'

    texto_punto1 = 'Mediante el escrito del 19 de marzo de 2026, la señora Martínez denunció a Interseguro por presuntas infracciones a la Ley N°29571, Código de Protección y Defensa del Consumidor (en adelante, Código)'
    run_cont = p.add_run(texto_punto1)
    run_cont.font.size = Pt(10)
    run_cont.font.name = 'Arial Narrow'

    # Agregar nota al pie
    run_nota = p.add_run('1')
    run_nota.font.superscript = True
    run_nota.font.size = Pt(8)

    p.add_run(', señalando lo siguiente:')
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    set_space_after_paragraph(p, 6)

    # Subitems (i), (ii), (iii), (iv), (v)
    subitems = [
        '(i) El 10 de setiembre de 2024, inició la vigencia del Seguro de Vida – Póliza N°1760006823 (en adelante, Seguro de Vida), adquirido por su hijo de iniciales L.M.R. (en adelante, asegurado), en el cual se le consignó en calidad de única beneficiaria.',
        '(ii) El 23 de marzo de 2025, el asegurado perdió la vida en circunstancias vinculadas a su abandono en la vía pública por parte del conductor de un vehículo de transporte público no identificado, sin que se haya determinado la identidad del responsable ni del vehículo involucrado.',
        '(iii) El 24 de abril de 2025, se emitió el Informe Policial N°562-2025-REG.POL-LIMA/DIVPOL-CHO-DEPINCRI-CHOSICA, en el cual se dejó constancia de las circunstancias del fallecimiento del asegurado, incluyendo su abandono en la vía pública y la falta de identificación del responsable.',
        '(iv) Posteriormente, conforme a las pericias y al certificado de necropsia, se determinó que el asegurado se encontraba bajo los efectos del alcohol al momento de su fallecimiento, estableciéndose como causa de muerte un paro cardíaco asociado a edema cerebral y daño pulmonar severo por asfixia, sin haberse precisado la causa inicial del deceso.',
        '(v) El 8 de septiembre de 2025, Interseguro emitió la carta N°GOT-SIN-90852-2025, mediante la cual comunicó la denegatoria de su solicitud de cobertura del Seguro de Vida, señalando que el fallecimiento del asegurado se encontraba comprendido dentro de un supuesto de exclusión por estado de ebriedad, motivo por el cual le rechazó el pago del monto asegurado en su calidad de única beneficiaria.',
    ]

    for subitem in subitems:
        p = doc.add_paragraph(subitem)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.line_spacing = 1.0
        for run in p.runs:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
        set_space_after_paragraph(p, 6)

    # Punto 2
    p = doc.add_paragraph()
    run = p.add_run('2. ')
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    p.add_run('La señora Martínez solicitó, en calidad de medida correctiva, que Interseguro cumpla con otorgar la cobertura del Seguro de Desgravamen y otorgar el pago de los daños y perjuicios ocasionados. Asimismo, no requirió de manera expresa el reembolso de costos y costas del presente procedimiento.')
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # Nota al pie del primer párrafo
    p = doc.add_paragraph()
    run = p.add_run('1 Publicado el 2 de setiembre del 2010 en el Diario Oficial El Peruano, vigente desde el 2 de octubre del 2010 y modificado por Decreto Legislativo 1308.')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True
    set_space_after_paragraph(p, 12)

    # Pie de página
    agregar_pie_pagina(doc, 'M-CPC-01/03')

    # PAGE BREAK para página 2
    doc.add_page_break()
    agregar_encabezado()

    # II. DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA
    p = doc.add_paragraph()
    run = p.add_run('II. DE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA')
    run.font.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # Punto 3
    p = doc.add_paragraph()
    run = p.add_run('3. ')
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    texto_p3 = 'La Secretaría Técnica de la Comisión de Protección al Consumidor N°1 (en adelante, la Secretaría Técnica), en ejercicio de sus facultades'
    p.add_run(texto_p3)
    run_nota = p.add_run('2')
    run_nota.font.superscript = True
    run_nota.font.size = Pt(8)
    p.add_run(', considera que el hecho denunciado, consistente en que la compañía aseguradora habría negado injustificadamente al denunciante, mediante la carta N°GOT-SIN-90852-2025, la cobertura de la Póliza N°1760006823 del Seguro de Vida; involucraría una presunta afectación a sus expectativas, quien no habría encontrado una correspondencia entre lo que esperaba recibir de parte del proveedor y lo que realmente recibió. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de idoneidad, tipificado en los artículos 18° y 19° del Código')
    run_nota2 = p.add_run('3')
    run_nota2.font.superscript = True
    run_nota2.font.size = Pt(8)
    p.add_run('.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        if not run.font.superscript:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # Punto 4
    p = doc.add_paragraph()
    run = p.add_run('4. ')
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    p.add_run('En tanto la denuncia reúne los requisitos establecidos por la norma citada, corresponde admitirla a trámite')
    run_nota3 = p.add_run('4')
    run_nota3.font.superscript = True
    run_nota3.font.size = Pt(8)
    p.add_run('.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        if not run.font.superscript:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 12)

    # III. REQUERIMIENTO DE INFORMACIÓN
    p = doc.add_paragraph()
    run = p.add_run('III. REQUERIMIENTO DE INFORMACIÓN')
    run.font.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # Punto 5
    p = doc.add_paragraph()
    run = p.add_run('5. ')
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    p.add_run('A efectos de tener mayores elementos que sirvan para la resolución definitiva del presente caso, la Secretaría Técnica, en ejercicio de las facultades que la ley le confiere, conviene requerir a la compañía aseguradora que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, cumpla con lo siguiente: (i) presentar una copia completa, legible y debidamente suscrita de la Póliza N°1760006823 - Seguro de Vida, así como el cargo de remisión de la póliza; (ii) presentar los medios probatorios que acrediten que la negativa de otorgamiento de cobertura fue justificada; y, (iii) presentar todas las comunicaciones cursadas con la parte denunciante en virtud de los hechos materia de denuncia.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 12)

    # NOTAS AL PIE (Página 2)
    p = doc.add_paragraph()
    run = p.add_run('2 LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True

    # Artículos citados (fuente pequeña)
    articulos_texto = '''Artículo 105.- Autoridad competente.
El Instituto Nacional de Defensa de la Competencia y de la Protección de la Propiedad Intelectual (Indecopi) es la autoridad con competencia primaria y de alcance nacional para conocer las presuntas infracciones a las disposiciones contenidas en el presente Código, así como para imponer las sanciones y medidas correctivas establecidas en el presente capítulo, conforme al Decreto Legislativo N° 1033, Ley de Organización y Funciones del Indecopi. Dicha competencia solo puede ser negada cuando ella haya sido asignada o se asigne a favor de otro organismo por norma expresa con rango de ley.
(…).
LEY DE ORGANIZACIÓN Y FUNCIONES DEL INDECOPI, APROBADA POR DECRETO LEGISLATIVO N° 1033
Artículo 27.- De la Comisión de Protección al Consumidor.-
Corresponde a la Comisión de Protección al Consumidor velar por el cumplimiento de la Ley de Protección al Consumidor y de las leyes que, en general, protegen a los consumidores de la falta de idoneidad de los bienes y servicios en función de la información brindada, de las omisiones de información y de la discriminación en el consumo, así como de aquellas que complementen o sustituyan a las anteriores.'''

    p.add_run('\n' + articulos_texto)
    set_space_after_paragraph(p, 6)

    # Agregar nota 3
    p = doc.add_paragraph()
    run = p.add_run('3 LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 18.- Idoneidad\nSe entiende por idoneidad la correspondencia entre lo que un consumidor espera y lo que efectivamente recibe, en función a lo que se le hubiera ofrecido, la publicidad e información transmitida, las condiciones y circunstancias de la transacción, las características y naturaleza del producto o servicio, el precio, entre otros factores, atendiendo a las circunstancias del caso.\nLa idoneidad es evaluada en función a la propia naturaleza del producto o servicio y a su aptitud para satisfacer la finalidad para la cual ha sido puesto en el mercado. Las autorizaciones por parte de los organismos del Estado para la fabricación de un producto o la prestación de un servicio, en los casos que sea necesario, no eximen de responsabilidad al proveedor frente al consumidor.\nArtículo 19.- Obligación de los proveedores\nEl proveedor responde por la idoneidad y calidad de los productos y servicios ofrecidos; por la autenticidad de las marcas y leyendas que exhiben sus productos o del signo que respalda al prestador del servicio, por la falta de conformidad entre la publicidad comercial de los productos y servicios y éstos, así como por el contenido y la vida útil del producto indicado en el envase, en lo que corresponda.')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True
    set_space_after_paragraph(p, 6)

    # Nota 4
    p = doc.add_paragraph()
    run = p.add_run('4 LEY SOBRE FACULTADES, NORMAS Y ORGANIZACIÓN DEL INDECOPI, APROBADA POR DECRETO LEGISLATIVO N° 807\nArtículo 24.- El Secretario Técnico se encargará de la tramitación del procedimiento. Para ello, cuenta con las siguientes facultades:\n(...)\nc) Admitir denuncias a trámite, en aquellos casos en que la Comisión le haya delegado esta facultad.\n(...).')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True

    # PAGE BREAK página 3
    doc.add_page_break()
    agregar_encabezado()

    # IV. RESOLUCIÓN DE LA SECRETARÍA TÉCNICA
    p = doc.add_paragraph()
    run = p.add_run('IV. RESOLUCIÓN DE LA SECRETARÍA TÉCNICA')
    run.font.bold = True
    run.font.size = Pt(10)
    run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # PRIMERO
    p = doc.add_paragraph()
    run_prim = p.add_run('PRIMERO: ')
    run_prim.font.bold = True
    run_prim.font.size = Pt(10)
    run_prim.font.name = 'Arial Narrow'

    p.add_run('admitir a trámite la denuncia del 19 de marzo de 2026 interpuesta por la señora Eufemia Estefa Martínez Moreno de Romero contra Interseguro Compañía de Seguros S.A., por la presunta infracción a los artículos 18° y 19° de la Ley N° 29571, Código de Protección y Defensa del Consumidor, en tanto la compañía aseguradora habría negado injustificadamente al denunciante, mediante la carta N°GOT-SIN-90852-2025, la cobertura de la Póliza N°1760006823 del Seguro de Vida.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # SEGUNDO
    p = doc.add_paragraph()
    run_seg = p.add_run('SEGUNDO: ')
    run_seg.font.bold = True
    run_seg.font.size = Pt(10)
    run_seg.font.name = 'Arial Narrow'

    p.add_run('tener por ofrecidos los medios probatorios presentados en el escrito de denuncia del 19 de marzo de 2026.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # TERCERO
    p = doc.add_paragraph()
    run_ter = p.add_run('TERCERO: ')
    run_ter.font.bold = True
    run_ter.font.size = Pt(10)
    run_ter.font.name = 'Arial Narrow'

    p.add_run('requerir a Interseguro Compañía de Seguros S.A. que cumpla con lo siguiente:\n(i) presentar documentos que acrediten su inscripción en los Registros Públicos o una declaración jurada que indique que cuenta con dicha inscripción;\n(ii) presentar copia simple de las facultades de representación de su representante legal en el presente procedimiento o la declaración jurada que indique que cuenta con dichas facultades y que estas se encuentran vigentes;\n(iii) consignar el Número de Registro Único de Contribuyentes (RUC); y,\n(iv) fijar domicilio procesal para el procedimiento, de conformidad con el numeral 1 del artículo 442° del Código Procesal Civil. Para ello podrá señalar domicilio físico o una dirección electrónica a la que pueda remitirse las notificaciones;\n(v) en caso califique como micro empresa o pequeña empresa, presentar los documentos que acrediten su volumen de ventas o ingresos brutos percibidos el año anterior relativo a todas sus actividades económicas y el número de trabajadores con el que cuenta')

    run_nota_5 = p.add_run('5')
    run_nota_5.font.superscript = True
    run_nota_5.font.size = Pt(8)

    p.add_run('. Ello, a fin de que la Comisión pueda meritar dicha documentación, conforme lo establece el artículo 110° del Código')

    run_nota_6 = p.add_run('6')
    run_nota_6.font.superscript = True
    run_nota_6.font.size = Pt(8)

    p.add_run('.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        if not run.font.superscript:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # CUARTO
    p = doc.add_paragraph()
    run_cuar = p.add_run('CUARTO: ')
    run_cuar.font.bold = True
    run_cuar.font.size = Pt(10)
    run_cuar.font.name = 'Arial Narrow'

    p.add_run('correr traslado de la denuncia interpuesta el 19 de marzo de 2026, a Interseguro Compañía de Seguros S.A., para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, presente sus descargos en un plazo no mayor de cinco (5) días hábiles contados desde la notificación.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # QUINTO
    p = doc.add_paragraph()
    run_quin = p.add_run('QUINTO: ')
    run_quin.font.bold = True
    run_quin.font.size = Pt(10)
    run_quin.font.name = 'Arial Narrow'

    p.add_run('requerir que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, el proveedor denunciado cumpla con: (i) presentar una copia completa, legible y debidamente suscrita de la Póliza N°1760006823 del Seguro de Vida, así como el cargo de remisión de la póliza; (ii) presentar los medios probatorios que acrediten que la negativa de otorgamiento de cobertura fue justificada; y, (iii) presentar todas las comunicaciones cursadas con la parte denunciante en virtud de los hechos materia de denuncia.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # SEXTO
    p = doc.add_paragraph()
    run_sex = p.add_run('SEXTO: ')
    run_sex.font.bold = True
    run_sex.font.size = Pt(10)
    run_sex.font.name = 'Arial Narrow'

    p.add_run('Informar a Interseguro Compañía de Seguros S.A. que puede acceder a los nueve (9) documentos presentados por la señora Eufemia Estefa Martínez Moreno de Romero, el cual se encontraba contenido en el USB adjuntado en su escrito del 19 de marzo de 2026, a través del siguiente link: https://indecopi-my.sharepoint.com/:f:/g/personal/apoyocc1e_indecopi_gob_pe/IgAb_utLXVuqTrZLA0y55DX2AdE_J2t0LXA_hW4jKzC8ANM?e=yi6ZyY, cuyo acceso tiene vigencia hasta el 3 de junio de 2026; dejándose a salvo su derecho de solicitar una nueva habilitación del link después de vencido el plazo señalado.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # SÉTIMO
    p = doc.add_paragraph()
    run_set = p.add_run('SÉTIMO: ')
    run_set.font.bold = True
    run_set.font.size = Pt(10)
    run_set.font.name = 'Arial Narrow'

    p.add_run('informar a las partes que el artículo 110° de la Ley N° 29571, Código de Protección y Defensa del Consumidor')

    run_nota_7 = p.add_run('7')
    run_nota_7.font.superscript = True
    run_nota_7.font.size = Pt(8)

    p.add_run(', faculta a la Comisión a calificar las infracciones de la referida norma como leves, graves o muy graves e imponer sanciones que van desde una amonestación hasta una multa por un máximo de 450 Unidades Impositivas Tributarias, sin perjuicio de las medidas correctivas, reparadoras y complementarias, que puedan ordenarse de acuerdo a lo estipulado en los artículos 114°, 115° y 116° de la referida norma')

    run_nota_8 = p.add_run('8')
    run_nota_8.font.superscript = True
    run_nota_8.font.size = Pt(8)

    p.add_run('. Asimismo, se consideran circunstancias atenuantes para la graduación de la sanción, el allanamiento de la denuncia o el reconocimiento de las pretensiones en ella contenidas, de acuerdo con el artículo 112° del Código')

    run_nota_9 = p.add_run('9')
    run_nota_9.font.superscript = True
    run_nota_9.font.size = Pt(8)

    p.add_run('.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        if not run.font.superscript:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # PAGE BREAK página 4
    doc.add_page_break()
    agregar_encabezado()

    # OCTAVO
    p = doc.add_paragraph()
    run_oct = p.add_run('OCTAVO: ')
    run_oct.font.bold = True
    run_oct.font.size = Pt(10)
    run_oct.font.name = 'Arial Narrow'

    p.add_run('informar a las partes que conforme a lo establecido en el artículo 39° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, los gastos por los peritajes realizados, actuación de pruebas, inspecciones y otros derivados de la tramitación del proceso serán de cargo de la parte que solicita la prueba, salvo pacto en contrario. En todos los casos, la resolución final determinará si los gastos deben ser asumidos por alguna de las partes, o reembolsados a la otra parte o al Indecopi, según sea el caso, de manera adicional a la sanción que haya podido imponerse.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # NOVENO
    p = doc.add_paragraph()
    run_nov = p.add_run('NOVENO: ')
    run_nov.font.bold = True
    run_nov.font.size = Pt(10)
    run_nov.font.name = 'Arial Narrow'

    p.add_run('comunicar a las partes que, de acuerdo a lo señalado por el artículo 29° del Decreto Legislativo N° 807')

    run_nota_10 = p.add_run('10')
    run_nota_10.font.superscript = True
    run_nota_10.font.size = Pt(8)

    p.add_run(', hasta antes de la emisión de la Resolución Final tienen la posibilidad de solicitar una audiencia de conciliación. En caso deleguen a favor de una tercera persona su actuación en la diligencia programada, ésta deberá presentar un poder especial con firma legalizada ante Notario Público, donde conste expresamente su facultad para asistir y conciliar en su representación. Ello bajo apercibimiento de no realizar la audiencia de conciliación y levantar el acta de inasistencia correspondiente.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        if not run.font.superscript:
            run.font.size = Pt(10)
            run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # DÉCIMO
    p = doc.add_paragraph()
    run_dec = p.add_run('DÉCIMO: ')
    run_dec.font.bold = True
    run_dec.font.size = Pt(10)
    run_dec.font.name = 'Arial Narrow'

    p.add_run('poner en conocimiento de las partes que, antes de la emisión de la Resolución Final, tienen la posibilidad de formular su desistimiento o presentar el acuerdo arribado mediante la conciliación, mediación, transacción o cualquier otro que, de forma indubitable, deje constancia que se ha solucionado la controversia materia de denuncia.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # DÉCIMO PRIMERO
    p = doc.add_paragraph()
    run_dp = p.add_run('DÉCIMO PRIMERO: ')
    run_dp.font.bold = True
    run_dp.font.size = Pt(10)
    run_dp.font.name = 'Arial Narrow'

    p.add_run('requerir a la señora Eufemia Estefa Martínez Moreno de Romero para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba la notificación en su bandeja de correo electrónico, efectúe la confirmación de recepción de la notificación remitida por este despacho a su correo electrónico, de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo 006-2026-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle conforme al numeral 1 del artículo 20° del citado cuerpo normativo.')

    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.0
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = 'Arial Narrow'
    set_space_after_paragraph(p, 6)

    # PAGE BREAK página 5
    doc.add_page_break()
    agregar_encabezado()

    # NOTAS AL PIE - Página 5+
    p = doc.add_paragraph()
    run = p.add_run('5 El número de trabajadores se atenderá siempre que la empresa haya sido constituida antes de la vigencia de la Ley Nº 30056, publicada el 2 de julio de 2013, que modificó el artículo 5 del Texto Único Ordenado de la Ley de Promoción de la Competitividad, Formalización y Desarrollo de la Micro y Pequeña Empresa y de Acceso al Empleo Decente (LEY MYPE). Ello, en la medida que la Tercera Disposición Complementaria Transitoria de la norma modificatoria precisa que las empresas constituidas antes de la entrada en vigencia de dicha Ley se rigen por los requisitos de acogimiento al régimen de las micro y pequeñas empresas regulados en el Decreto Legislativo 1086.')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True
    set_space_after_paragraph(p, 6)

    # Más notas
    p = doc.add_paragraph()
    run = p.add_run('6 LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 110.- Sanciones Administrativas\n(...)\nEn el caso de las microempresas, la multa no puede superar el diez por ciento (10%) de las ventas o ingresos brutos percibidos por el infractor, relativos a todas sus actividades económicas, correspondientes al ejercicio inmediato anterior al de la expedición de la resolución de primera instancia, siempre que se haya acreditado dichos ingresos, no se encuentre en una situación de reincidencia y el caso no verse sobre la vida, salud o integridad de los consumidores. Para el caso de las pequeñas empresas, la multa no puede superar el veinte por ciento (20%) de las ventas o ingresos brutos percibidos por el infractor, conforme a los requisitos señalados anteriormente.\n(…).')
    run.font.size = Pt(8)
    run.font.name = 'Arial Narrow'
    run.italic = True
    set_space_after_paragraph(p, 6)

    # Guardar documento
    output_path = Path(r'D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por claude\ADM_0955-2026_R1.docx')
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc.save(str(output_path))

    return output_path


if __name__ == '__main__':
    try:
        path = crear_resolucion_955()
        print(f"[OK] Documento .docx creado:")
        print(f"  Archivo: {path.name}")
        print(f"  Tamanio: {path.stat().st_size} bytes")
        print(f"  Paginas: 6 (aproximado)")
        print(f"  Expediente: 0955-2026/CC1")
        print(f"  Denunciante: Eufemia Estefa Martinez Moreno de Romero")
        print(f"  Denunciado: Interseguro Compania de Seguros S.A.")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
