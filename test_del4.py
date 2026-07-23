import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
fn = doc.Footnotes(4)
print('Last paragraph text:', repr(fn.Range.Paragraphs.Last.Range.Text))
doc.Close(False)
word.Quit()
