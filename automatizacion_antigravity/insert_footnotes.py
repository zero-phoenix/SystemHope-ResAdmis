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
    
    # CRITICAL: Disable AutoFormat to prevent Word from converting "a.", "1.", etc. into Lists
    word.Options.AutoFormatAsYouTypeApplyBulletedLists = False
    word.Options.AutoFormatAsYouTypeApplyNumberedLists = False
    
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
                import re
                lines = []
                for line in str(note).split("\n"):
                    clean = line.lstrip(" \t")
                    # ====================================================================
                    # REGLA ABSOLUTA PARA EVITAR EL AUTOFORMATO DE WORD EN LISTAS (PIES DE PÁGINA)
                    # ====================================================================
                    # Meta-análisis del problema: 
                    # Al inyectar texto vía COM en los pies de página, Word aplica AutoFormato.
                    # Si detecta "a. " o "a) ", lo convierte en una lista. Al hacerlo párrafo por 
                    # párrafo, reinicia la numeración, convirtiendo "a, b, c" en "a, a, a".
                    # Intentos fallidos previos: 
                    # 1. Usar espacios invisibles (\u200B) o Non-Breaking Spaces (\xA0): Word los ignora.
                    # 2. Usar ListFormat.RemoveNumbers(): Borra la viñeta, dejando solo el texto.
                    # 3. Leer ListString y reinsertar: Reinserta "a." en todos porque la lista se reinicia.
                    # 4. Usar Zero-Width Joiner (\u200D): Word también lo ignora al detectar el patrón.
                    #
                    # SOLUCIÓN DEFINITIVA: 
                    # Reemplazar el carácter desencadenante ('.' o ')') por un "One Dot Leader" (U+2024).
                    # Visualmente es idéntico a un punto ('․' vs '.'), pero el motor de Word no lo 
                    # reconoce como viñeta, bloqueando completamente la creación de la lista.
                    # ====================================================================
                    match = re.match(r'^([a-zA-Z0-9]+)([.)]) ', clean)
                    if match:
                        clean = f"{match.group(1)}\u2024 {clean[match.end():]}"
                    lines.append(clean)
                
                # Prepend \t ONLY to the first line, so the footnote marker jumps to the hanging indent
                safe_note = "\t" + lines[0]
                if len(lines) > 1:
                    safe_note += "\r" + "\r".join(lines[1:])
                
                # Insert the footnote
                document.Footnotes.Add(rng, "", safe_note)
        
        # Enforce strict formatting for all footnotes
        for i in range(1, document.Footnotes.Count + 1):
            fn = document.Footnotes(i)
            fn.Range.Font.Name = "Arial Narrow"
            fn.Range.Font.Size = 8
            
            paragraphs_count = fn.Range.Paragraphs.Count
            for j, p in enumerate(fn.Range.Paragraphs):
                # Remove any list formatting just in case
                p.Range.ListFormat.RemoveNumbers()
                
                print(f"DEBUG {j} AFTER REMOVENUMBERS: {repr(p.Range.Text[:40])}")
                
                # Eradicate any leading tabs or spaces Word might have mysteriously inherited
                import re
                text = p.Range.Text
                if j > 0:
                    clean_start = re.sub(r'^[\x00-\x20]+', '', text)
                    if clean_start != text:
                        diff = len(text) - len(clean_start)
                        rng_del = p.Range.Duplicate
                        rng_del.End = rng_del.Start + diff
                        rng_del.Text = ""
                        
                print(f"DEBUG {j} AFTER CLEAN: {repr(p.Range.Text[:40])}")
                
                # In VBA, indents are measured in points, not twips! 1 cm = 28.35 points
                if j == 0:
                    # First paragraph has the footnote marker
                    p.Format.LeftIndent = 28.35
                    p.Format.FirstLineIndent = -28.35
                    # Need a tab to jump from marker to 1cm
                    p.Format.TabStops.ClearAll()
                    p.Format.TabStops.Add(Position=28.35, Alignment=0)
                else:
                    # Subsequent paragraphs don't have a marker, just indent the whole block to 1cm
                    p.Format.LeftIndent = 28.35
                    p.Format.FirstLineIndent = 0
                    
                p.Format.Alignment = 3  # wdAlignParagraphJustify
                
                if j == paragraphs_count - 1:
                    p.Format.SpaceAfter = 10
                else:
                    p.Format.SpaceAfter = 0
                
                import re
                text = p.Range.Text
                # We format the entire paragraph to NOT be bold initially, to clear any inherited styles
                p.Range.Font.Bold = False
                
                # Footnote first line starts with \x02 (Footnote reference) and potentially spaces/tabs.
                clean_text = re.sub(r'^[\x00-\x20]+', '', text)
                
                if clean_text.startswith("LEY ") or clean_text.startswith("DECRETO ") or clean_text.startswith("TEXTO ÚNICO ORDENADO"):
                    p.Range.Font.Bold = True
                elif clean_text.startswith("Artículo "):
                    clean_for_end = clean_text.strip()
                    # If it's short or doesn't end with a period, it's just a title, bold the whole paragraph
                    if len(clean_for_end) < 100 or not clean_for_end.endswith("."):
                        p.Range.Font.Bold = True
                    else:
                        # It contains the text of the article. Bold ONLY the "Artículo XX.-" prefix!
                        match = re.search(r'^(?:[\x00-\x20]*)Artículo\s+\d+(?:[.-]+)?', text)
                        if match:
                            rng_bold = p.Range.Duplicate
                            rng_bold.End = p.Range.Start + match.end()
                            rng_bold.Font.Bold = True
            
        # Llamamos a nuestra rutina de limpieza en la etapa final
        from aplicar_reglas_base import aplicar_reglas_base_win32com
        aplicar_reglas_base_win32com(document)
            
        document.SaveAs(str(output_path))
    finally:
        document.Close()
        word.Quit()
    return True
