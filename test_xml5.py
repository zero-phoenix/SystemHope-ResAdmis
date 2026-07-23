import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx')
for i in [14, 15]:
    fn = doc.Footnotes(i)
    for j, p in enumerate(fn.Range.Paragraphs):
        print(f'FN {i} P{j}: Text={repr(p.Range.Text[:20])} SpaceBefore={p.Format.SpaceBefore} SpaceAfter={p.Format.SpaceAfter}')
doc.Close(False)
word.Quit()
