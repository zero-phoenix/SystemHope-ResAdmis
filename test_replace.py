import re
abbrev = 'Rímac'
text = 'la aseguradora hizo tal cosa y LA ASEGURADORA no quiso'
print(re.sub(r'(?i)\bla aseguradora\b', abbrev, text))
print(re.sub(r'(?i)\bla aseguradora\b', 'la compañía aseguradora', text))
