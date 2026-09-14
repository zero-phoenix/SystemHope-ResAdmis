import zipfile
import re
from pathlib import Path

p = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras\01_seguro_vehicular\anulacion_indebida\2_ddos_banco_y_aseguradora\varon\TPL_2138_2025_SEGURO_VEHICULAR_ANULACION_INDEBIDA_BANCO_VARON_R1.docx")

with zipfile.ZipFile(p) as z:
    doc_xml = z.read("word/document.xml").decode("utf-8")
    paras_xml = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)
    paras = [re.sub(r'<[^>]+>', ' ', p).strip() for p in paras_xml]
    paras = [re.sub(r'\s+', ' ', p) for p in paras if p]

print("=== PÁRRAFO DE IMPUTACIÓN EN SECCIÓN II ===")
for p_txt in paras:
    if "involucraría" in p_txt or "expectativas" in p_txt or "calificar el hecho" in p_txt:
        print(p_txt)
        print("-" * 40)

print("\n=== ARTÍCULOS PRIMERO Y SEGUNDO EN RESUELVE ===")
for p_txt in paras:
    if p_txt.startswith("PRIMERO:") or p_txt.startswith("SEGUNDO:"):
        print(p_txt)
        print("-" * 40)

