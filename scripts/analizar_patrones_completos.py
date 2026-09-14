import zipfile
import re
from pathlib import Path
from collections import Counter, defaultdict

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))

# Patrones a extraer
organos_origen = Counter()
tipos_documento = Counter()
formulas_fn = []
palabras_anclaje = Counter()

# Estructura Considerativa
secciones_considerativa = Counter()
articulos_resolutiva = Counter()

for f in docs:
    try:
        with zipfile.ZipFile(f) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            fn_xml = z.read("word/footnotes.xml").decode("utf-8") if "word/footnotes.xml" in z.namelist() else ""
            
            # 1. Analizar si tiene nota de traslado
            m_fn1 = re.search(r'<w:footnote[^>]*w:id="1"[^>]*>(.*?)</w:footnote>', fn_xml, re.DOTALL)
            if m_fn1:
                fn_txt = re.sub(r'<[^>]+>', ' ', m_fn1.group(1))
                fn_txt = re.sub(r'\s+', ' ', fn_txt).strip()
                if any(k in fn_txt.lower() for k in ['remiti', 'remisi', 'traslado', 'memorandum', 'oficio']):
                    formulas_fn.append(fn_txt)
                    
                    # Tipo de documento de traslado
                    if "MEMORANDUM" in fn_txt.upper():
                        tipos_documento["MEMORANDUM"] += 1
                    elif "DOCUMENTO DE TRASLADO" in fn_txt.upper():
                        tipos_documento["DOCUMENTO DE TRASLADO"] += 1
                    elif "OFICIO" in fn_txt.upper():
                        tipos_documento["OFICIO"] += 1
                    elif "PROVIDENCIA" in fn_txt.upper():
                        tipos_documento["PROVIDENCIA"] += 1
                    elif "RESOLUCI" in fn_txt.upper():
                        tipos_documento["RESOLUCION"] += 1
                    else:
                        tipos_documento["OTRO"] += 1
                        
                    # Órgano de origen
                    m_org = re.search(r'([A-Z0-9]+(?:-[A-Z0-9]+)*\/INDECOPI)', fn_txt)
                    if m_org:
                        organos_origen[m_org.group(1)] += 1
                    else:
                        # buscar PS1, PS2, CC2, etc.
                        m_org2 = re.search(r'\b(PS1|PS2|CC2|ILN|CPC-[A-Z]+|ORPS[A-Z0-9\-]*)\b', fn_txt)
                        if m_org2:
                            organos_origen[m_org2.group(1)] += 1
                            
                    # Anclaje en document.xml
                    pos_fn1 = doc_xml.find('footnoteReference w:id="1"')
                    if pos_fn1 != -1:
                        # Extraer 50 caracteres antes de footnoteReference
                        sub_pre = doc_xml[max(0, pos_fn1-150):pos_fn1]
                        # Quitar XML
                        clean_pre = re.sub(r'<[^>]+>', ' ', sub_pre)
                        words = clean_pre.strip().split()
                        if words:
                            palabras_anclaje[words[-1].lower()] += 1

            # 2. Estructura Considerativa
            # Secciones con números romanos o títulos
            titulos = re.findall(r'(?:I|II|III|IV|V|VI)\.\s+([A-ZÁÉÍÓÚÑ\s]{4,40})', doc_xml)
            for t in titulos:
                secciones_considerativa[t.strip()] += 1
                
            # 3. Estructura Resolutiva
            articulos = re.findall(r'\b(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]TIMO|OCTAVO|NOVENO|D[EÉ]CIMO(?:\s+[A-ZÁÉÍÓÚ]+)?):', doc_xml)
            for a in articulos:
                articulos_resolutiva[a.upper()] += 1

    except Exception as e:
        pass

print("=== 1. TIPOS DE DOCUMENTO DE TRASLADO ===")
for k, v in tipos_documento.most_common():
    print(f"  {k}: {v}")

print("\n=== 2. ÓRGANOS REMITENTES MÁS COMUNES ===")
for k, v in organos_origen.most_common(15):
    print(f"  {k}: {v}")

print("\n=== 3. PALABRA DE ANCLAJE DE LA NOTA AL PIE 1 ===")
for k, v in palabras_anclaje.most_common(10):
    print(f"  {k}: {v}")

print("\n=== 4. FÓRMULAS TEXTUALES CANÓNICAS DE TRASLADO (MUESTRAS) ===")
for f in formulas_fn[:8]:
    print(f"  * {f}")

print("\n=== 5. SECCIONES CONSIDERATIVAS MÁS FRECUENTES ===")
for k, v in secciones_considerativa.most_common(10):
    print(f"  {k}: {v}")

print("\n=== 6. ARTÍCULOS RESOLUTIVOS DETECTADOS ===")
for k, v in articulos_resolutiva.most_common(12):
    print(f"  {k}: {v}")

