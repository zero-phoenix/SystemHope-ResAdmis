import xml.etree.ElementTree as ET
tree = ET.parse('footnotes_debug.xml')
root = tree.getroot()
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
fns = root.findall('w:footnote', ns)
for i, fn in enumerate(fns):
    if i in [2, 3, 4, 5]:
        print(f'\nFootnote {i}:')
        for j, p in enumerate(fn.findall('w:p', ns)):
            texts = p.findall('.//w:t', ns)
            text = ''.join(t.text for t in texts if t.text)
            print(f'  P{j}: {repr(text)}')

