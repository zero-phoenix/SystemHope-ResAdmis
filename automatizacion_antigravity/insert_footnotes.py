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
                # Clean up any manual spaces/tabs in the JSON to guarantee uniform alignment
                lines = str(note).split("\n")
                clean_lines = ["\t" + line.lstrip(" \t") for line in lines]
                # Use \r to separate paragraphs in Word COM
                safe_note = "\r".join(clean_lines)
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
                # We format the entire paragraph to NOT be bold initially, to clear any inherited styles
                p.Range.Font.Bold = False
                
                # Check if paragraph contains "LEY ", "Artículo ", or "DECRETO " anywhere to apply bolding.
                # In the user's example, "LEY 29571..." is bold, and "Artículo 110.-..." is bold,
                # but the following text "El órgano resolutivo puede sancionar..." is not bold.
                if text.startswith("LEY ") or text.startswith("Artículo ") or text.startswith("DECRETO ") or text.startswith("TEXTO ÚNICO ORDENADO"):
                    # The rule is that the *title* of the law or article is bolded.
                    # Since these titles usually take up the whole paragraph in our JSON, we bold the whole paragraph.
                    p.Range.Font.Bold = True
            
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
