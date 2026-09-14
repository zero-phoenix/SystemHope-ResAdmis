from pathlib import Path
import json
import re
import traceback

target = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
existing = list(target.glob("**/*.docx"))
print(f"Total generados: {len(existing)}")

with open(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\docs\catalogo_modelos_phoenyx.json", encoding="utf-8") as f:
    cat = json.load(f)

print("Ultimos 3 generados:")
for f in existing[-3:]:
    print(" ", f.name)

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.depurar_y_estructurar_modelos import (
    RAMAS_MAP, categorizar_materia, categorizar_proveedor,
    categorizar_sujeto, normalizar_cadena, depurar_archivo_docx,
    TARGET_ROOT
)

# Test from len(existing) to the end
start_idx = max(0, len(existing) - 2)
print(f"Starting test from index: {start_idx}")

for idx in range(start_idx, min(start_idx + 15, len(cat))):
    item = cat[idx]
    p = Path(item["ruta_absoluta"])
    print(f"Testing item {idx}: {p.name}")
    try:
        tax = item.get("taxonomia", {})
        meta = item.get("metadata_doc", {})
        tipo_seguro_raw = tax.get("tipo_seguro", "Seguro no especificado")
        rama_folder = RAMAS_MAP.get(tipo_seguro_raw, "17_seguro_no_especificado")
        materia_folder = categorizar_materia(tax.get("hecho_infractor", ""), tax.get("cobertura", ""))
        proveedor_folder = categorizar_proveedor(tax.get("proveedor_carpeta", ""), meta.get("denunciado", ""), tax.get("es_multiple_ddo", False))
        sujeto_folder = categorizar_sujeto(tax.get("sujeto_tipo", ""), tax.get("caso_carpeta", ""), meta.get("denunciante", ""))
        exp_raw = meta.get("expediente", "")
        m_exp = re.search(r'(\d+-\d{4})', exp_raw)
        if not m_exp:
            m_exp = re.search(r'(\d+-\d{4})', p.name)
        num_exp = m_exp.group(1) if m_exp else f"EXP{idx:03d}"
        m_r = re.search(r'R(\d+)', p.name, re.IGNORECASE)
        res_tag = f"_R{m_r.group(1)}" if m_r else ""
        ddo_tag = "ASEGURADORA"
        if "banco" in proveedor_folder:
            ddo_tag = "BANCO"
        elif "2_ddos" in proveedor_folder:
            ddo_tag = "BANCO_Y_ASEGURADORA"
        elif "corredor" in proveedor_folder:
            ddo_tag = "CORREDOR"
        nombre_base = f"TPL_{num_exp}_{rama_folder[3:].upper()}_{materia_folder.upper()}_{ddo_tag}_{sujeto_folder.upper()}{res_tag}"
        nombre_limpio = normalizar_cadena(nombre_base).upper() + ".DOCX"
        destino_dir = TARGET_ROOT / rama_folder / materia_folder / proveedor_folder / sujeto_folder
        destino_path = destino_dir / nombre_limpio
        print(f"  Destino: {destino_path}")
        ok = depurar_archivo_docx(p, destino_path)
        print(f"  OK: {ok}")
    except Exception as e:
        print(f"  EXCEPTION AT {idx}:")
        traceback.print_exc()
        break
