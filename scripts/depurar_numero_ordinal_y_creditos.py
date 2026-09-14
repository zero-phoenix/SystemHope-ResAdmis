# -*- coding: utf-8 -*-
import re

def mask_number(num_str):
    """Preserves first 3 and last 3, replaces middle with xxxxxx."""
    digits = re.sub(r'[\s\-\*]', '', num_str)
    if len(digits) <= 6:
        return num_str
    return f"{digits[:3]}xxxxxx{digits[-3:]}"

def depurar_texto_xml(xml_content):
    """
    Depura contenido XML de un archivo DOCX:
    1. Reemplaza numeros de tarjetas y creditos por confidencialidad (ej 123xxxxxx879).
       NUNCA censura polizas ni certificados de seguro.
    2. Erradica totalmente 'N°', 'Nº', 'n°', 'nº' y los simbolos ordinales '°' y 'º'.
    """
    # Función que procesa el contenido interno de <w:t>...</w:t>
    def procesar_wt(match):
        attrs = match.group(1)
        text = match.group(2)
        
        # --- A. CENSURA DE CRÉDITOS Y TARJETAS (NUNCA PÓLIZAS NI CERTIFICADOS) ---
        # Excepciones que NUNCA deben censurarse:
        # Poliza, certificado, expediente, resolucion, ley, decreto, ruc, dni, placa, telefono.
        def repl_credit(m):
            prefix = m.group(1)
            num = m.group(2)
            # Validar que no sea poliza o certificado
            low_pre = prefix.lower()
            if any(k in low_pre for k in ['póliza', 'poliza', 'certificado', 'expediente', 'ley', 'decreto', 'resolución', 'resolucion', 'ruc', 'dni', 'placa']):
                return m.group(0)
            masked = mask_number(num)
            return f"{prefix}{masked}"

        # Detectar patrones de crédito / tarjeta / préstamo / cuenta
        text = re.sub(
            r'((?:crédito|credito|préstamo|prestamo|financiamiento|tarjeta|VTAR|cuenta)\s+(?:[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]{0,35})?(?:N[°ºo]\.?\s*)?)([0-9\-\*]{7,25})',
            repl_credit,
            text,
            flags=re.IGNORECASE
        )

        # --- B. ERRADICACIÓN DE 'N°', 'Nº', 'n°', 'nº' Y ORDINALES '°', 'º' ---
        # 1. Frases compuestas con N°
        text = re.sub(r'\bcon\s+N[°ºo]\.?\s+de\b', 'con número de', text, flags=re.IGNORECASE)
        text = re.sub(r'\bsin\s+N[°ºo]\.?\b', 'sin número', text, flags=re.IGNORECASE)
        
        # 2. Entidades con N°
        text = re.sub(r'\bComisión de Protección al Consumidor\s+N[°ºo]\.?\s*1\b', 'Comisión de Protección al Consumidor 1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bPlaca\s+(?:de\s+Rodaje\s+)?N[°ºo]\.?\s*', 'Placa de Rodaje ', text, flags=re.IGNORECASE)
        
        # 3. Eliminar N°/Nº pegado o separado de dígitos/códigos
        # ej: "Ley N° 29571" -> "Ley 29571", "Póliza N° 123" -> "Póliza 123", "N° 006-2026-JUS" -> "006-2026-JUS"
        text = re.sub(r'\bN[°ºo]\.?\s*([0-9A-Za-z\-_]+)', r'\1', text)
        text = re.sub(r'\bn[°ºo]\.?\s*([0-9A-Za-z\-_]+)', r'\1', text)
        
        # 4. Eliminar ordinales pegados a dígitos (ej. 19° -> 19, 108º -> 108, 1° -> 1)
        text = re.sub(r'(\d+)[°º]', r'\1', text)
        
        # 5. Cualquier otro N° o Nº remanente
        text = re.sub(r'N[°ºo]\.?', '', text)
        text = re.sub(r'n[°ºo]\.?', '', text)
        
        # 6. Cualquier '°' o 'º' suelto remanente
        text = text.replace('°', '').replace('º', '')

        # Limpiar espacios dobles generados
        text = re.sub(r' {2,}', ' ', text)

        return f"<w:t{attrs}>{text}</w:t>"

    # Aplicar a todos los tags <w:t ...>...</w:t>
    nuevo_xml = re.sub(r'<w:t([^>]*)>(.*?)</w:t>', procesar_wt, xml_content, flags=re.DOTALL)
    return nuevo_xml
