import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = False
doc = word.Documents.Open(r'C:\Users\Admin\Desktop\ADM 2190-2026.docx')
print('--- RESOLUTIVA ---')
for p in doc.Paragraphs:
    text = p.Range.Text.strip()
    if text.startswith('PRIMERO:') or text.startswith('CUARTO:'):
        print(text)
doc.Close(False)
word.Quit()
