import re
text = 'Ley N 29571, Cdigo de Proteccin y Defensa del Consumidor.'
clean_text = re.sub(r'^[ \t]+', '', text)
print(bool(re.match(r'^(?:LEY|DECRETO|TEXTO)\b', clean_text, re.IGNORECASE)))
