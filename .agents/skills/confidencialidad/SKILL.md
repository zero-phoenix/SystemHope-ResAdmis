---
name: confidencialidad
description: Redactar un admisorio CC1 que además resuelve una solicitud de confidencialidad de información presentada por una parte (subtipo confidencialidad, 23 plantillas del corpus).
---

# Admisorio con confidencialidad

## Cuándo aplica
Solo cuando el expediente trae una solicitud de confidencialidad, o cuando hay información sensible (por ejemplo, datos de salud) que la Secretaría Técnica califica de oficio. Si no, **no** se usa este subtipo.

## Instrucciones
1. `scripts/admisorio.py preparar <carpeta> --subtipo confidencialidad ...` Elige una candidata APTA de la misma rama y con el mismo número de denunciados.
2. Encabezado: `MATERIAS: CONFIDENCIALIDAD` más las materias de admisión. La resolución lleva su número propio con el formato del corpus (`RESOLUCIÓN : 0090-2026/CC1-ST`).
3. Antes de la admisión va la sección «DE LA SOLICITUD DE CONFIDENCIALIDAD PRESENTADA». Conserva de la plantilla, sin alterar:
   - el marco normativo: artículo 6 del Decreto Legislativo 807 y Directiva 001-2008/TRI-INDECOPI, con sus modificatorias;
   - los requisitos del numeral 3.2;
   - la Directiva 001-2025-GEG/INDECOPI sobre el expediente electrónico.

   Después:
   - narra quién presentó qué documento y cuándo, con su nombre literal entre comillas;
   - evalúa los cinco requisitos;
   - declara, frente a quién y por cuánto tiempo.
4. **PRIMERO** resuelve la confidencialidad: «calificar como confidencial, frente a terceros ajenos al procedimiento, la información presentada por [tratativa] con su escrito de … del [fecha], la cual obra en el documento [n] denominado “[NOMBRE]”, de la pieza [n] del expediente, presentado el [fecha]; precisándose que la confidencialidad declarada deberá mantenerse permanentemente.» También existe la variante «calificar, de oficio, como confidencial…».
5. **SEGUNDO** admite la denuncia, con las imputaciones de siempre. Los demás ordinales corren un lugar.
6. Si el documento se remitió a la contraparte, **no** es confidencial frente a ella; solo frente a terceros.

## Restricciones
- No inventes números de pieza ni nombres de documento: salen del expediente.
- No copies los datos sensibles en la resolución. Se describen, por ejemplo: «información referida a la salud personal».
