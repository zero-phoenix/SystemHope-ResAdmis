#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regresiones R-212, sin escribir documentos ni tocar expedientes.

    python scripts/prueba_traslado.py
    python scripts/prueba_traslado.py --corpus

--corpus mide las plantillas vigentes por lectura de sus ZIP; no las migra.
"""
from __future__ import annotations

import json
import sys
import unittest
import zipfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

import admisorio
import prueba_verificador as PV
import verificar_admisorio as V
from migraciones import traslado_denuncia as TD

CITA = (
    "denuncia del 30 de abril de 2026, subsanada mediante escrito del 7 de setiembre de 2026"
    " y complementada mediante escrito del 8 de setiembre de 2026"
)
INADMISIBILIDAD = "PRIMERO: dejar sin efecto la inadmisibilidad declarada mediante Resolución 1."
CONFIDENCIALIDAD = "PRIMERO: calificar como confidencial la información presentada."
CASO = {
    "escritos": [
        {"tipo": "denuncia", "fecha": "30 de abril de 2026"},
        {"tipo": "subsanación", "fecha": "7 de setiembre de 2026"},
        {"tipo": "complemento", "fecha": "8 de setiembre de 2026"},
    ]
}


def admision(ordinal="SEGUNDO", cita=CITA):
    return ordinal + ": admitir a trámite la " + cita + ", interpuesta por la señora Prueba contra Aseguradora Ejemplo S.A."


def traslado(cita=CITA):
    return "CUARTO: correr traslado de la " + cita + " a Aseguradora Ejemplo S.A. para que, de conformidad con lo dispuesto por el artículo 26."


def xml(textos):
    return "<w:document>" + "".join("<w:p><w:r><w:t>" + TD.T.escapar(t) + "</w:t></w:r></w:p>" for t in textos) + "</w:document>"


def textos_xml(x):
    return [TD.T.texto(m.group(0)) for m in TD.T.N.RE_P.finditer(x)]


def fallos(textos):
    return V.prueba_r212_traslado_de_la_denuncia([SimpleNamespace(texto=t) for t in textos])


class Traslado(unittest.TestCase):
    def test_ordinal_especial_conservado_y_migracion_idempotente(self):
        for anteriores, ordinal in [
            ([INADMISIBILIDAD], "SEGUNDO"),
            ([CONFIDENCIALIDAD], "SEGUNDO"),
            ([INADMISIBILIDAD, CONFIDENCIALIDAD.replace("PRIMERO", "SEGUNDO")], "TERCERO"),
        ]:
            with self.subTest(anteriores=anteriores):
                inicial = xml(anteriores + [admision(ordinal), traslado("presente resolución")])
                migrado, n, falta = TD.migrar_xml(inicial)
                ps = textos_xml(migrado)
                self.assertEqual((n, falta), (1, False))
                self.assertEqual(ps[:len(anteriores)], anteriores)
                self.assertEqual(TD.cita_denuncia(migrado), CITA)
                self.assertEqual(fallos(ps), [])
                self.assertEqual(TD.migrar_xml(migrado), (migrado, 0, False))

    def test_mutaciones_rechazadas_y_admision_intacta(self):
        for escrito in ["subsanad", "complementad"]:
            for cambiar_fecha in [False, True]:
                with self.subTest(escrito=escrito, cambiar_fecha=cambiar_fecha):
                    original = xml([INADMISIBILIDAD, admision(), traslado()])
                    mutante = PV.mutar_escrito_traslado(original, escrito, cambiar_fecha)
                    self.assertNotEqual(mutante, original)
                    self.assertEqual(textos_xml(mutante)[:2], [INADMISIBILIDAD, admision()])
                    self.assertTrue(fallos(textos_xml(mutante)))

    def test_cita_truncada_no_pasa_como_subcadena(self):
        self.assertTrue(fallos([admision(), traslado("denuncia del 30 de abril de 2026")]))

    def test_escrito_presentado_el_es_cita_y_no_terminador(self):
        cita = (
            "denuncia del 28 de agosto de 2026, subsanada mediante escrito"
            " presentado el 7 de setiembre de 2026"
        )
        self.assertEqual(TD.cita_admision(admision(cita=cita)), cita)
        self.assertEqual(fallos([admision(cita=cita), traslado(cita)]), [])
        self.assertTrue(
            fallos(
                [
                    admision(cita=cita),
                    traslado("denuncia del 28 de agosto de 2026, subsanada mediante escrito"),
                ]
            )
        )

    def test_espacios_de_maquetacion_no_cambian_cita(self):
        self.assertEqual(fallos([admision(), traslado(CITA.replace("mediante", "  mediante\u00a0"))]), [])

    def test_cita_no_extraible_no_se_aprueba(self):
        self.assertTrue(fallos([INADMISIBILIDAD, traslado()]))
        self.assertTrue(fallos([admision(), "CUARTO: correr traslado de documentos a Aseguradora Ejemplo S.A."]))

    def test_fechas_caso_en_ordinal_admision(self):
        apertura = "Mediante el escrito de " + CITA + ", la señora Prueba denunció."
        for anteriores, ordinal in [
            ([INADMISIBILIDAD], "SEGUNDO"),
            ([CONFIDENCIALIDAD], "SEGUNDO"),
            ([INADMISIBILIDAD, CONFIDENCIALIDAD.replace("PRIMERO", "SEGUNDO")], "TERCERO"),
        ]:
            with self.subTest(ordinal=ordinal, anteriores=anteriores):
                ps = [apertura] + anteriores + [admision(ordinal)]
                self.assertEqual(admisorio._control_fechas_escritos(CASO, ps), [])
                ps[-1] = admision(ordinal, "denuncia del 30 de abril de 2026")
                errores = admisorio._control_fechas_escritos(CASO, ps)
                self.assertEqual(len(errores), 2)
                self.assertTrue(all("ordinal de admision" in e for e in errores))

    def test_setiembre_y_septiembre_son_la_misma_fecha(self):
        caso = {"escritos": [{"tipo": "subsanacion", "fecha": "4 de setiembre de 2026"}]}
        ps = [
            "Mediante el escrito del 29 de julio de 2026, subsanado mediante escrito del"
            " 4 de septiembre de 2026, el señor Prueba denunció.",
            "PRIMERO: admitir a trámite la denuncia del 29 de julio de 2026, subsanada"
            " mediante escrito del 4 de septiembre de 2026, interpuesta por el señor Prueba.",
        ]
        self.assertEqual(admisorio._control_fechas_escritos(caso, ps), [])


def medir_corpus():
    conteos, ordinales = Counter(), Counter()
    for p in sorted((RAIZ / "plantillas_maestras").rglob("*.docx")):
        with zipfile.ZipFile(p) as z:
            x = z.read("word/document.xml").decode("utf-8")
        ts = textos_xml(x)
        conteos["plantillas"] += 1
        adm = next((t for t in ts if TD.cita_admision(t)), "")
        if not adm:
            conteos["sin_cita_extraible"] += 1
            continue
        ordinal = adm.partition(":")[0].strip()
        ordinales[ordinal] += 1
        conteos["admision_no_primero"] += ordinal != "PRIMERO"
        cita = TD.cita_admision(adm)
        conteos["citas_compuestas"] += "subsanad" in cita or "complement" in cita
        conteos["rechazadas_r212"] += bool(fallos(ts))
    print(json.dumps({"conteos": dict(conteos), "ordinal_admision": dict(ordinales)}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    corpus = "--corpus" in sys.argv
    if corpus:
        sys.argv.remove("--corpus")
    resultado = unittest.main(exit=False)
    if corpus:
        medir_corpus()
    raise SystemExit(not resultado.result.wasSuccessful())
