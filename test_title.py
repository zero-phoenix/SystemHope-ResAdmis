import re

def format_resolutiva_name(name):
    match = re.match(r'^(.*?)\s*\(.*?\)$', name.strip())
    if match:
        name = match.group(1)
    words = name.split()
    for i, w in enumerate(words):
        if w.upper() in ['S.A.', 'S.A.C.', 'E.I.R.L.', 'S.R.L.', 'S.A.A.']:
            words[i] = w.upper()
        elif w.upper() in ['Y', 'E', 'DE', 'DEL', 'EL', 'LA', 'LOS', 'LAS']:
            if i > 0:
                words[i] = w.lower()
            else:
                words[i] = w.capitalize()
        else:
            words[i] = w.capitalize()
    return ' '.join(words)

print(format_resolutiva_name('GLADIS YSABEL BENITES CAJA (SEÑORA BENITES)'))
print(format_resolutiva_name('RÍMAC SEGUROS Y REASEGUROS S.A. (RÍMAC SEGUROS)'))
