import json
from pathlib import Path
path = Path(r'automatizacion_antigravity\casos\2190-2026.json')
content = path.read_text(encoding='utf-8')
try:
    fixed = content.encode('cp1252').decode('utf-8')
    path.write_text(fixed, encoding='utf-8')
    print('Fixed encoding!')
except Exception as e:
    print(e)
