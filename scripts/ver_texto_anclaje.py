import zipfile
import re
from pathlib import Path

sample_files = [
    Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras\01_seguro_vehicular\anulacion_indebida\2_ddos_banco_y_aseguradora\varon\TPL_2138_2025_SEGURO_VEHICULAR_ANULACION_INDEBIDA_BANCO_VARON_R1.docx"),
    Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras\01_seguro_vehicular\deficiente_gestion_siniestro\2_o_mas_ddos_varios\mujer\TPL_1176_2026_SEGURO_VEHICULAR_DEFICIENTE_GESTION_SINIESTRO_ASEGURADORA_MUJER_R2.docx"),
    Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras\01_seguro_vehicular\discriminacion\2_o_mas_ddos_varios\mujer\TPL_1519_2025_SEGURO_VEHICULAR_DISCRIMINACION_ASEGURADORA_MUJER_R2.docx"),
]

for sf in sample_files:
    if sf.exists():
        with zipfile.ZipFile(sf) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8")
            fn_xml = z.read("word/footnotes.xml").decode("utf-8")
            m_fn = re.search(r'<w:footnote[^>]*w:id="1"[^>]*>(.*?)</w:footnote>', fn_xml, re.DOTALL)
            fn_text = re.sub(r'<[^>]+>', ' ', m_fn.group(1)).strip() if m_fn else ''
            
            # Buscar donde esta el footnoteReference w:id="1" en document.xml
            idx_fn = doc_xml.find('footnoteReference w:id="1"')
            if idx_fn != -1:
                # buscar el párrafo completo
                p_start = doc_xml.rfind("<w:p ", 0, idx_fn)
                if p_start == -1: p_start = doc_xml.rfind("<w:p>", 0, idx_fn)
                p_end = doc_xml.find("</w:p>", idx_fn) + 6
                p_xml = doc_xml[p_start:p_end]
                
                # extraer runs dentro de p_xml para ver que palabra tiene el superíndice
                runs = re.findall(r'<w:r[^>]*>(.*?)</w:r>', p_xml, re.DOTALL)
                words_before = []
                for r in runs:
                    if 'footnoteReference' in r:
                        break
                    t = re.findall(r'<w:t[^>]*>(.*?)</w:t>', r)
                    if t:
                        words_before.append("".join(t))
                
                print("========================================")
                print("Archivo:", sf.name)
                print("Texto inmediatamente antes del superíndice:", "".join(words_before)[-80:])
                print("Nota al pie 1:", fn_text)

