import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\Desktop\ADM 2190-2026.docx')
fn = doc.Footnotes(1)
for j, p in enumerate(fn.Range.Paragraphs):
    print(f'FN 1 P{j}: Text={repr(p.Range.Text[:50])} SpaceBefore={p.Format.SpaceBefore} SpaceAfter={p.Format.SpaceAfter}')
doc.Close(False)
word.Quit()
