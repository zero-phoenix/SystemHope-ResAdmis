import zipfile
import re
from pathlib import Path

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))

muestras_notif = []

for f in docs[:50]:
    try:
        with zipfile.ZipFile(f) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            
            m_notif = list(re.finditer(r'\bnotificar\b', doc_xml, re.IGNORECASE))
            if m_notif:
                pos_notif = m_notif[-1].start()
                sub = doc_xml[pos_notif-200:pos_notif+2500]
                # Limpiar párrafos
                paras = re.findall(r'<w:p[^>]*>(.*?)</w:p>', sub, re.DOTALL)
                clean_paras = [re.sub(r'<[^>]+>', ' ', p).strip() for p in paras]
                clean_paras = [re.sub(r'\s+', ' ', p) for p in clean_paras if p and len(p) > 20]
                muestras_notif.append({
                    "file": f.name,
                    "notif_text": clean_paras[:4]
                })
    except Exception:
        pass

for m in muestras_notif[:6]:
    print("==================================================")
    print("Archivo:", m["file"])
    for p in m["notif_text"]:
        print("  Párrafo:", p)
