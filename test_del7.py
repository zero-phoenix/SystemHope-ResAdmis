import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Open(r'C:\Users\Admin\.gemini\antigravity\scratch\ResAdmi\Modelos al 30-06-26\MODELO xxxx exp. ADM ver. David 1 DDO,  VARIAS IMPUTACIONES.docx')
fn = doc.Footnotes(15)
rng = fn.Range.Duplicate
print('Range text before:', repr(rng.Text))
while rng.Characters.Count > 0 and rng.Characters.Last.Text in ['\r', '\n', ' ', '\t']:
    rng.Characters.Last.Delete()
print('Range text after:', repr(rng.Text))
doc.Close(False)
word.Quit()
