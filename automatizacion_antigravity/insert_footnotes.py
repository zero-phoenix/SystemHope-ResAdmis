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
                document.Footnotes.Add(rng, "", str(note))
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
