import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
fns = doc.Footnotes
fn3 = fns(3)
print(repr(fn3.Range.Text))
while fn3.Range.Characters.Count > 1 and fn3.Range.Characters.Last.Previous.Text in ['\r', '\n', ' ', '\t']:
    fn3.Range.Characters.Last.Previous.Delete()
print('AFTER', repr(fn3.Range.Text))
doc.Close(False)
word.Quit()
