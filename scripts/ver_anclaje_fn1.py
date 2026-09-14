import zipfile
import re
from pathlib import Path

sample_path = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras\01_seguro_vehicular\anulacion_indebida\2_ddos_banco_y_aseguradora\varon\TPL_2138_2025_SEGURO_VEHICULAR_ANULACION_INDEBIDA_BANCO_VARON_R1.docx")

with zipfile.ZipFile(sample_path) as z:
    doc_xml = z.read("word/document.xml").decode("utf-8")
    
# Buscar donde esta <w:footnoteReference w:id="1"
pos = doc_xml.find('footnoteReference w:id="1"')
if pos != -1:
    p_start = doc_xml.rfind("<w:p ", 0, pos)
    if p_start == -1: p_start = doc_xml.rfind("<w:p>", 0, pos)
    p_end = doc_xml.find("</w:p>", pos) + 6
    p_xml = doc_xml[p_start:p_end]
    clean_p = re.sub(r"<[^>]+>", " ", p_xml)
    clean_p = re.sub(r"\s+", " ", clean_p).strip()
    print("Párrafo donde se ancla la Nota al Pie 1:")
    print(clean_p)
    print("\nXML del párrafo:")
    print(p_xml[:1000])
else:
    print("No se encontro footnoteReference w:id=1")
