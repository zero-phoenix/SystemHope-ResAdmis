import docx
import re
doc = docx.Document(r'C:\Users\D\Code\repos\SystemHope-ResAdmis\plantillas_maestras\04_seguro_proteccion_tarjetas_y_dinero\negativa_cobertura\1_ddo_aseguradora\varon\TPL_2536_2025_SEGURO_PROTECCION_TARJETAS_Y_DINERO_NEGATIVA_COBERTURA_ASEGURADORA_VARON_R1.docx')
text = "\n".join([p.text for p in doc.paragraphs])
def check(s):
    if s in text:
        print(f"MATCH: {s[:50]}...")
    else:
        print(f"FAIL: {s[:50]}...")
check("Secretaria Técnica\nComisión de Protección al Consumidor 1\n\nLSM/JCQ")
check("Secretaria Técnica")
check("EVELING ROA QUISPE")
check("del Certificado  108059-1190614 de la póliza de seguro que cubre eventos de robo o fraude en operaciones bancarias")
check("del Certificado 108059-1190614 de la póliza de seguro que cubre eventos de robo o fraude en operaciones bancarias")
check("la compañía aseguradora se habría negado injustificadamente a otorgar al denunciante la cobertura del Certificado  108059-1190614 por las catorce (14) operaciones no reconocidas realizadas desde su cuenta de ahorros")
check("la compañía aseguradora se habría negado injustificadamente a otorgar al denunciante la cobertura del Certificado 108059-1190614 por las catorce (14) operaciones no reconocidas realizadas desde su cuenta de ahorros")
check("la compañía aseguradora no habría cumplido con brindar una respuesta dentro del plazo legal a la solicitud de cobertura del Certificado  108059-1190614 presentada por el denunciante por las catorce (14) operaciones no reconocidas realizadas desde su cuenta de ahorros")
check("la compañía aseguradora no habría cumplido con brindar una respuesta dentro del plazo legal a la solicitud de cobertura del Certificado 108059-1190614 presentada por el denunciante por las catorce (14) operaciones no reconocidas realizadas desde su cuenta de ahorros")
check("El señor Espinoza solicitó, en calidad de medida correctiva, que Interseguro cumpla con: (i) realizar la devolución del dinero correspondiente a las 14 operaciones fraudulentas, realizadas el 18 y 19 de octubre de 2024, por el total de S/28 049,00 más los intereses generados; (ii) otorgar la reparación integral por los siguientes conceptos: daño emergente por costos incurridos en trámites (por la suma estimada de S/ 8 000,00); lucro cesante por intereses por el tiempo transcurrido (por la suma aproximada de S/ 1 500,00); daño moral por indemnización por afectación emocional y descrédito; y daños contra su honra y honor (por la suma de S/ 10 000,00). Asimismo, requirió el reembolso de costos y costas del presente procedimiento.")
