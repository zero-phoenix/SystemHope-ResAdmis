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
                # Split by \n, strip leading spaces/tabs, and prepend \t to force alignment at 1cm
                lines = ["\t" + line.lstrip(" \t") for line in str(note).split("\n")]
                # Use \r to separate paragraphs in Word COM
                safe_note = "\r".join(lines)
                
                # Insert the footnote
                document.Footnotes.Add(rng, "", safe_note)
        
        # Enforce strict formatting for all footnotes
        for i in range(1, document.Footnotes.Count + 1):
            fn = document.Footnotes(i)
            fn.Range.Font.Name = "Arial Narrow"
            fn.Range.Font.Size = 8
            
            for p in fn.Range.Paragraphs:
                # In VBA, indents are measured in points, not twips!
                # 1 cm = 28.35 points
                # For footnotes, the footnote reference marker pushes the first line.
                # Standard hanging indent for footnotes: LeftIndent = 1cm, FirstLineIndent = -1cm
                p.Format.LeftIndent = 28.35
                p.Format.FirstLineIndent = -28.35
                
                # We need to insert a tab after the footnote reference to jump to the 1cm mark.
                # Word automatically inserts a space by default after the footnote number, 
                # but we want a tab for perfect alignment. 
                # Note: this is handled natively by Word if we just let the LeftIndent handle it,
                # but to ensure text starts at the indent, we make sure there is a tab after the reference marker.
                # Actually, the best way to align footnotes is to set a tab stop at 28.35
                p.Format.TabStops.ClearAll()
                p.Format.TabStops.Add(Position=28.35, Alignment=0) # wdAlignTabLeft
                p.Format.Alignment = 3  # wdAlignParagraphJustify
                
                import re
                text = p.Range.Text
                # We format the entire paragraph to NOT be bold initially, to clear any inherited styles
                p.Range.Font.Bold = False
                
                # Check if paragraph contains "LEY ", "Artículo ", or "DECRETO " anywhere to apply bolding.
                # Footnote first line starts with \x02 (Footnote reference) and potentially spaces/tabs.
                # We strip all control characters, spaces, and tabs from the start of the string to evaluate correctly.
                clean_text = re.sub(r'^[\x00-\x20]+', '', text)
                
                if clean_text.startswith("LEY ") or clean_text.startswith("Artículo ") or clean_text.startswith("DECRETO ") or clean_text.startswith("TEXTO ÚNICO ORDENADO"):
                    # The rule is that the *title* of the law or article is bolded.
                    # Since these titles usually take up the whole paragraph in our JSON, we bold the whole paragraph.
                    p.Range.Font.Bold = True
            
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
