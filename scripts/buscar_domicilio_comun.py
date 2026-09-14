import zipfile
import re
from pathlib import Path

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))

muestras_domicilio_comun = []

for f in docs:
    try:
        with zipfile.ZipFile(f) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            paras_xml = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)
            paras = [re.sub(r'<[^>]+>', ' ', p).strip() for p in paras_xml]
            paras = [re.sub(r'\s+', ' ', p) for p in paras if p]
            
            for p in paras:
                # Buscar requerimiento o notificacion donde hayan al menos 2 sujetos con ' y '
                if any(p.startswith(art) for art in ["OCTAVO", "NOVENO", "DÉCIMO", "UNDÉCIMO", "DUODÉCIMO"]):
                    if (" y a " in p or " y al " in p or " y a la " in p or "ambos" in p or "común" in p or "mismo domicilio" in p):
                        if any(k in p.lower() for k in ["casilla", "correo", "bandeja", "domicilio", "notificaci"]):
                            muestras_domicilio_comun.append({
                                "file": f.name,
                                "parrafo": p
                            })
                            break
    except Exception:
        pass

print(f"Total de casos con notificación conjunta / domicilio compartido: {len(muestras_domicilio_comun)}")
for m in muestras_domicilio_comun[:10]:
    print("\n=======================================================")
    print("Archivo:", m["file"])
    print("Párrafo:", m["parrafo"])

