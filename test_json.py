import json
with open(r'automatizacion_antigravity\casos\2190-2026.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    f1 = data['footnotes']['__F1__']
    print(repr(f1[:100]))
