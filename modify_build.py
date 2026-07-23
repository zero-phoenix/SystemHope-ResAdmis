import re
from pathlib import Path

code = '''
def format_resolutiva_name(name):
    match = re.match(r'^(.*?)\s*\((.*?)\)$', name.strip())
    if match:
        name = match.group(1)
    name = name.replace('RA?MAC', 'RÍMAC').replace('RA-mac', 'Rímac')
    words = name.split()
    for i, w in enumerate(words):
        if w.upper() in ['S.A.', 'S.A.C.', 'E.I.R.L.', 'S.R.L.', 'S.A.A.']:
            words[i] = w.upper()
        elif w.upper() in ['Y', 'E', 'DE', 'DEL', 'EL', 'LA', 'LOS', 'LAS']:
            if i > 0:
                words[i] = w.lower()
            else:
                words[i] = w.capitalize()
        else:
            words[i] = w.capitalize()
    return ' '.join(words)

def preprocess_caso(caso):
    abbreviation = "Rímac"
    if 'denunciado' in caso:
        if 'RIMAC' in caso['denunciado'].upper() or 'RÍMAC' in caso['denunciado'].upper() or 'RA?MAC' in caso['denunciado'].upper():
            caso['denunciado'] = re.sub(r'\([^\)]*R[IÍA\?\-]+MAC SEGUROS[^\)]*\)', '(RÍMAC)', caso['denunciado'], flags=re.IGNORECASE)
            caso['denunciado'] = caso['denunciado'].replace('RA?MAC', 'RÍMAC').replace('RA-mac', 'Rímac')
        
        match = re.match(r'^(.*?)\s*\((.*?)\)$', caso['denunciado'].strip())
        if match:
            abbrev_raw = match.group(2)
            if abbrev_raw.upper() == 'RÍMAC' or abbrev_raw.upper() == 'RIMAC' or abbrev_raw.upper() == 'RA?MAC':
                abbreviation = "Rímac"
            else:
                abbreviation = abbrev_raw.title()
    
    for key, value in caso.items():
        if isinstance(value, str):
            value = value.replace('Rímac Seguros', 'Rímac').replace('Rimac Seguros', 'Rimac').replace('RA-mac Seguros', 'Rímac').replace('RÍMAC SEGUROS', 'RÍMAC')
            value = value.replace('N° ', '').replace('N°', '').replace('°', '')
            if key == "medida_correctiva":
                value = re.sub(r'(?i)\bla aseguradora\b', abbreviation, value)
                value = re.sub(r'(?i)\bla compañ[ií]a aseguradora\b', abbreviation, value)
            else:
                value = re.sub(r'(?i)\bla aseguradora\b', 'la compañía aseguradora', value)
            caso[key] = value
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, str):
                    item = item.replace('Rímac Seguros', 'Rímac').replace('Rimac Seguros', 'Rimac').replace('RA-mac Seguros', 'Rímac').replace('RÍMAC SEGUROS', 'RÍMAC')
                    item = item.replace('N° ', '').replace('N°', '').replace('°', '')
                    if key == "medida_correctiva":
                        item = re.sub(r'(?i)\bla aseguradora\b', abbreviation, item)
                        item = re.sub(r'(?i)\bla compañ[ií]a aseguradora\b', abbreviation, item)
                    else:
                        item = re.sub(r'(?i)\bla aseguradora\b', 'la compañía aseguradora', item)
                new_list.append(item)
            caso[key] = new_list
        elif isinstance(value, dict):
            new_dict = {}
            for k, v in value.items():
                if isinstance(v, str):
                    v = v.replace('Rímac Seguros', 'Rímac').replace('Rimac Seguros', 'Rimac').replace('RA-mac Seguros', 'Rímac').replace('RÍMAC SEGUROS', 'RÍMAC')
                    v = v.replace('N° ', '').replace('N°', '').replace('°', '')
                new_dict[k] = v
            caso[key] = new_dict
    return caso

def _default_resolutivos(caso):
    denunciado = format_resolutiva_name(caso["denunciado"])
    denunciante = format_resolutiva_name(caso["denunciante"])
    fecha = caso["fecha_denuncia"]
    return {
        "PRIMERO": f"admitir a trámite la denuncia del {fecha} interpuesta por {denunciante} contra {denunciado}, por lo siguiente:",
        "SEGUNDO": f"tener por ofrecidos los medios probatorios presentados en el escrito de denuncia del {fecha}.",
        "TERCERO": f"requerir a {denunciado} que cumpla con lo siguiente:",
        "CUARTO": f"correr traslado de la denuncia interpuesta el {fecha} a {denunciado}, para que, de conformidad con lo dispuesto por el artículo 26 de la Ley sobre Facultades, Normas y Organización del Indecopi, aprobada por Decreto Legislativo 807, presente sus descargos en un plazo no mayor de cinco (5) días hábiles contados desde la notificación.",
        "QUINTO": f"requerir que, en un plazo no mayor de cinco (5) días hábiles contado a partir del día siguiente de la notificación de la presente resolución, el proveedor denunciado cumpla con lo siguiente: {caso.get('req_info', '')}",
    }
'''

path = Path('automatizacion_antigravity/build.py')
content = path.read_text('utf-8')

match = re.search(r'def _default_resolutivos\(caso\):.*?return \{.*?\n    \}', content, flags=re.DOTALL)
if match:
    content = content[:match.start()] + code + content[match.end():]

match = re.search(r'def preprocess_caso\(caso\):.*?return caso\n\n', content, flags=re.DOTALL)
if match:
    content = content[:match.start()] + code + "\n" + content[match.end():]

# Let's be safer, just replace from format_resolutiva_name down
match = re.search(r'def format_resolutiva_name\(name\):.*?return \{.*?\n    \}', content, flags=re.DOTALL)
if match:
    content = content[:match.start()] + code + content[match.end():]

path.write_text(content, 'utf-8')
