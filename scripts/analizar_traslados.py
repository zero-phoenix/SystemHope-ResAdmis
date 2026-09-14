import zipfile
import re
from pathlib import Path
from collections import defaultdict

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))
print(f"Total plantillas a examinar: {len(docs)}")

traslado_casos = []

for f in docs:
    try:
        with zipfile.ZipFile(f) as z:
            fn_xml = z.read("word/footnotes.xml").decode("utf-8") if "word/footnotes.xml" in z.namelist() else ""
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            
            # Buscar en notas al pie tempranas (id 1 a 5)
            m_fn = re.findall(r'<w:footnote[^>]*w:id="([1-5])"[^>]*>(.*?)</w:footnote>', fn_xml, re.DOTALL)
            for fn_id, fn_content in m_fn:
                text_fn = re.sub(r'<[^>]+>', ' ', fn_content)
                text_fn = re.sub(r'\s+', ' ', text_fn).strip()
                
                # Criterio de demarcación de traslado
                indicadores = [
                    'remitid', 'remisi', 'inhibi', 'incompetencia', 'orps', 'sumar', 
                    'declinatoria', 'traslado', 'mesa de partes', 'oficio n', 'providencia',
                    'proviene', 'deriv', 'competencia territorial', 'otra sede', 'sede central'
                ]
                
                if any(k in text_fn.lower() for k in indicadores) and 'diario oficial el peruano' not in text_fn.lower():
                    # Extraer el primer párrafo tras HECHOS
                    p_hechos = ""
                    pos_hechos = doc_xml.find("HECHOS")
                    if pos_hechos != -1:
                        m_p = re.search(r'<w:p[^>]*>(.*?)</w:p>', doc_xml[pos_hechos:pos_hechos+4000], re.DOTALL)
                        if m_p:
                            p_hechos = re.sub(r'<[^>]+>', ' ', m_p.group(1))
                            p_hechos = re.sub(r'\s+', ' ', p_hechos).strip()
                    
                    traslado_casos.append({
                        "file": f.name,
                        "rel_path": str(f.relative_to(base_dir)).replace("\\", "/"),
                        "fn_id": fn_id,
                        "fn_text": text_fn,
                        "hechos_p1": p_hechos
                    })
                    break
    except Exception as e:
        pass

print(f"Total de modelos con nota al pie de traslado/remisión: {len(traslado_casos)}")

# Imprimir muestras representativas
for idx, c in enumerate(traslado_casos[:15], 1):
    print(f"\n==================== MUESTRA {idx} ====================")
    print("Archivo:", c["file"])
    print("Ruta:", c["rel_path"])
    print("Nota al pie (ID " + c["fn_id"] + "):", c["fn_text"])
    print("Considerativa (Hechos P1):", c["hechos_p1"][:300])

