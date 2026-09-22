import os
import re
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.text import WD_TAB_ALIGNMENT
from formato_nucleo import add_paragraph, add_run, add_blank, add_meta
from aplicar_reglas_base import aplicar_reglas_base

def main():
    template_path = os.path.abspath(r"D:\BETTER CALL DAVID\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx")
    doc = Document(template_path)
    
    # Clear the body
    for p in doc.paragraphs:
        p._element.getparent().remove(p._element)
    for t in doc.tables:
        t._element.getparent().remove(t._element)
        
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial Narrow'
    font.size = Pt(11)

    # Header (Regla 55: encabezado CC1)
    add_header_txt = ("SECRETAR\u00cdA T\u00c9CNICA DE LA\n"
                      "COMISI\u00d3N DE PROTECCI\u00d3N AL CONSUMIDOR 1\n"
                      "SEDE CENTRAL")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf = p.paragraph_format
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)
    run = p.add_run(add_header_txt)
    run.font.name = 'Arial Narrow'
    run.font.size = Pt(11)
    run.bold = True
    run.italic = True
    
    add_blank(doc)

    # Metadata (Regla 54: sangr\u00eda colgante 1.48")
    add_meta(doc, "EXPEDIENTE\t:\t", "0955-2026/CC1")
    add_meta(doc, "DENUNCIANTE\t:\t", "EUFEMIA ESTEFA MART\u00cdNEZ MORENO DE ROMERO (SE\u00d1ORA MART\u00cdNEZ)")
    add_meta(doc, "DENUNCIADO\t:\t", "INTERSEGURO COMPA\u00d1\u00cdA DE SEGUROS S.A. (INTERSEGURO)")
    add_meta(doc, "MATERIAS\t:\t", "ADMISI\u00d3N A TR\u00c1MITE\n\t\tREQUERIMIENTO DE INFORMACI\u00d3N")
    add_meta(doc, "RESOLUCI\u00d3N\t:\t", "1")

    add_blank(doc)
    add_paragraph(doc, "Lima, 20 de abril de 2026", align=WD_ALIGN_PARAGRAPH.LEFT)
    add_blank(doc)
    
    # Roman numeral indent: Left indent 0.39 inches, first line -0.39 inches
    roman_indent = Inches(0.39)
    roman_hanging = Inches(-0.39)
    
    # Number indent: same as roman
    num_indent = Inches(0.39)
    num_hanging = Inches(-0.39)
    
    # List indent: Left indent 0.79 inches, first line -0.39 inches
    list_indent = Inches(0.79)
    list_hanging = Inches(-0.39)
    
    add_paragraph(doc, "I.\tHECHOS", bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left_indent=roman_indent, hanging_indent=roman_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "1.\tMediante el escrito del 19 de marzo de 2026, la señora Martínez denunció a Interseguro por presuntas infracciones a la Ley N°29571, Código de Protección y Defensa del Consumidor (en adelante, Código)__F1__, señalando lo siguiente:", left_indent=num_indent, hanging_indent=num_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "(i)\tEl 10 de setiembre de 2024, inició la vigencia del Seguro de Vida – Póliza N°1760006823 (en adelante, Seguro de Vida), adquirido por su hijo de iniciales L.M.R. (en adelante, asegurado), en el cual se le consignó en calidad de única beneficiaria.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "(ii)\tEl 23 de marzo de 2025, el asegurado perdió la vida en circunstancias vinculadas a su abandono en la vía pública por parte del conductor de un vehículo de transporte público no identificado, sin que se haya determinado la identidad del responsable ni del vehículo involucrado.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "(iii)\tEl 24 de abril de 2025, se emitió el Informe Policial N°562-2025-REG.POL-LIMA/DIVPOL-CHO-DEPINCRI-CHOSICA, en el cual se dejó constancia de las circunstancias del fallecimiento del asegurado, incluyendo su abandono en la vía pública y la falta de identificación del responsable.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "(iv)\tPosteriormente, conforme a las pericias y al certificado de necropsia, se determinó que el asegurado se encontraba bajo los efectos del alcohol al momento de su fallecimiento, estableciéndose como causa de muerte un paro cardíaco asociado a edema cerebral y daño pulmonar severo por asfixia, sin haberse precisado la causa inicial del deceso.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "(v)\tEl 8 de septiembre de 2025, Interseguro emitió la carta N°GOT-SIN-90852-2025, mediante la cual comunicó la denegatoria de su solicitud de cobertura del Seguro de Vida, señalando que el fallecimiento del asegurado se encontraba comprendido dentro de un supuesto de exclusión por estado de ebriedad, motivo por el cual le rechazó el pago del monto asegurado en su calidad de única beneficiaria.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "2.\tLa señora Martínez solicitó, en calidad de medida correctiva, que Interseguro cumpla con otorgar la cobertura del Seguro de Desgravamen y otorgar el pago de los daños y perjuicios ocasionados. Asimismo, no requirió de manera expresa el reembolso de costos y costas del presente procedimiento.", left_indent=num_indent, hanging_indent=num_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "II.\tDE LA ADMISIÓN A TRÁMITE DE LA DENUNCIA", bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left_indent=roman_indent, hanging_indent=roman_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "3.\tLa Secretaría Técnica de la Comisión de Protección al Consumidor N°1 (en adelante, la Secretaría Técnica), en ejercicio de sus facultades__F2__, considera que el hecho denunciado, consistente en que la compañía aseguradora habría negado injustificadamente al denunciante, mediante la carta N°GOT-SIN-90852-2025, la cobertura de la Póliza N°1760006823 del Seguro de Vida; involucraría una presunta afectación a sus expectativas, quien no habría encontrado una correspondencia entre lo que esperaba recibir de parte del proveedor y lo que realmente recibió. Por consiguiente, corresponde calificar el hecho materia de denuncia como una presunta infracción al deber de idoneidad, tipificado en los artículos 18° y 19° del Código__F3__.", left_indent=num_indent, hanging_indent=num_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "4.\tEn tanto la denuncia reúne los requisitos establecidos por la norma citada, corresponde admitirla a trámite__F4__.", left_indent=num_indent, hanging_indent=num_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "III.\tREQUERIMIENTO DE INFORMACIÓN", bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left_indent=roman_indent, hanging_indent=roman_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "5.\tA efectos de tener mayores elementos que sirvan para la resolución definitiva del presente caso, la Secretaría Técnica, en ejercicio de las facultades que la ley le confiere, conviene requerir a la compañía aseguradora que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, cumpla con lo siguiente: (i) presentar una copia completa, legible y debidamente suscrita de la Póliza N°1760006823 - Seguro de Vida, así como el cargo de remisión de la póliza; (ii) presentar los medios probatorios que acrediten que la negativa de otorgamiento de cobertura fue justificada; y, (iii) presentar todas las comunicaciones cursadas con la parte denunciante en virtud de los hechos materia de denuncia.", left_indent=num_indent, hanging_indent=num_hanging)
    add_blank(doc)
    
    add_paragraph(doc, "IV.\tRESOLUCIÓN DE LA SECRETARÍA TÉCNICA", bold=True, align=WD_ALIGN_PARAGRAPH.JUSTIFY, left_indent=roman_indent, hanging_indent=roman_hanging)
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "PRIMERO: ", bold=True)
    add_run(p, "admitir a trámite la denuncia del 19 de marzo de 2026 interpuesta por la señora Eufemia Estefa Martínez Moreno de Romero contra Interseguro Compañía de Seguros S.A., por la presunta infracción a los artículos 18° y 19° de la Ley N° 29571, Código de Protección y Defensa del Consumidor, en tanto la compañía aseguradora habría negado injustificadamente al denunciante, mediante la carta N°GOT-SIN-90852-2025, la cobertura de la Póliza N°1760006823 del Seguro de Vida.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "SEGUNDO: ", bold=True)
    add_run(p, "tener por ofrecidos los medios probatorios presentados en el escrito de denuncia del 19 de marzo de 2026.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "TERCERO: ", bold=True)
    add_run(p, "requerir a Interseguro Compañía de Seguros S.A. que cumpla con lo siguiente:")
    add_blank(doc)
    
    add_paragraph(doc, "(i)\tpresentar documentos que acrediten su inscripción en los Registros Públicos o una declaración jurada que indique que cuenta con dicha inscripción;", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    add_paragraph(doc, "(ii)\tpresentar copia simple de las facultades de representación de su representante legal en el presente procedimiento o la declaración jurada que indique que cuenta con dichas facultades y que estas se encuentran vigentes;", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    add_paragraph(doc, "(iii)\tconsignar el Número de Registro Único de Contribuyentes (RUC); y,", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    add_paragraph(doc, "(iv)\tfijar domicilio procesal para el procedimiento, de conformidad con el numeral 1 del artículo 442° del Código Procesal Civil. Para ello podrá señalar domicilio físico o una dirección electrónica a la que pueda remitirse las notificaciones;", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    add_paragraph(doc, "(v)\ten caso califique como micro empresa o pequeña empresa, presentar los documentos que acrediten su volumen de ventas o ingresos brutos percibidos el año anterior relativo a todas sus actividades económicas y el número de trabajadores con el que cuenta__F5__. Ello, a fin de que la Comisión pueda meritar dicha documentación, conforme lo establece el artículo 110° del Código__F6__.", left_indent=list_indent, hanging_indent=list_hanging)
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "CUARTO: ", bold=True)
    add_run(p, "correr traslado de la presente resolución a Interseguro Compañía de Seguros S.A. para que, de conformidad con lo dispuesto por el artículo 26° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobado por Decreto Legislativo N° 8079, presente sus descargos sobre la imputación de cargos realizada en un plazo no mayor a cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, vencido el cual, el Secretario Técnico declarará en rebeldía a los denunciados que no lo hubieran presentado. Debe precisarse que de conformidad con lo establecido por el artículo 223° del Texto Único Ordenado de la Ley N° 27444, Ley del Procedimiento Administrativo General, las alegaciones y los hechos relevantes de la reclamación, salvo que hayan sido específicamente negadas en la contestación, se tendrán por aceptadas o meritadas como ciertas.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "QUINTO: ", bold=True)
    add_run(p, "requerir que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, el proveedor denunciado cumpla con: (i) presentar una copia completa, legible y debidamente suscrita de la Póliza N°1760006823 del Seguro de Vida, así como el cargo de remisión de la póliza; (ii) presentar los medios probatorios que acrediten que la negativa de otorgamiento de cobertura fue justificada; y, (iii) presentar todas las comunicaciones cursadas con la parte denunciante en virtud de los hechos materia de denuncia.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "SEXTO: ", bold=True)
    add_run(p, "Informar a Interseguro Compañía de Seguros S.A. que puede acceder a los nueve (9) documentos presentados por la señora Eufemia Estefa Martínez Moreno de Romero, el cual se encontraba contenido en el USB adjuntado en su escrito del 19 de marzo de 2026, a través del siguiente link: ")
    link = add_run(p, "https://indecopi-my.sharepoint.com/:f:/g/personal/apoyocc1e_indecopi_gob_pe/IgAb_utLXVuqTrZLA0y55DX2AdE_J2t0LXA_hW4jKzC8ANM?e=yi6ZyY", underline=True)
    from docx.shared import RGBColor
    link.font.color.rgb = RGBColor(0, 0, 255) # Blue link
    add_run(p, ", cuyo acceso tiene vigencia hasta el 3 de junio de 2026; dejándose a salvo su derecho de solicitar una nueva habilitación del link después de vencido el plazo señalado.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "SÉTIMO: ", bold=True)
    add_run(p, "informar a las partes que el artículo 110° de la Ley N° 29571, Código de Protección y Defensa del Consumidor__F7__, faculta a la Comisión a calificar las infracciones de la referida norma como leves, graves o muy graves e imponer sanciones que van desde una amonestación hasta una multa por un máximo de 450 Unidades Impositivas Tributarias, sin perjuicio de las medidas correctivas, reparadoras y complementarias, que puedan ordenarse de acuerdo a lo estipulado en los artículos 114°, 115° y 116° de la referida norma__F8__. Asimismo, se consideran circunstancias atenuantes para la graduación de la sanción, el allanamiento de la denuncia o el reconocimiento de las pretensiones en ella contenidas, de acuerdo con el artículo 112° del Código__F9__.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "OCTAVO: ", bold=True)
    add_run(p, "informar a las partes que conforme a lo establecido en el artículo 39° de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, los gastos por los peritajes realizados, actuación de pruebas, inspecciones y otros derivados de la tramitación del proceso serán de cargo de la parte que solicita la prueba, salvo pacto en contrario. En todos los casos, la resolución final determinará si los gastos deben ser asumidos por alguna de las partes, o reembolsados a la otra parte o al Indecopi, según sea el caso, de manera adicional a la sanción que haya podido imponerse.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "NOVENO: ", bold=True)
    add_run(p, "comunicar a las partes que, de acuerdo a lo señalado por el artículo 29° del Decreto Legislativo N° 807__F10__, hasta antes de la emisión de la Resolución Final tienen la posibilidad de solicitar una audiencia de conciliación. En caso deleguen a favor de una tercera persona su actuación en la diligencia programada, ésta deberá presentar un poder especial con firma legalizada ante Notario Público, ")
    add_run(p, "donde conste expresamente su facultad para asistir y conciliar en su representación. Ello bajo apercibimiento de no realizar la audiencia de conciliación y levantar el acta de inasistencia correspondiente.", underline=True)
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "DÉCIMO: ", bold=True)
    add_run(p, "poner en conocimiento de las partes que, antes de la emisión de la Resolución Final, tienen la posibilidad de formular su desistimiento o presentar el acuerdo arribado mediante la conciliación, mediación, transacción o cualquier otro que, de forma indubitable, deje constancia que se ha solucionado la controversia materia de denuncia.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "DÉCIMO PRIMERO: ", bold=True)
    add_run(p, "requerir a la señora Eufemia Estefa Martínez Moreno de Romero para que, dentro del plazo de dos (2) días hábiles siguientes a la fecha en que reciba la notificación en su bandeja de correo electrónico, efectúe la confirmación de recepción de la notificación remitida por este despacho a su correo electrónico, de conformidad con el segundo párrafo del numeral 4 del artículo 20° del Texto Único Ordenado de la Ley del Procedimiento Administrativo General, aprobado mediante Decreto Supremo N° 004-2019-JUS, bajo apercibimiento de rehacer el acto de notificación y notificarle conforme al numeral 1 del artículo 20° del citado cuerpo normativo__F11__.")
    add_blank(doc)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "DÉCIMO SEGUNDO: ", bold=True)
    add_run(p, "requerir a Interseguro Compañía de Seguros S.A. para que efectúe el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su Casilla Electrónica, dentro de los cinco (5) primeros días hábiles siguientes a la fecha en que recibe la notificación.")
    
    add_blank(doc)
    add_blank(doc)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    add_run(p, "Firmado digitalmente por\nEVELING ROA QUISPE\nSecretaria Técnica\nComisión de Protección al Consumidor N°1", bold=True)
    
    from formato_nucleo import TAMANO_INICIALES
    p_ini = doc.add_paragraph()
    p_ini.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_ini.paragraph_format.space_before = Pt(0)
    p_ini.paragraph_format.space_after = Pt(0)
    r_ini = p_ini.add_run("LGP/JCQ")
    r_ini.font.name = "Arial Narrow"
    r_ini.font.size = TAMANO_INICIALES
    
    # Aplicar reglas base CC1 antes de guardar
    aplicar_reglas_base(doc)
    
    temp_path = os.path.abspath(r"D:\BETTER CALL DAVID\ResAdmi\temp_v7.docx")
    doc.save(temp_path)
    
    # Now use win32com to add footnotes
    import win32com.client
    
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    doc_com = word.Documents.Open(temp_path)
    
    footnotes_data = {
        "__F1__": "Publicado el 2 de setiembre del 2010 en el Diario Oficial El Peruano, vigente desde el 2 de octubre del 2010 y modificado por Decreto Legislativo 1308.",
        "__F2__": "<b>LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 105.- Autoridad competente.</b>\nEl Instituto Nacional de Defensa de la Competencia y de la Protección de la Propiedad Intelectual (Indecopi) es la autoridad con competencia primaria y de alcance nacional para conocer las presuntas infracciones a las disposiciones contenidas en el presente Código, así como para imponer las sanciones y medidas correctivas establecidas en el presente capítulo, conforme al Decreto Legislativo N° 1033, Ley de Organización y Funciones del Indecopi. Dicha competencia solo puede ser negada cuando ella haya sido asignada o se asigne a favor de otro organismo por norma expresa con rango de ley.\n(...).\n\n<b>LEY DE ORGANIZACIÓN Y FUNCIONES DEL INDECOPI, APROBADA POR DECRETO LEGISLATIVO N° 1033\nArtículo 27.-</b> De la Comisión de Protección al Consumidor.-\nCorresponde a la Comisión de Protección al Consumidor velar por el cumplimiento de la Ley de Protección al Consumidor y de las leyes que, en general, protegen a los consumidores de la falta de idoneidad de los bienes y servicios en función de la información brindada, de las omisiones de información y de la discriminación en el consumo, así como de aquellas que complementen o sustituyan a las anteriores.",
        "__F3__": "<b>LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 18.- Idoneidad</b>\nSe entiende por idoneidad la correspondencia entre lo que un consumidor espera y lo que efectivamente recibe, en función a lo que se le hubiera ofrecido, la publicidad e información transmitida, las condiciones y circunstancias de la transacción, las características y naturaleza del producto o servicio, el precio, entre otros factores, atendiendo a las circunstancias del caso.\nLa idoneidad es evaluada en función a la propia naturaleza del producto o servicio y a su aptitud para satisfacer la finalidad para la cual ha sido puesto en el mercado. Las autorizaciones por parte de los organismos del Estado para la fabricación de un producto o la prestación de un servicio, en los casos que sea necesario, no eximen de responsabilidad al proveedor frente al consumidor.\n\n<b>Artículo 19.- Obligación de los proveedores</b>\nEl proveedor responde por la idoneidad y calidad de los productos y servicios ofrecidos; por la autenticidad de las marcas y leyendas que exhiben sus productos o del signo que respalda al prestador del servicio, por la falta de conformidad entre la publicidad comercial de los productos y servicios y éstos, así como por el contenido y la vida útil del producto indicado en el envase, en lo que corresponda.",
        "__F4__": "<b>LEY SOBRE FACULTADES, NORMAS Y ORGANIZACIÓN DEL INDECOPI, APROBADA POR DECRETO LEGISLATIVO N° 807\nArtículo 24.-</b> El Secretario Técnico se encargará de la tramitación del procedimiento. Para ello, cuenta con las siguientes facultades:\n(...)\nc) Admitir denuncias a trámite, en aquellos casos en que la Comisión le haya delegado esta facultad.\n(...).",
        "__F5__": "El número de trabajadores se atenderá siempre que la empresa haya sido constituida antes de la vigencia de la Ley Nº 30056, publicada el 2 de julio de 2013, que modificó el artículo 5 del Texto Único Ordenado de la Ley de Promoción de la Competitividad, Formalización y Desarrollo de la Micro y Pequeña Empresa y de Acceso al Empleo Decente (LEY MYPE). Ello, en la medida que la Tercera Disposición Complementaria Transitoria de la norma modificatoria precisa que las empresas constituidas antes de la entrada en vigencia de dicha Ley se rigen por los requisitos de acogimiento al régimen de las micro y pequeñas empresas regulados en el Decreto Legislativo 1086.",
        "__F6__": "<b>LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 110.- Sanciones Administrativas</b>\n(...)\nEn el caso de las microempresas, la multa no puede superar el diez por ciento (10%) de las ventas o ingresos brutos percibidos por el infractor, relativos a todas sus actividades económicas, correspondientes al ejercicio inmediato anterior al de la expedición de la resolución de primera instancia, siempre que se haya acreditado dichos ingresos, no se encuentre en una situación de reincidencia y el caso no verse sobre la vida, salud o integridad de los consumidores. Para el caso de las pequeñas empresas, la multa no puede superar el veinte por ciento (20%) de las ventas o ingresos brutos percibidos por el infractor, conforme a los requisitos señalados anteriormente.\n(...).",
        "__F7__": "<b>LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 110.- Sanciones administrativas</b>\nEl órgano resolutivo puede sancionar las infracciones administrativas a que se refiere el artículo 108º con amonestación y multas de hasta cuatrocientos cincuenta (450) Unidades Impositivas Tributarias (UIT), las cuales son calificadas de la siguiente manera:\na. Infracciones leves, con una amonestación o con una multa de hasta cincuenta (50) UIT.\nb. Infracciones graves, con una multa de hasta ciento cincuenta (150) UIT.\nc. Infracciones muy graves, con una multa de hasta cuatrocientos cincuenta (450) UIT.\n(...).",
        "__F8__": "<b>Artículo 114.- Medidas correctivas</b>\nSin perjuicio de la sanción administrativa que corresponda al proveedor por una infracción al presente Código, el Indecopi puede dictar, en calidad de mandatos, medidas correctivas reparadoras y complementarias.\nLas medidas correctivas reparadoras pueden dictarse a pedido de parte o de oficio, siempre y cuando sean expresamente informadas sobre esa posibilidad en la notificación de cargo al proveedor por la autoridad encargada del procedimiento.\nLas medidas correctivas complementarias pueden dictarse de oficio o a pedido de parte.\n\n<b>Artículo 115.- Medidas correctivas reparadoras</b>\n115.1 Las medidas correctivas reparadoras tienen el objeto de resarcir las consecuencias patrimoniales directas e inmediatas ocasionadas al consumidor por la infracción administrativa a su estado anterior. En caso el órgano resolutivo dicte una o varias medidas correctivas, debe considerar lo acordado por las partes durante la relación de consumo. Las medidas correctivas reparadoras pueden consistir en ordenar al proveedor infractor lo siguiente:\na. Reparar productos.\nb. Cambiar productos por otros de idénticas o similares características, cuando la reparación no sea posible o no resulte razonable según las circunstancias.\nc. Entregar un producto de idénticas características o, cuando esto no resulte posible, de similares características, en los supuestos de pérdida o deterioro atribuible al proveedor y siempre que exista interés del consumidor.\nd. Cumplir con ejecutar la prestación u obligación asumida; y si esto no resulte posible o no sea razonable, otra de efectos equivalentes, incluyendo prestaciones dinerarias.\ne. Cumplir con ejecutar otras prestaciones u obligaciones legales o convencionales a su cargo.\nf. Devolver la contraprestación pagada por el consumidor, más los intereses legales correspondientes, cuando la reparación, reposición, o cumplimiento de la prestación u obligación, según sea el caso, no resulte posible o no sea razonable según las circunstancias.\ng. En los supuestos de pagos indebidos o en exceso, devolver estos montos, más los intereses correspondientes.\nPagar los gastos incurridos por el consumidor para mitigar las consecuencias de la infracción administrativa.\nOtras medidas reparadoras análogas de efectos equivalentes a las anteriores.\n\n115.2 Las medidas correctivas reparadoras no pueden ser solicitadas de manera acumulativa conjunta, pudiendo plantearse de manera alternativa o subsidiaria, con excepción de la medida correctiva señalada en el literal h) que puede solicitarse conjuntamente con otra medida correctiva. Cuando los órganos competentes del Indecopi se pronuncian respecto de una medida correctiva reparadora, aplican el principio de congruencia procesal.\n115.3 Las medidas correctivas reparadoras pueden solicitarse en cualquier momento hasta antes de la notificación de cargo al proveedor, sin perjuicio de la facultad de secretaría técnica de la comisión de requerir al consumidor que precise la medida correctiva materia de solicitud. El consumidor puede variar su solicitud de medida correctiva hasta antes de la decisión de primera instancia, en cuyo caso se confiere traslado al proveedor para que formule su descargo.\n115.4 Corresponde al consumidor que solicita el dictado de la medida correctiva reparadora probar las consecuencias patrimoniales directas e inmediatas causadas por la comisión de la infracción administrativa.\n115.5 Los bienes o montos objeto de medidas correctivas reparadoras son entregados por el proveedor directamente al consumidor que los reclama, salvo mandato distinto contenido en la resolución. Aquellos bienes o montos materia de una medida correctiva reparadora, que por algún motivo se encuentran en posesión del Indecopi y deban ser entregados a los consumidores beneficiados, son puestos a disposición de estos.\n115.6 El extremo de la resolución final que ordena el cumplimiento de una medida correctiva reparadora a favor del consumidor constituye título ejecutivo conforme con lo dispuesto en el artículo 688 del Código Procesal Civil, una vez que quedan consentidas o causan estado en la vía administrativa. La legitimidad para obrar en los procesos civiles de ejecución corresponde a los consumidores beneficiados con la medida correctiva reparadora.\n115.7 Las medidas correctivas reparadoras como mandatos dirigidos a resarcir las consecuencias patrimoniales directas e inmediatas originadas por la infracción buscan corregir la conducta infractora y no tienen naturaleza indemnizatoria; son dictadas sin perjuicio de la indemnización por los daños y perjuicios que el consumidor puede solicitar en la vía judicial o arbitral correspondiente. No obstante, se descuenta de la indemnización patrimonial aquella satisfacción patrimonial deducible que el consumidor haya recibido a consecuencia del dictado de una medida correctiva reparadora en sede administrativa.\n\n<b>Artículo 116.- Medidas correctivas complementarias</b>\nLas medidas correctivas complementarias tienen el objeto de revertir los efectos de la conducta infractora o evitar que esta se produzca nuevamente en el futuro y pueden ser, entre otras, las siguientes:\na. Que el proveedor cumpla con atender la solicitud de información requerida por el consumidor, siempre que dicho requerimiento guarde relación con el producto adquirido o servicio contratado.\nb. Declarar inexigibles las cláusulas que han sido identificadas como abusivas en el procedimiento.\nc. El decomiso y destrucción de la mercadería, envases, envolturas o etiquetas.\nd. En caso de infracciones muy graves y de reincidencia o reiterancia:\n(i) Solicitar a la autoridad correspondiente la clausura temporal del establecimiento industrial, comercial o de servicios por un plazo máximo de seis (6) meses.\n(ii) Solicitar a la autoridad competente la inhabilitación, temporal o permanente, del proveedor en función de los alcances de la infracción sancionada.\ne. Publicación de avisos rectificatorios o informativos en la forma que determine el Indecopi, tomando en consideración los medios que resulten idóneos para revertir los efectos que el acto objeto de sanción ha ocasionado.\nf. Cualquier otra medida correctiva que tenga el objeto de revertir los efectos de la conducta infractora o evitar que esta se produzca nuevamente en el futuro.\nEl Indecopi está facultado para solicitar a la autoridad municipal y policial el apoyo respectivo para la ejecución de las medidas correctivas complementarias correspondientes.",
        "__F9__": "<b>LEY N° 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicado el 2 de setiembre de 2010 y modificado por Decreto Legislativo N° 1308\nArtículo 112.- Criterios de graduación de las sanciones administrativas</b>\n(...)\nSe consideran circunstancias atenuantes especiales, las siguientes:\n(...)\n3. En los procedimientos de oficio promovidos por una denuncia de parte, cuando el proveedor se allana a la denuncia presentada o reconoce las pretensiones en ella contenidas, se da por concluido el procedimiento liminarmente, pudiendo imponerse una amonestación si el allanamiento o reconocimiento se realiza con la presentación de los descargos; caso contrario la sanción a imponer será pecuniaria. En aquellos casos en que el allanamiento o reconocimiento verse sobre controversias referidas a actos de discriminación, actos contrarios a la vida y a la salud y sustancias peligrosas, se considera como un atenuante pero la sanción a imponer será pecuniaria. En todos los supuestos de allanamiento y reconocimiento formulados con la presentación de los descargos, se exonera al denunciado del pago de los costos del procedimiento, pero no de las costas.",
        "__F10__": "<b>DECRETO LEGISLATIVO Nº 807, LEY SOBRE FACULTADES, NORMAS Y ORGANIZACIÓN DEL INDECOPI FACULTADES DE LAS COMISIONES Y OFICINAS DEL INDECOPI\nArtículo 29.-</b> En cualquier estado del procedimiento, e incluso antes de admitirse a trámite la denuncia, el Secretario Técnico podrá citar a las partes a audiencia de conciliación. La audiencia se desarrollará ante el Secretario Técnico o ante la persona que éste designe. Si ambas partes arribaran a un acuerdo respecto de la denuncia, se levantará un acta donde conste el acuerdo respectivo, el mismo que tendrá efectos de transacción extrajudicial. En cualquier caso, la Comisión podrá continuar de oficio el procedimiento, si del análisis de los hechos denunciados considera que podría estarse afectando intereses de terceros.",
        "__F11__": "<b>TEXTO ÚNICO ORDENADO DE LA LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL, aprobado mediante DECRETO SUPREMO N° 004-2019-JUS y publicado el 25 de enero de 2019\nArtículo 20.- Modalidades de notificación</b>\n20.4. El administrado interesado o afectado por el acto que hubiera consignado en su escrito alguna dirección electrónica que conste en el expediente puede ser notificado a través de ese medio siempre que haya dado su autorización expresa para ello. Para este caso no es de aplicación el orden de prelación dispuesto en el numeral 20.1.\nLa notificación dirigida a la dirección de correo electrónico señalada por el administrado se entiende válidamente efectuada cuando la entidad reciba la respuesta de recepción de la dirección electrónica señalada por el administrado o esta sea generada en forma automática por una plataforma tecnológica o sistema informático que garantice que la notificación ha sido efectuada. La notificación surte efectos el día que conste haber sido recibida, conforme lo previsto en el numeral 2 del artículo 25.\nEn caso de no recibirse respuesta automática de recepción en un plazo máximo de dos (2) días hábiles contados desde el día siguiente de efectuado el acto de notificación vía correo electrónico, se procede a notificar por cédula conforme al inciso 20.1.1, volviéndose a computar el plazo establecido en el numeral 24.1 del artículo 24."
    }
    
    import docx
    
    for key, footnote_text in footnotes_data.items():
        rng = doc_com.Content
        if rng.Find.Execute(FindText=key):
            rng.Text = "" # Erase the placeholder
            fn = doc_com.Footnotes.Add(Range=rng, Text="")
            
            parts = re.split(r'(<b>.*?</b>)', footnote_text, flags=re.DOTALL)
            insert_rng = fn.Range
            insert_rng.Collapse(1) # Collapse to start
            for part in parts:
                if not part: continue
                is_bold = False
                if part.startswith('<b>') and part.endswith('</b>'):
                    text = part[3:-4]
                    is_bold = True
                else:
                    text = part
                
                insert_rng.Text = text
                insert_rng.Font.Bold = is_bold
                insert_rng.Collapse(0) # wdCollapseEnd = 0
                
    from formato_nucleo import FUENTE_NOTAS, TAMANO_NOTAS
    for fn in doc_com.Footnotes:
        fn.Range.Font.Name = FUENTE_NOTAS
        fn.Range.Font.Size = TAMANO_NOTAS.pt
        fn.Range.ParagraphFormat.Alignment = 3 # justify

    out_dir = os.path.abspath(r"D:\BETTER CALL DAVID\ResAdmi\productos (resoluciones) elaborada por google antigravity")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_path = os.path.join(out_dir, "ADM 0955-2026.docx")
    doc_com.SaveAs(out_path)
    
    # Save a PDF as well to double check
    pdf_path = os.path.join(out_dir, "ADM 0955-2026.pdf")
    doc_com.ExportAsFixedFormat(pdf_path, 17) # 17 is wdExportFormatPDF
    
    doc_com.Close()
    word.Quit()
    print("Success V7")
    
    # Validar contra el validador universal
    try:
        from validador_universal import validar_documento
        valido, violaciones = validar_documento(out_path)
        if valido:
            print("\n\u2714 DOCUMENTO V\u00c1LIDO - Todas las reglas cumplidas")
        else:
            print("\n\u26a0 Documento con advertencias de formato")
    except Exception as e:
        print(f"  Validador no disponible: {e}")

if __name__ == '__main__':
    main()
