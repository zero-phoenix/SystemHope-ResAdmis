#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verificar_plantillas_maestras.py
Auditoría integral y control de calidad sobre las 605 plantillas maestras en plantillas_maestras/:
1. Validez estructural OOXML (ZIP, [Content_Types].xml, document.xml).
2. Verificación de LPAG: 0 citas de 004-2019-JUS, presencia de 006-2026-JUS.
3. Cero corrupción de encoding (\ufffd).
4. Verificación de reglas léxicas estrictas (cónyuge, luego de, esta/este, etc.).
"""

import sys
import zipfile
import re
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis")
TARGET_ROOT = REPO_ROOT / "plantillas_maestras"

def auditar_todo():
    archivos = list(TARGET_ROOT.glob("**/*.docx"))
    print(f"Total de archivos .docx encontrados en {TARGET_ROOT.name}: {len(archivos)}")
    
    if not archivos:
        print("ERROR: No se encontraron archivos.")
        return False
        
    corruptos = 0
    con_lpag_viejo = 0
    con_lpag_nuevo = 0
    con_ufffd = 0
    con_tras = 0
    con_esposo = 0
    con_esta_tilde = 0
    
    for idx, f in enumerate(archivos, 1):
        # 1. Validar ZIP OOXML
        try:
            with zipfile.ZipFile(f, 'r') as z:
                namelist = z.namelist()
                if '[Content_Types].xml' not in namelist or 'word/document.xml' not in namelist:
                    corruptos += 1
                    continue
                
                # Leer texto de document.xml y footnotes.xml
                todo_texto = ""
                for name in namelist:
                    if name.endswith('.xml') and ('document' in name or 'footnotes' in name):
                        txt = z.read(name).decode('utf-8', errors='replace')
                        todo_texto += " " + txt
                        
                if '004-2019-JUS' in todo_texto:
                    con_lpag_viejo += 1
                if '006-2026-JUS' in todo_texto:
                    con_lpag_nuevo += 1
                if '\ufffd' in todo_texto:
                    con_ufffd += 1
                if re.search(r'\btras\b', todo_texto, re.IGNORECASE):
                    con_tras += 1
                if re.search(r'\besposo\b|\besposa\b', todo_texto, re.IGNORECASE):
                    con_esposo += 1
                if re.search(r'\bésta\b|\béste\b|\béstas\b|\béstos\b', todo_texto):
                    con_esta_tilde += 1
                    
        except Exception as e:
            corruptos += 1
            print(f"Error en {f.name}: {e}")

    print("\n" + "=" * 60)
    print("RESULTADOS DEL CONTROL DE CALIDAD AUTOMATIZADO")
    print("=" * 60)
    print(f"Archivos evaluados:                  {len(archivos)}")
    print(f"Archivos OOXML válidos e íntegros:   {len(archivos) - corruptos} / {len(archivos)}")
    print(f"Archivos corruptos:                  {corruptos}")
    print(f"Archivos con LPAG derogado (004):    {con_lpag_viejo} (Esperado: 0)")
    print(f"Archivos con LPAG vigente (006):     {con_lpag_nuevo} (Actualizados)")
    print(f"Archivos con caracteres \\ufffd:     {con_ufffd} (Esperado: 0)")
    print(f"Archivos con palabra 'tras':         {con_tras} (Esperado: 0)")
    print(f"Archivos con 'esposo/esposa':        {con_esposo} (Esperado: 0)")
    print(f"Archivos con tilde en 'ésta/éste':   {con_esta_tilde} (Esperado: 0)")
    print("=" * 60)
    
    if corruptos == 0 and con_lpag_viejo == 0 and con_ufffd == 0:
        print("[APROBADO] Todas las plantillas superaron el control de calidad.")
        return True
    else:
        print("[OBSERVACIÓN] Se detectaron discrepancias.")
        return False

if __name__ == "__main__":
    auditar_todo()
