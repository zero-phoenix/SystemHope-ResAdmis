import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
print('Before count:', doc.Footnotes.Count)
fn = doc.Footnotes(4)
rng = fn.Range.Duplicate
while True:
    rng.End = rng.End + 1
    if rng.Characters.Last.Text in ['\r', '\n', ' ', '\t']:
        rng.Characters.Last.Delete()
    else:
        break
print('After count:', doc.Footnotes.Count)
doc.Close(False)
word.Quit()
