import json
from pathlib import Path
path = Path(r'automatizacion_antigravity\casos\2190-2026.json')
content = path.read_text(encoding='utf-8')
print('RA?MAC' in content)
print('RA-mac' in content)
print('RÍMAC' in content)
