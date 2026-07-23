import xml.etree.ElementTree as ET
tree = ET.parse('footnotes_debug.xml')
root = tree.getroot()
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
fns = root.findall('w:footnote', ns)
print('Total footnotes:', len(fns))
for i, fn in enumerate(fns):
    print(f'\nFootnote {i}: id={fn.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id")}; paras={len(fn.findall("w:p", ns))}')
    for j, p in enumerate(fn.findall('w:p', ns)):
        ppr = p.find('w:pPr', ns)
        spacing = ppr.find('w:spacing', ns) if ppr is not None else None
        style = ppr.find('w:pStyle', ns) if ppr is not None else None
        s_val = style.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if style is not None else 'None'
        space_after = spacing.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}after') if spacing is not None else 'None'
        print(f'  P{j}: Style={s_val}, SpaceAfter={space_after}')
