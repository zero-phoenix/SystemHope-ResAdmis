import zipfile
import re
from pathlib import Path
from collections import Counter

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))

num_articulos_dist = Counter()
secciones_principales = Counter()
patrones_apertura_hechos = Counter()
patrones_pretension = Counter()

for f in docs:
    try:
        with zipfile.ZipFile(f) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            
            # Contar articulos resolutivos en cada archivo
            arts = re.findall(r'\b(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]TIMO|OCTAVO|NOVENO|D[EÉ]CIMO(?:\s+[A-ZÁÉÍÓÚ]+)?):', doc_xml)
            num_articulos_dist[len(arts)] += 1
            
            # Secciones principales
            if "I. HECHOS" in doc_xml or "I.   HECHOS" in doc_xml or "I.	HECHOS" in doc_xml:
                secciones_principales["I. HECHOS"] += 1
            if "ADMISIÓN A TRÁMITE" in doc_xml.upper() or "ADMISION A TRAMITE" in doc_xml.upper():
                secciones_principales["II. ADMISIÓN A TRÁMITE"] += 1
            if "REQUERIMIENTO DE INFORMACIÓN" in doc_xml.upper() or "REQUERIMIENTO DE INFORMACION" in doc_xml.upper():
                secciones_principales["III. REQUERIMIENTO DE INFORMACIÓN"] += 1
                
            # Apertura de hechos
            m_open = re.search(r'HECHOS.*?(Mediante\s+[^,\.]{10,80})', doc_xml, re.DOTALL)
            if m_open:
                clean_open = re.sub(r'<[^>]+>', '', m_open.group(1)).strip()
                clean_open = re.sub(r'\s+', ' ', clean_open)
                # abstraer tipo
                if "escrito del" in clean_open.lower():
                    patrones_apertura_hechos["Mediante el escrito del [fecha]"] += 1
                elif "denuncia del" in clean_open.lower():
                    patrones_apertura_hechos["Mediante la denuncia del [fecha]"] += 1
                elif "oficio" in clean_open.lower():
                    patrones_apertura_hechos["Mediante Oficio..."] += 1
                else:
                    patrones_apertura_hechos["Otro tipo de apertura"] += 1

    except Exception:
        pass

print("=== DISTRIBUCIÓN DE CANTIDAD DE ARTÍCULOS RESOLUTIVOS POR MODELO ===")
for num_arts, count in sorted(num_articulos_dist.items()):
    print(f"  {num_arts} artículos: {count} modelos")

print("\n=== PRESENCIA DE SECCIONES PRINCIPALES EN CONSIDERATIVA ===")
for sec, count in secciones_principales.items():
    print(f"  {sec}: {count} modelos ({count/len(docs)*100:.1f}%)")

print("\n=== PATRONES DE APERTURA EN NUMERAL 1 DE HECHOS ===")
for pat, count in patrones_apertura_hechos.most_common():
    print(f"  {pat}: {count} modelos")
