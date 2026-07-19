# Guía de Contribución - ResAdmi

¡Gracias por tu interés en contribuir a ResAdmi! Este documento proporciona directrices para contribuir.

## 📋 Código de Conducta

Por favor, sé respetuoso con otros contribuyentes y mantén la profesionalidad.

## 🚀 Cómo Contribuir

### 1. Reportar Bugs

**Antes de reportar**, verifica que el bug no haya sido reportado anteriormente.

Incluye en tu reporte:
- Descripción clara del problema
- Steps específicos para reproducir
- Comportamiento esperado vs. actual
- Tu entorno (OS, Python version, Word version)
- Logs/traceback si aplica

### 2. Sugerir Mejoras

Usa Issues con el tag `enhancement` para:
- Nuevas funcionalidades
- Mejoras de rendimiento
- Cambios de UI/UX
- Optimizaciones

Describe:
- El problema que resuelve
- Solución propuesta
- Beneficios esperados
- Posibles alternativas

### 3. Pull Requests

#### Preparación

```bash
# 1. Fork y clonar
git clone https://github.com/tu-usuario/ResAdmi.git
cd ResAdmi

# 2. Crear rama
git checkout -b feature/nombre-descriptivo

# 3. Instalar en modo desarrollo
pip install -r requirements.txt
pip install pre-commit
pre-commit install
```

#### Desarrollo

```bash
# 4. Hacer cambios, siguiendo estilo del proyecto
# - Usa type hints
# - Escribe docstrings
# - Mantén líneas < 100 caracteres

# 5. Tests (si aplica)
pytest tests/ -v
pytest tests/ --cov=scripts/

# 6. Formatos y linting
black scripts/
flake8 scripts/

# 7. Commit con mensajes claros
git commit -m "feat: agregar validación de artículos"
git commit -m "fix: corregir alineación de tablas"
```

#### Mensaje de Commit

Sigue [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: agregar nueva funcionalidad
fix: corregir bug específico
docs: actualizar documentación
refactor: reorganizar código sin cambiar lógica
test: agregar o actualizar tests
chore: cambios de configuración, dependencias
```

#### Envío de PR

```bash
# 8. Push a tu fork
git push origin feature/nombre-descriptivo

# 9. Abre Pull Request en GitHub con:
# - Título descriptivo
# - Descripción de cambios
# - Reference a issues relacionados (#123)
# - Screenshots si aplica (cambios visuales)
```

#### Checkpoints de Revisión

Tu PR será revisada por:
- ✅ Tests unitarios pasan
- ✅ Cobertura > 80%
- ✅ Sin linting errors
- ✅ Documentación actualizada
- ✅ Compatible con Python 3.8+

---

## 📐 Estándares de Código

### Estructura de Funciones

```python
def generar_resolucion(
    expediente: str,
    denunciante: str,
    denunciado: str,
    hechos: List[str],
    *,
    template_path: Optional[str] = None,
) -> str:
    """
    Genera una resolución administrativa basada en los datos proporcionados.
    
    Args:
        expediente: Número de expediente (ej: "2190-2026")
        denunciante: Nombre completo del denunciante
        denunciado: Nombre de la empresa/organización denunciada
        hechos: Lista de hechos alegados
        template_path: Ruta opcional a plantilla personalizada
        
    Returns:
        Ruta del documento generado
        
    Raises:
        ValueError: Si datos requeridos están faltando
        FileNotFoundError: Si la plantilla no existe
        
    Example:
        >>> doc = generar_resolucion(
        ...     expediente="2190-2026",
        ...     denunciante="Juan Pérez",
        ...     denunciado="Empresa XYZ",
        ...     hechos=["Primer hecho", "Segundo hecho"]
        ... )
        >>> print(doc)
        '/output/ADM_2190-2026_v1.docx'
    """
    # Implementación
```

### Type Hints

```python
from typing import List, Optional, Dict, Tuple

def procesar_documento(
    archivo: str,
    options: Optional[Dict[str, str]] = None,
) -> Tuple[bool, str]:
    pass
```

### Docstrings

Usa Google style:

```python
def metodo_importante(param1: str, param2: int) -> bool:
    """Descripción corta en una línea.
    
    Descripción más larga explicando el propósito,
    el contexto y cualquier consideración importante.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
        
    Returns:
        True si operación exitosa, False en caso contrario
        
    Raises:
        ValueError: Si param2 es negativo
        
    Note:
        Notas adicionales importantes aquí
    """
```

---

## 🧪 Testing

### Estructura de Tests

```
tests/
├── __init__.py
├── test_builder.py
├── test_validator.py
├── test_docx_handler.py
└── fixtures/
    └── sample_templates/
```

### Escribir Tests

```python
import pytest
from scripts.builder import DocumentBuilder

class TestDocumentBuilder:
    @pytest.fixture
    def builder(self):
        """Fixture para crear instancia de builder"""
        return DocumentBuilder(template_path="tests/fixtures/template.docx")
    
    def test_generar_documento_exitoso(self, builder):
        """Verifica generación básica de documento"""
        resultado = builder.build(
            expediente="2190-2026",
            denunciante="Test User",
            denunciado="Test Company",
            hechos=["Hecho 1"]
        )
        assert resultado is not None
        assert resultado.endswith(".docx")
    
    @pytest.mark.parametrize("article", [24])
    def test_prohibido_articulo_24(self, builder, article):
        """Verifica que artículo 24 está prohibido"""
        with pytest.raises(ValueError):
            builder.validate_article(article)
```

### Ejecutar Tests

```bash
# Tests rápidos
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=scripts/ --cov-report=html

# Test específico
pytest tests/test_builder.py::TestDocumentBuilder::test_generar_documento_exitoso -v

# Con output verboso
pytest tests/ -vv -s
```

---

## 📝 Documentación

### Actualizar Docs

Si cambias funcionalidad, actualiza:

1. **Docstrings** en el código
2. **README.md** si es feature visible
3. **CHANGELOG.md** con tus cambios
4. **Archivos de guía** en `docs/`

### Formato de Documentación

- Usa Markdown
- Máximo 100 caracteres por línea (excepto URLs)
- Secciones con headers H2-H4 (`##`, `###`, `####`)
- Código en bloques ` ``` `

---

## 🔄 Proceso de Revisión

1. **Automático:** GitHub Actions ejecuta tests
2. **Automático:** Pre-commit hooks validan código
3. **Manual:** Mantenedores revisan cambios
4. **Feedback:** Se sugieren mejoras si aplica
5. **Merge:** Si todo está OK, se mergea y publica

---

## 📌 Áreas de Contribución Activas

Estas son áreas donde se necesita ayuda:

- [ ] Tests adicionales (cobertura > 90%)
- [ ] Documentación mejorada
- [ ] Refactoring de scripts antiguos
- [ ] Soporte Linux/Mac
- [ ] Integración con CI/CD
- [ ] Validadores adicionales
- [ ] Ejemplos de uso
- [ ] Traducción de docs

---

## ❓ Preguntas?

- 💬 [Discussiones en GitHub](https://github.com/davidchaveznge-wq/ResAdmi/discussions)
- 📧 Email: (disponible pronto)
- 🐛 [Issues](https://github.com/davidchaveznge-wq/ResAdmi/issues)

---

## ✨ ¡Gracias!

Tus contribuciones hacen a ResAdmi mejor. ¡Apreciamos tu tiempo y esfuerzo!

---

**Última actualización:** Julio 2026
