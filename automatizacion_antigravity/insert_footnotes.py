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
                # Use \r\t instead of \n to force true paragraph breaks AND insert a tab for the hanging indent
                # We also prepend a \t so the first line has a tab after the footnote reference
                safe_note = "\t" + str(note).replace("\n", "\r\t")
                document.Footnotes.Add(rng, "", safe_note)
        
        # Enforce strict formatting for all footnotes
        for i in range(1, document.Footnotes.Count + 1):
            fn = document.Footnotes(i)
            fn.Range.Font.Name = "Arial Narrow"
            fn.Range.Font.Size = 8
            
            for p in fn.Range.Paragraphs:
                # In VBA, indents are measured in points, not twips!
                # 1 cm = 28.35 points
                p.Format.LeftIndent = 28.35
                p.Format.FirstLineIndent = -28.35
                p.Format.Alignment = 3  # wdAlignParagraphJustify
                
                text = p.Range.Text.strip()
                if text.startswith("LEY ") or text.startswith("Artículo "):
                    p.Range.Font.Bold = True
            
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
