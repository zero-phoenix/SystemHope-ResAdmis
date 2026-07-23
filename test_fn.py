import win32com.client
word = win32com.client.Dispatch('Word.Application')
word.Visible = True
doc = word.Documents.Add()
doc.Content.Text = 'Hello'
fn = doc.Footnotes.Add(Range=doc.Content, Text='Test\r\r \r')
print('start count', fn.Range.Paragraphs.Count)
c = fn.Range.Characters.Count
while c > 1 and fn.Range.Characters(c - 1).Text in ['\r', '\n', ' ', '\t']:
  fn.Range.Characters(c - 1).Delete()
  c = fn.Range.Characters.Count
print('end count', fn.Range.Paragraphs.Count)
doc.Close(False)
word.Quit()
