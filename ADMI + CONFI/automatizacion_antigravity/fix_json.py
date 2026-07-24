import json
from pathlib import Path

json_path = Path("automatizacion_antigravity/casos/1750-2026.json")
data = json.loads(json_path.read_text(encoding="utf-8"))

for key, val in data.get("footnotes", {}).items():
    # Remove markdown bold
    val = val.replace("**", "")
    # Replace true newlines with vertical tabs (soft line breaks) to preserve Footnote style
    val = val.replace("\n", "\x0b")
    # Clean up double vertical tabs if any
    val = val.replace("\x0b\x0b", "\x0b")
    # Clean up any weird tab-vtab combinations
    val = val.replace("\t\x0b", "\x0b")
    data["footnotes"][key] = val

json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("JSON cleaned!")
