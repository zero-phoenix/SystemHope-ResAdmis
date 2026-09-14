# -*- coding: utf-8 -*-
import glob, re, zipfile, json
from collections import defaultdict

providers_stats = defaultdict(lambda: {'count': 0, 'casilla': 0, 'correo': 0, 'domicilio': 0, 'expedientes': set()})

files = glob.glob('plantillas_maestras/**/*.docx', recursive=True)
for f in files:
    exp_m = re.search(r'TPL_(\d{4}_\d{4})', f)
    exp = exp_m.group(1).replace('_', '-') if exp_m else 'DESCONOCIDO'
    try:
        with zipfile.ZipFile(f) as z:
            xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
            paras = re.findall(r'<w:p\b[^>]*>(.*?)</w:p>', xml)
            for p in paras:
                text = re.sub(r'<[^>]+>', '', p).strip()
                
                # Casilla
                m_cas = re.search(r'requerir a\s+([^,]+?)\s+para que efectúe el acuse de recibo mediante la confirmación de recepción de la notificación remitida por este despacho a su(?:s)? Casilla(?:s)? Electrónica(?:s)?', text, re.IGNORECASE)
                if m_cas:
                    prov = m_cas.group(1).strip()
                    for p_sub in re.split(r'\s+y\s+(?:a\s+)?', prov):
                        p_sub = p_sub.strip().rstrip('.')
                        if len(p_sub) > 3 and 'señor' not in p_sub.lower():
                            providers_stats[p_sub]['count'] += 1
                            providers_stats[p_sub]['casilla'] += 1
                            providers_stats[p_sub]['expedientes'].add(exp)

                # Correo
                m_cor = re.search(r'requerir a\s+([^,]+?)\s+para que, dentro del plazo de dos \(2\) días hábiles siguientes a la fecha en que recib(?:a|an) la notificación en su(?:s)? bandeja(?:s)? de correo electrónico', text, re.IGNORECASE)
                if m_cor:
                    prov = m_cor.group(1).strip()
                    for p_sub in re.split(r'\s+y\s+(?:a\s+)?', prov):
                        p_sub = p_sub.strip().rstrip('.')
                        if len(p_sub) > 3 and 'señor' not in p_sub.lower():
                            providers_stats[p_sub]['count'] += 1
                            providers_stats[p_sub]['correo'] += 1
                            providers_stats[p_sub]['expedientes'].add(exp)

                # Domicilio
                m_dom = re.search(r'requerir a\s+([^,]+?)\s+para que, dentro del plazo de dos \(2\) días hábiles siguientes a la fecha en que recib(?:a|an) la notificación en su(?:s)? domicilio procesal', text, re.IGNORECASE)
                if m_dom:
                    prov = m_dom.group(1).strip()
                    for p_sub in re.split(r'\s+y\s+(?:a\s+)?', prov):
                        p_sub = p_sub.strip().rstrip('.')
                        if len(p_sub) > 3 and 'señor' not in p_sub.lower():
                            providers_stats[p_sub]['count'] += 1
                            providers_stats[p_sub]['domicilio'] += 1
                            providers_stats[p_sub]['expedientes'].add(exp)
    except Exception:
        pass

print(f"Total proveedores unicos detectados en notificaciones: {len(providers_stats)}")
top_provs = sorted(providers_stats.items(), key=lambda x: x[1]['count'], reverse=True)
output_data = {}
for p, data in top_provs:
    if data['casilla'] >= data['correo'] and data['casilla'] >= data['domicilio']:
        via = "Casilla Electrónica"
    elif data['correo'] >= data['domicilio']:
        via = "Correo Electrónico"
    else:
        via = "Domicilio Procesal / Cédula Física"
    
    output_data[p] = {
        "denominacion": p,
        "via_notificacion_oficial": via,
        "frecuencia_total": data['count'],
        "casilla_count": data['casilla'],
        "correo_count": data['correo'],
        "domicilio_count": data['domicilio'],
        "expedientes_muestra": sorted(list(data['expedientes']))[:5]
    }
    if data['count'] >= 5:
        print(f"{p} | {via} | Casilla:{data['casilla']} Correo:{data['correo']} Dom:{data['domicilio']}")

with open("docs/directorio_proveedores_domicilios.json", "w", encoding="utf-8") as out_f:
    json.dump(output_data, out_f, indent=2, ensure_ascii=False)
print("Guardado en docs/directorio_proveedores_domicilios.json")
