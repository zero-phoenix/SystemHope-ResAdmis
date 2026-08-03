import os
import subprocess
import sys
import json
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Uso: python orquestador.py <ruta_json>")
        sys.exit(1)
        
    json_path = Path(sys.argv[1]).resolve()
    if not json_path.exists():
        print(f"Error: No se encontró el archivo JSON {json_path}")
        sys.exit(1)

    print("Fase E_JSON: Validando y recargando JSON en UTF-8 estricto...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            caso = json.load(f)
        # Re-save to guarantee utf-8
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(caso, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error parseando o guardando JSON: {e}")
        sys.exit(1)

    print("Fase F_CLEANUP: Purgando procesos zombie WINWORD.EXE...")
    os.system("taskkill /F /IM WINWORD.EXE /T >nul 2>&1")

    base_dir = Path(__file__).resolve().parent
    build_script = base_dir / "automatizacion_antigravity" / "build.py"
    insert_script = base_dir / "automatizacion_antigravity" / "insert_footnotes.py"
    
    # We output to output/ or productos (resoluciones) elaborada por google antigravity/
    output_dir = base_dir / "productos (resoluciones) elaborada por google antigravity"
    output_dir.mkdir(parents=True, exist_ok=True)
    expediente_safe = caso.get("expediente", "default").replace("/", "_").replace(" ", "_")
    output_docx = output_dir / f"{expediente_safe}_FINAL.docx"

    print(f"Fase G_EXEC & H_BUILD: Ejecutando build.py vía subprocess.Popen...")
    try:
        # Popen isolates execution
        proc_build = subprocess.Popen(
            [sys.executable, str(build_script), str(json_path), str(output_docx)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc_build.communicate()
        if proc_build.returncode != 0:
            print("Error en build.py:")
            print(out)
            print(err)
            sys.exit(1)
        print("build.py ejecutado con éxito.")
    except Exception as e:
        print(f"Excepción llamando a build.py: {e}")
        sys.exit(1)

    print(f"Fase I, J, K (COM Interop): Ejecutando insert_footnotes.py vía subprocess.Popen...")
    try:
        proc_com = subprocess.Popen(
            [sys.executable, str(insert_script), str(output_docx)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc_com.communicate()
        if proc_com.returncode != 0:
            print("Error en insert_footnotes.py:")
            print(out)
            print(err)
            sys.exit(1)
        print("insert_footnotes.py ejecutado con éxito.")
    except Exception as e:
        print(f"Excepción llamando a insert_footnotes.py: {e}")
        sys.exit(1)

    print("--- ORQUESTACIÓN COMPLETADA ---")
    print(f"Documento final en: {output_docx}")

if __name__ == "__main__":
    main()
