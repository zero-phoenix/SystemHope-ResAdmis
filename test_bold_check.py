import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(r'C:\Users\Admin\Desktop\ADM 2190-2026.docx')
fn = doc.Footnotes(1)
for j, p in enumerate(fn.Range.Paragraphs):
    print(f'P{j}: {p.Range.Text.strip()}')
    for w in p.Range.Words:
        print(f'  Word: {repr(w.Text)} Bold: {w.Font.Bold}')
    if j > 2: break
doc.Close(False)
word.Quit()
