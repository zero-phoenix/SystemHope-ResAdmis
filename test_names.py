import re
def format_resolutiva_name(name):
    match = re.match(r'^(.*?)\s*\(.*?\)$', name.strip())
    if match:
        name = match.group(1)
    return name.title()

print(format_resolutiva_name('GLADIS YSABEL BENITES CAJA (SEAORA BENITES)'))
print(format_resolutiva_name('RA?MAC SEGUROS Y REASEGUROS S.A. (RA?MAC SEGUROS)'))
