import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
fn = doc.Footnotes(4)
rng = fn.Range.Duplicate
print('End before:', rng.End)
while True:
    rng.End = rng.End + 1
    if rng.Characters.Last.Text == '\r':
        print('Found extra enter at end!')
        rng.Characters.Last.Delete()
    else:
        break
print('End after:', rng.End)
doc.Close(False)
word.Quit()
