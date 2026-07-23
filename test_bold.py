import re
text = 'Artculo 18.- Idoneidad\r'
clean_text = re.sub(r'^[\x00-\x20]+', '', text)
print(repr(clean_text))
print(bool(re.match(r'^Art[iI]culo\s+', clean_text, re.IGNORECASE)))
