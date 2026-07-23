import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(r'C:\Users\Admin\Desktop\ADM 2190-2026.docx')
fn = doc.Footnotes(1)
for j, p in enumerate(fn.Range.Paragraphs):
    print(f'FN 1 P{j}: Bold={p.Range.Font.Bold} Text={repr(p.Range.Text[:50])}')
doc.Close(False)
word.Quit()
