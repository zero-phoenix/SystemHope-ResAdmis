import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\productos (resoluciones) elaborada por google antigravity\ADM 2190-2026-CC1.docx')
fn = doc.Footnotes(4)
print('Before paragraphs:', fn.Range.Paragraphs.Count)
if fn.Range.Paragraphs.Count > 1 and fn.Range.Paragraphs.Last.Range.Text == '\r':
    print('Deleting last paragraph!')
    fn.Range.Paragraphs.Last.Range.Delete()
print('After paragraphs:', fn.Range.Paragraphs.Count)
doc.Close(False)
word.Quit()
