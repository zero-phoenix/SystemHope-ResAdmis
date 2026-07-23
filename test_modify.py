import re
def format_resolutiva_name(name):
    match = re.match(r'^(.*?)\s*\(.*?\)$', name.strip())
    if match:
        name = match.group(1)
    name = name.replace('RA?MAC', 'RÍMAC').replace('RA-mac', 'Rímac')
    words = name.split()
    for i, w in enumerate(words):
        if w.upper() in ['S.A.', 'S.A.C.', 'E.I.R.L.', 'S.R.L.', 'Y', 'E', 'DE', 'DEL', 'EL', 'LA', 'LOS', 'LAS']:
            if w.upper() in ['Y', 'E', 'DE', 'DEL', 'EL', 'LA', 'LOS', 'LAS'] and i > 0:
                words[i] = w.lower()
            else:
                words[i] = w.upper()
        else:
            words[i] = w.capitalize()
    return ' '.join(words)
print(format_resolutiva_name('GLADIS YSABEL BENITES CAJA (SEAORA BENITES)'))
print(format_resolutiva_name('RA?MAC SEGUROS Y REASEGUROS S.A. (RA?MAC SEGUROS)'))
