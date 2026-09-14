import zipfile
import re
from pathlib import Path
from collections import Counter, defaultdict

base_dir = Path(r"C:\Users\D\ZCodeProject\SystemHope-ResAdmis\plantillas_maestras")
docs = list(base_dir.glob("**/*.docx"))

# 1. Denominaciones
denominaciones_personas = Counter()
denominaciones_empresas = Counter()

# 2. Espejo Considerativa vs Resolutiva
coincidencias_imputacion = []

# 3. Notificación con domicilio compartido
notif_compartidas = []
notif_individuales = []

# 4. Requerimientos
requerimientos_incisos = Counter()
requerimientos_verbos = Counter()

for f in docs[:150]:  # Muestra robusta de 150 modelos
    try:
        with zipfile.ZipFile(f) as z:
            doc_xml = z.read("word/document.xml").decode("utf-8") if "word/document.xml" in z.namelist() else ""
            
            # Limpiar XML a texto por párrafos
            paras_xml = re.findall(r'<w:p[^>]*>(.*?)</w:p>', doc_xml, re.DOTALL)
            paras = [re.sub(r'<[^>]+>', ' ', p).strip() for p in paras_xml]
            paras = [re.sub(r'\s+', ' ', p) for p in paras if p]
            
            # --- 1. Denominación en Hechos ---
            for p in paras:
                if p.startswith("1. Mediante") or p.startswith("Mediante"):
                    m_sr = re.search(r'\b(el señor|la señora|los señores|la sucesión|el denunciante|la denunciante)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)*)', p, re.IGNORECASE)
                    if m_sr:
                        denominaciones_personas[m_sr.group(1).lower()] += 1
                        
            # --- 2. Comparar Considerativa (Sec II) vs Resolutiva (PRIMERO) ---
            # Buscar "consistente en que" en Sec II
            hecho_considerativa = ""
            for p in paras:
                if "involucraría una presunta afectación" in p or "consistente en que" in p and "calificar el hecho" in p:
                    m_c = re.search(r'consistente en que\s+(.*?)(?:,\s+lo que|\s+involucraría|\.\s+Por consiguiente)', p, re.IGNORECASE)
                    if m_c:
                        hecho_considerativa = m_c.group(1).strip()
                        break
            
            hecho_resolutiva = ""
            for p in paras:
                if p.startswith("PRIMERO:") and "consistente en que" in p:
                    m_r = re.search(r'consistente en que\s+(.*?)(?:;\s+presunta|\.\s+SEGUNDO|\s+infracción)', p, re.IGNORECASE)
                    if m_r:
                        hecho_resolutiva = m_r.group(1).strip()
                        break
                        
            if hecho_considerativa and hecho_resolutiva:
                # Medir similitud
                coincidencias_imputacion.append({
                    "file": f.name,
                    "considerativa": hecho_considerativa[:120],
                    "resolutiva": hecho_resolutiva[:120],
                    "identicos": hecho_considerativa.lower() == hecho_resolutiva.lower()
                })

            # --- 3. Domicilio Compartido en Resolutivos ---
            for p in paras:
                if any(p.startswith(x) for x in ["OCTAVO:", "NOVENO:", "DÉCIMO:", "UNDÉCIMO:"]):
                    # Verificar si notifica a 2 partes en el mismo parrafo
                    if " y a " in p or " y al " in p:
                        if any(k in p.lower() for k in ["casilla", "correo", "domicilio", "electrónico", "dirección"]):
                            notif_compartidas.append(p[:200])

            # --- 4. Requerimientos de Información ---
            for p in paras:
                if p.startswith("CUARTO:") or p.startswith("QUINTO:") or "REQUERIR a" in p:
                    if "(a)" in p and "(b)" in p:
                        # contar incisos
                        num_inc = len(re.findall(r'\([a-z]\)', p))
                        requerimientos_incisos[num_inc] += 1
                    m_verb = re.search(r'REQUERIR\s+a\s+[^,]+,\s+para\s+que\s+[^,]+,\s+([a-z]+)', p, re.IGNORECASE)
                    if m_verb:
                        requerimientos_verbos[m_verb.group(1).lower()] += 1

    except Exception as e:
        pass

print("=== 1. DENOMINACIONES DE PERSONAS EN HECHOS ===")
for k, v in denominaciones_personas.most_common():
    print(f"  {k}: {v}")

print("\n=== 2. ISOMORFISMO CONSIDERATIVA VS RESOLUTIVA (MUESTRAS) ===")
print(f"Total pares analizados: {len(coincidencias_imputacion)}")
identicos_count = sum(1 for c in coincidencias_imputacion if c['identicos'])
print(f"Identicos al 100%: {identicos_count} / {len(coincidencias_imputacion)} ({identicos_count/max(1, len(coincidencias_imputacion))*100:.1f}%)")
for c in coincidencias_imputacion[:4]:
    print("---")
    print("Considerativa:", c["considerativa"])
    print("Resolutiva:   ", c["resolutiva"])

print("\n=== 3. NOTIFICACIÓN CONJUNTA / DOMICILIO COMPARTIDO (MUESTRAS) ===")
print(f"Total detectados: {len(notif_compartidas)}")
for n in notif_compartidas[:5]:
    print("  *", n)

print("\n=== 4. INCISOS EN REQUERIMIENTOS ===")
for k, v in sorted(requerimientos_incisos.items()):
    print(f"  {k} incisos: {v} casos")

