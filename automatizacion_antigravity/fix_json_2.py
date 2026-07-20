import json
from pathlib import Path

json_path = Path("automatizacion_antigravity/casos/1750-2026.json")
data = json.loads(json_path.read_text(encoding="utf-8"))

# 1. Restore soft line breaks to true newlines to prevent justified text stretch
for key, val in data.get("footnotes", {}).items():
    val = val.replace("\x0b", "\n")
    data["footnotes"][key] = val

# 2. Remove the duplicated footnote 5
if "__F5__" in data.get("footnotes", {}):
    del data["footnotes"]["__F5__"]

# 3. Remove the redundant paragraph from imputaciones_analisis
new_analisis = []
for para in data.get("imputaciones_analisis", []):
    if "En tanto la denuncia reúne los requisitos" in para:
        continue
    new_analisis.append(para)
data["imputaciones_analisis"] = new_analisis

json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("JSON cleaned (removed F5, removed redundant paragraph, restored newlines)")
