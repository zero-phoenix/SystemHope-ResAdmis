import xml.etree.ElementTree as ET
import zipfile
z = zipfile.ZipFile(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx')
xml_str = z.read('word/footnotes.xml').decode('utf-8')
tree = ET.fromstring(xml_str)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
fns = tree.findall('.//w:footnote', ns)
for i, fn in enumerate(fns):
    print(f'Footnote {i}: paras={len(fn.findall("w:p", ns))}')
    for j, p in enumerate(fn.findall("w:p", ns)):
        texts = p.findall('.//w:t', ns)
        text = ''.join(t.text for t in texts if t.text)
        print(f'  P{j}: {repr(text)}')
