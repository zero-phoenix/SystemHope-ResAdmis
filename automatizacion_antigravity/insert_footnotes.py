def insert_footnotes(input_path, output_path, footnotes_dict):
    try:
        import win32com.client
    except ImportError:
        print("Word/win32com no disponible: se omite inserción de notas al pie (ejecutar en la PC del usuario con Word)")
        return False
    if not footnotes_dict:
        return True
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    document = word.Documents.Open(str(input_path))
    try:
        # Remove all highlighting (Control+E equivalent)
        document.Content.HighlightColorIndex = 0
        for marker, note in footnotes_dict.items():
            rng = document.Content
            find = rng.Find
            find.Text = marker
            if find.Execute():
                rng.Text = ""
                # win32com requires positional args: Range, Reference, Text
                # Use \r instead of \n to force true paragraph breaks in Word
                safe_note = str(note).replace("\n", "\r")
                document.Footnotes.Add(rng, "", safe_note)
        
        # Enforce strict formatting for all footnotes
        for i in range(1, document.Footnotes.Count + 1):
            fn = document.Footnotes(i)
            fn.Range.Font.Name = "Arial Narrow"
            fn.Range.Font.Size = 8
            fn.Range.ParagraphFormat.Alignment = 3  # wdAlignParagraphJustify
            
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
