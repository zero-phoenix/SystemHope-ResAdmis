import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx')
fn = doc.Footnotes(14)
print('Template FN 14:')
for j, p in enumerate(fn.Range.Paragraphs):
    print(f'P{j} Bold: {p.Range.Font.Bold} Text: {p.Range.Text.strip()[:50]}')
doc.Close(False)
word.Quit()
