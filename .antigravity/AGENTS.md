# ANCLAJE OBLIGATORIO

**No hay reglas en este archivo. Están todas en `AGENTS.md`, en la raíz de este
repositorio, y es el único sitio donde viven.**

Si estás leyendo esto desde fuera del repositorio, o tu carpeta de trabajo no es
la raíz de `SystemHope-ResAdmis`, **detente**: vas a redactar resoluciones
administrativas sin las directivas que las gobiernan.

    Antigravity  →  Add Workspace  →  la raíz de este repositorio

Comprobación antes de empezar:

    python scripts/comprobar_anclaje.py

Un archivo de redirección solo funciona si el agente lo lee y lo obedece, y eso
es justo lo que no se puede dar por hecho. Por eso el flujo real no depende de
este aviso: `scripts/admisorio.py preparar` llama a la comprobación y **se
detiene** si no estás anclado.
