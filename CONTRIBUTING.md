# Cómo contribuir a SystemHope ResAdmis

1. **Reglas**: solo se cambian en `AGENTS.md` (vigente, < 12 000 caracteres) y se registran en `CHANGELOG.md` y `automatizacion_antigravity/REGLAS_DE_APRENDIZAJE.md`. Una regla sin cifra del corpus o sin mandato del instructor es una opinión.
2. **Cada regla nueva lleva su falsador** en `scripts/verificar_admisorio.py` y su mutación en `scripts/prueba_verificador.py`: la regla debe rechazar el error que prohíbe.
3. **Datos personales**: el repositorio es público. Nunca se suben expedientes, cédulas, padrones ni mapas de caso; la guardia (`scripts/guardia_admisorio.py`, hook de pre-commit y `admisorio_gate.yml`) los bloquea.
4. **Antes de un commit**:

```bash
pip install -r requirements.txt
python scripts/autocomprobacion.py
python scripts/prueba_verificador.py
python -m compileall -q scripts src
```

5. **Plantillas**: solo entran admisorios corregidos por el instructor, anonimizados y verificados (flujo de incorporación: parte 3 del plan v3).

Repositorio: https://github.com/zero-phoenix/SystemHope-ResAdmis
