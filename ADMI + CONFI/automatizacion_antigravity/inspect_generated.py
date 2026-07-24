import sys
from docx import Document

d = Document(r"productos (resoluciones) elaborada por google antigravity\ADM 2142-2026-CC1.docx")

for i, p in enumerate(d.paragraphs):
    if "El 06 de julio" in p.text or "La aseguradora no" in p.text or "Presunta infracción" in p.text:
        print(f"Index {i}: {p.text[:40]}...")
        print("  Style:", p.style.name)
        numpr = p._p.pPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr")
        if numpr is not None:
            ilvl = numpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ilvl")
            numId = numpr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numId")
            print(f"  numPr: ilvl={ilvl.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if ilvl is not None else 'None'}, numId={numId.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if numId is not None else 'None'}")
        else:
            print("  numPr: None")
        print(f"  Indents: left={p.paragraph_format.left_indent}, first_line={p.paragraph_format.first_line_indent}")
