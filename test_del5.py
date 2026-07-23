import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
for i in range(1, doc.Footnotes.Count + 1):
    print(f'Footnote {i} text repr:', repr(doc.Footnotes(i).Range.Text))
doc.Close(False)
word.Quit()
