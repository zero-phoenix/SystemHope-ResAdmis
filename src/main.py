"""Interfaz gráfica ResAdmi — GUI minimalista gris/negro con acentos naranja.

Diseño: tema oscuro profesional, tipografía Segoe UI, acentos naranja.
SIN menciones visibles a INDECOPI/CC1 (el dominio se preserva internamente).

Flujo "cero input manual":
- Pestaña Generar: eliges carpeta con PDFs → botón Generar → aparece el .docx.
- Pestaña Chat: conversación para dar contexto adicional.
- Pestaña Aprendizaje: subir modelos reales para extraer reglas.
- Pestaña Ajustes: proveedor IA, plantilla, carpeta de salida.

Thread-safe: las llamadas IA van en hilos separados.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from . import ai_client, aprendizaje_reglas
from .app import generar_desde_carpeta, generar_resolucion
from .config import USER_DIR, Settings


# ---------------------------------------------------------------------------
# Tema minimalista: gris/negro + acentos naranja
# ---------------------------------------------------------------------------

COLOR_BG = "#1a1a1a"           # fondo casi negro
COLOR_SURFACE = "#242424"      # tarjetas gris oscuro
COLOR_SURFACE_2 = "#2d2d2d"    # hover
COLOR_BORDER = "#3a3a3a"       # bordes sutiles
COLOR_TEXT = "#f5f5f5"         # texto blanco roto
COLOR_MUTED = "#a0a0a0"        # gris medio
COLOR_PRIMARY = "#ff8c00"      # naranja (acento principal)
COLOR_PRIMARY_DARK = "#e07b00"
COLOR_ACCENT = "#ffa500"       # naranja claro
COLOR_SUCCESS = "#4ade80"      # verde éxito
COLOR_WARNING = "#fbbf24"      # amarillo
COLOR_DANGER = "#f87171"       # rojo claro
FONT_FAMILY = "Segoe UI"
FONT_FAMILY_MONO = "Cascadia Mono, Consolas"


def aplicar_tema(root: tk.Tk) -> None:
    """Configura el estilo ttk con tema oscuro profesional."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(background=COLOR_BG)

    style.configure(".", font=(FONT_FAMILY, 10), background=COLOR_BG, foreground=COLOR_TEXT)
    style.configure("TFrame", background=COLOR_BG)
    style.configure("Card.TFrame", background=COLOR_SURFACE, relief="flat", borderwidth=0)
    style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=(FONT_FAMILY, 10))
    style.configure("Card.TLabel", background=COLOR_SURFACE, foreground=COLOR_TEXT)
    style.configure("Title.TLabel", font=(FONT_FAMILY, 20, "bold"), foreground=COLOR_PRIMARY, background=COLOR_BG)
    style.configure("Subtitle.TLabel", font=(FONT_FAMILY, 12, "bold"), foreground=COLOR_TEXT, background=COLOR_BG)
    style.configure("Muted.TLabel", font=(FONT_FAMILY, 9), foreground=COLOR_MUTED, background=COLOR_BG)
    style.configure("Hint.TLabel", font=(FONT_FAMILY, 9), foreground=COLOR_MUTED, background=COLOR_SURFACE)
    style.configure("Card.TLabelframe", background=COLOR_SURFACE, foreground=COLOR_ACCENT,
                    font=(FONT_FAMILY, 10, "bold"), borderwidth=1, relief="solid")
    style.configure("Card.TLabelframe.Label", background=COLOR_SURFACE, foreground=COLOR_ACCENT)

    # Botones: naranja principal, gris secundario
    style.configure("TButton", font=(FONT_FAMILY, 10, "bold"), padding=(16, 10),
                    background=COLOR_PRIMARY, foreground="#1a1a1a", borderwidth=0, relief="flat")
    style.map("TButton",
              background=[("active", COLOR_PRIMARY_DARK), ("pressed", COLOR_PRIMARY_DARK)],
              foreground=[("disabled", "#666666")])
    style.configure("Secondary.TButton", background=COLOR_SURFACE_2, foreground=COLOR_TEXT,
                    borderwidth=1, relief="solid")
    style.map("Secondary.TButton",
              background=[("active", COLOR_BORDER)],
              foreground=[("active", COLOR_ACCENT)])
    style.configure("Danger.TButton", background=COLOR_DANGER, foreground="#1a1a1a")
    style.map("Danger.TButton", background=[("active", "#ef4444")])

    # Entries oscuros
    style.configure("TEntry", fieldbackground=COLOR_SURFACE_2, foreground=COLOR_TEXT,
                    borderwidth=1, relief="solid", padding=6)
    style.map("TEntry", fieldbackground=[("focus", COLOR_SURFACE)])
    style.configure("TCombobox", fieldbackground=COLOR_SURFACE_2, foreground=COLOR_TEXT,
                    background=COLOR_SURFACE, padding=6)
    style.map("TCombobox", fieldbackground=[("focus", COLOR_SURFACE)])

    # Notebook
    style.configure("TNotebook", background=COLOR_BG, borderwidth=0, tabmargins=(10, 8, 10, 0))
    style.configure("TNotebook.Tab", font=(FONT_FAMILY, 10, "bold"),
                    background=COLOR_BG, foreground=COLOR_MUTED,
                    padding=(20, 10), borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", COLOR_SURFACE)],
              foreground=[("selected", COLOR_PRIMARY)],
              expand=[("selected", (0, 0, 0, 0))])

    style.configure("Vertical.TScrollbar", background=COLOR_BORDER, troughcolor=COLOR_BG, borderwidth=0)


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------


class ResAdmiApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = Settings.cargar()
        root.title("ResAdmi · Generador de Resoluciones")
        root.geometry("1100x820")
        root.minsize(1000, 700)
        root.configure(bg=COLOR_BG)

        aplicar_tema(root)

        self.chat_historial: list[dict[str, str]] = []

        self._construir_layout()
        self._refrescar_estado_ia()

    # -------------------------------------------------------------- layout
    def _construir_layout(self) -> None:
        # Header minimalista
        header = ttk.Frame(self.root, style="Card.TFrame")
        header.pack(fill="x")
        inner_h = ttk.Frame(header)
        inner_h.pack(fill="x", padx=20, pady=14)
        ttk.Label(inner_h, text="ResAdmi", style="Title.TLabel").pack(side="left")
        ttk.Label(inner_h, text="Generador de resoluciones admisorias",
                  style="Muted.TLabel").pack(side="left", padx=(14, 0), pady=(8, 0))

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(2, 6))

        self.tab_generar = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_chat = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_aprendizaje = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_ajustes = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_generar, text="  🚀  Generar  ")
        self.notebook.add(self.tab_chat, text="  💬  Chat  ")
        self.notebook.add(self.tab_aprendizaje, text="  🎓  Aprendizaje  ")
        self.notebook.add(self.tab_ajustes, text="  ⚙  Ajustes  ")

        self._tab_generar()
        self._tab_chat()
        self._tab_aprendizaje()
        self._tab_ajustes()

        # Footer
        footer = ttk.Frame(self.root)
        footer.pack(fill="x", padx=12, pady=(0, 12))
        self.estado_var = tk.StringVar(value="● Listo.")
        ttk.Label(footer, textvariable=self.estado_var, style="Muted.TLabel").pack(side="left", padx=4)

    # ============================================================
    # PESTAÑA 1: GENERAR (flujo cero input manual)
    # ============================================================
    def _tab_generar(self) -> None:
        tab = self.tab_generar
        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, padx=20, pady=18)

        # Intro
        ttk.Label(container, text="Genera una resolución en 1 clic",
                  style="Subtitle.TLabel").pack(anchor="w")
        ttk.Label(container,
                  text="Arrastra tus PDFs (denuncia, anexos, escritos adicionales) a una carpeta, "
                       "selecciónala aquí y pulsa Generar. La IA con visión lee todo por ti.",
                  style="Muted.TLabel", wraplength=1000, justify="left").pack(anchor="w", pady=(2, 18))

        # Selector de carpeta GRANDE
        drop = ttk.LabelFrame(container, text="  📁  Carpeta con los documentos del expediente  ",
                              style="Card.TLabelframe")
        drop.pack(fill="x", pady=(0, 14))
        df = ttk.Frame(drop)
        df.pack(fill="x", padx=14, pady=14)
        self.var_carpeta_entrada = tk.StringVar()
        ttk.Entry(df, textvariable=self.var_carpeta_entrada, width=72).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(df, text="📂  Examinar...", style="Secondary.TButton",
                   command=self._examinar_carpeta_entrada).pack(side="left")
        self.lbl_docs_detectados = ttk.Label(df, text="", style="Hint.TLabel")
        self.lbl_docs_detectados.pack(anchor="w", pady=(8, 0))

        # Botón GENERAR grande
        btn_frame = ttk.Frame(container)
        btn_frame.pack(fill="x", pady=(0, 14))
        self.btn_generar = ttk.Button(btn_frame, text="⚡  GENERAR RESOLUCIÓN",
                                      command=self._on_generar_desde_carpeta)
        self.btn_generar.pack(fill="x", ipady=10)

        # Reporte
        consola = ttk.LabelFrame(container, text="  Reporte  ", style="Card.TLabelframe")
        consola.pack(fill="both", expand=True)
        fc = ttk.Frame(consola)
        fc.pack(fill="both", expand=True, padx=14, pady=10)
        self.consola = tk.Text(fc, height=10, wrap="word", font=(FONT_FAMILY_MONO, 9),
                               bg=COLOR_SURFACE_2, fg=COLOR_TEXT, relief="flat", borderwidth=0,
                               insertbackground=COLOR_TEXT, selectbackground=COLOR_PRIMARY)
        self.consola.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(fc, command=self.consola.yview, orient="vertical")
        sb.pack(side="right", fill="y")
        self.consola.config(yscrollcommand=sb.set, state="disabled")
        self.consola.tag_config("CRITICA", foreground=COLOR_DANGER,
                                font=(FONT_FAMILY_MONO, 9, "bold"))
        self.consola.tag_config("VALIDABLE", foreground=COLOR_WARNING)
        self.consola.tag_config("OK", foreground=COLOR_SUCCESS,
                                font=(FONT_FAMILY_MONO, 9, "bold"))
        self.consola.tag_config("INFO", foreground=COLOR_MUTED)

    def _examinar_carpeta_entrada(self) -> None:
        path = filedialog.askdirectory(title="Selecciona carpeta con los PDFs del expediente")
        if path:
            self.var_carpeta_entrada.set(path)
            self._actualizar_docs_detectados(path)

    def _actualizar_docs_detectados(self, path: str) -> None:
        try:
            from . import extractor_pdfs
            docs = extractor_pdfs.descubrir_documentos(path)
            n = len(docs)
            if n == 0:
                self.lbl_docs_detectados.config(
                    text="⚠  No se detectaron PDFs ni imágenes en esta carpeta.",
                    foreground=COLOR_WARNING)
            else:
                self.lbl_docs_detectados.config(
                    text=f"✓  {n} documento(s) detectado(s) listo(s) para procesar.",
                    foreground=COLOR_SUCCESS)
        except Exception:
            pass

    def _on_generar_desde_carpeta(self) -> None:
        carpeta = self.var_carpeta_entrada.get().strip()
        if not carpeta or not Path(carpeta).exists():
            messagebox.showerror("Carpeta", "Selecciona una carpeta válida con los PDFs del expediente.")
            return
        if not self.settings.plantilla_maestra or not Path(self.settings.plantilla_maestra).exists():
            messagebox.showerror("Plantilla", "Configura una plantilla .docx en Ajustes.")
            return

        self.btn_generar.config(state="disabled")
        self.estado_var.set("● Procesando documentos... (puede tardar 1-3 minutos)")
        self._log_consola("Iniciando generación desde carpeta...", "INFO")
        threading.Thread(target=self._worker_generar_carpeta, args=(carpeta,), daemon=True).start()

    def _worker_generar_carpeta(self, carpeta: str) -> None:
        try:
            reporte = generar_desde_carpeta(carpeta, self.settings)
            self.root.after(0, lambda: self._mostrar_reporte(reporte))
        except Exception as exc:
            err = f"{exc}"
            self.root.after(0, lambda: self._mostrar_error(err))

    # ============================================================
    # PESTAÑA 2: CHAT
    # ============================================================
    def _tab_chat(self) -> None:
        tab = self.tab_chat
        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, padx=20, pady=18)

        ttk.Label(container, text="Conversación", style="Subtitle.TLabel").pack(anchor="w")
        ttk.Label(container,
                  text="Da contexto adicional al proveedor si lo necesitas. Es opcional.",
                  style="Muted.TLabel").pack(anchor="w", pady=(2, 14))

        hist_frame = ttk.LabelFrame(container, text="  Historial  ", style="Card.TLabelframe")
        hist_frame.pack(fill="both", expand=True, pady=(0, 10))
        hf = ttk.Frame(hist_frame)
        hf.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display = tk.Text(hf, wrap="word", font=(FONT_FAMILY, 10),
                                    bg=COLOR_SURFACE_2, fg=COLOR_TEXT, relief="flat", borderwidth=0,
                                    insertbackground=COLOR_TEXT, selectbackground=COLOR_PRIMARY)
        self.chat_display.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(hf, command=self.chat_display.yview, orient="vertical")
        sb.pack(side="right", fill="y")
        self.chat_display.config(yscrollcommand=sb.set, state="disabled")
        self.chat_display.tag_config("user", foreground=COLOR_PRIMARY,
                                     font=(FONT_FAMILY, 10, "bold"))
        self.chat_display.tag_config("assistant", foreground=COLOR_TEXT)
        self.chat_display.tag_config("system", foreground=COLOR_MUTED, font=(FONT_FAMILY, 9))

        input_frame = ttk.LabelFrame(container, text="  Tu mensaje  ", style="Card.TLabelframe")
        input_frame.pack(fill="x")
        if_container = ttk.Frame(input_frame)
        if_container.pack(fill="x", padx=10, pady=10)
        self.chat_input = tk.Text(if_container, height=4, font=(FONT_FAMILY, 10), wrap="word",
                                  bg=COLOR_SURFACE_2, fg=COLOR_TEXT, relief="flat", borderwidth=0,
                                  insertbackground=COLOR_TEXT)
        self.chat_input.pack(fill="x", side="left", expand=True)
        btns_chat = ttk.Frame(if_container)
        btns_chat.pack(side="right", fill="y", padx=(10, 0))
        ttk.Button(btns_chat, text="Enviar", command=self._on_chat_enviar).pack(fill="x", pady=2)
        ttk.Button(btns_chat, text="Limpiar", style="Secondary.TButton",
                   command=self._on_chat_limpiar).pack(fill="x", pady=2)

    def _on_chat_enviar(self) -> None:
        texto = self.chat_input.get("1.0", "end").strip()
        if not texto:
            return
        self.chat_input.delete("1.0", "end")
        self.chat_historial.append({"role": "user", "content": texto})
        self._render_chat_msg("user", texto)
        self.estado_var.set("● Pensando...")
        threading.Thread(target=self._worker_chat, args=(texto,), daemon=True).start()

    def _worker_chat(self, texto: str) -> None:
        proveedor = self.settings.proveedor_ia
        system_msg = "Eres un asistente experto que ayuda a preparar contexto para generar resoluciones."
        mensajes = [{"role": "system", "content": system_msg}] + self.chat_historial[-10:]
        res = ai_client.chat_conversacional(mensajes, proveedor_id=proveedor)
        if res.ok:
            self.chat_historial.append({"role": "assistant", "content": res.texto})
            self.root.after(0, lambda: self._render_chat_msg("assistant", res.texto))
            self.root.after(0, lambda: self.estado_var.set(f"● Respondido vía {res.proveedor_usado}"))
        else:
            err = res.error
            self.root.after(0, lambda: self._render_chat_msg("system", f"Error: {err}"))
            self.root.after(0, lambda: self.estado_var.set("● Error en chat"))

    def _render_chat_msg(self, role: str, contenido: str) -> None:
        self.chat_display.config(state="normal")
        etiqueta = {"user": "Tú", "assistant": "IA", "system": "Sistema"}[role]
        self.chat_display.insert("end", f"{etiqueta}:\n", role)
        self.chat_display.insert("end", contenido + "\n\n")
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")

    def _on_chat_limpiar(self) -> None:
        self.chat_historial = []
        self.chat_display.config(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.config(state="disabled")
        self.estado_var.set("● Chat limpiado.")

    # ============================================================
    # PESTAÑA 3: APRENDIZAJE
    # ============================================================
    def _tab_aprendizaje(self) -> None:
        tab = self.tab_aprendizaje
        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, padx=20, pady=18)

        ttk.Label(container, text="Mejora continua del sistema",
                  style="Subtitle.TLabel").pack(anchor="w")
        ttk.Label(container,
                  text="Sube modelos de resolución reales y la IA con visión extraerá detalles "
                       "técnicos/estilísticos, proponiendo nuevas reglas automáticamente.",
                  style="Muted.TLabel", wraplength=1000, justify="left").pack(anchor="w", pady=(2, 14))

        upload = ttk.LabelFrame(container, text="  Subir modelo real  ", style="Card.TLabelframe")
        upload.pack(fill="x", pady=(0, 10))
        uf = ttk.Frame(upload)
        uf.pack(fill="x", padx=10, pady=10)
        self.var_modelo_path = tk.StringVar()
        ttk.Entry(uf, textvariable=self.var_modelo_path, width=80).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(uf, text="📂  Examinar", style="Secondary.TButton",
                   command=self._examinar_modelo).pack(side="left")
        ttk.Button(uf, text="🔍  Analizar", command=self._on_analizar_modelo).pack(side="left", padx=(8, 0))
        ttk.Label(uf, text="PDF, JPG, PNG, BMP, WEBP", style="Hint.TLabel").pack(side="left", padx=(14, 0))

        res_frame = ttk.LabelFrame(container, text="  Análisis y reglas propuestas  ", style="Card.TLabelframe")
        res_frame.pack(fill="both", expand=True, pady=(0, 10))
        rf = ttk.Frame(res_frame)
        rf.pack(fill="both", expand=True, padx=10, pady=10)
        self.aprendizaje_display = tk.Text(rf, wrap="word", font=(FONT_FAMILY, 10),
                                           bg=COLOR_SURFACE_2, fg=COLOR_TEXT, relief="flat", borderwidth=0,
                                           insertbackground=COLOR_TEXT)
        self.aprendizaje_display.pack(fill="both", expand=True, side="left")
        sb = ttk.Scrollbar(rf, command=self.aprendizaje_display.yview, orient="vertical")
        sb.pack(side="right", fill="y")
        self.aprendizaje_display.config(yscrollcommand=sb.set, state="disabled")

        bottom = ttk.Frame(container)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="📚  Ver propuestas acumuladas", style="Secondary.TButton",
                   command=self._on_ver_propuestas).pack(side="left")

    def _examinar_modelo(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecciona modelo real",
            filetypes=[("Documentos/imágenes", "*.pdf *.jpg *.jpeg *.png *.bmp *.webp *.gif"),
                       ("Todos", "*.*")],
        )
        if path:
            self.var_modelo_path.set(path)

    def _on_analizar_modelo(self) -> None:
        path = self.var_modelo_path.get().strip()
        if not path or not Path(path).exists():
            messagebox.showerror("Archivo", "Selecciona un archivo válido.")
            return
        self.estado_var.set("● Analizando modelo con visión...")
        threading.Thread(target=self._worker_analizar, args=(path,), daemon=True).start()

    def _worker_analizar(self, path: str) -> None:
        res = aprendizaje_reglas.analizar_modelo(path, proveedor_id=self.settings.proveedor_ia)
        if res.ok:
            try:
                aprendizaje_reglas.guardar_propuesta(res.analisis, path)
            except Exception:
                pass
            texto = res.analisis
            if res.nuevas_reglas:
                texto += "\n\n---\n**Nuevas reglas propuestas:** " + ", ".join(res.nuevas_reglas)
            self.root.after(0, lambda: self._render_aprendizaje(texto))
            self.root.after(0, lambda: self.estado_var.set(
                f"● OK · {res.proveedor_usado} · {len(res.nuevas_reglas)} regla(s) propuesta(s)"))
        else:
            err = res.error
            self.root.after(0, lambda: self._render_aprendizaje(f"Error: {err}"))
            self.root.after(0, lambda: self.estado_var.set("● Error analizando"))

    def _render_aprendizaje(self, texto: str) -> None:
        self.aprendizaje_display.config(state="normal")
        self.aprendizaje_display.delete("1.0", "end")
        self.aprendizaje_display.insert("end", texto)
        self.aprendizaje_display.config(state="disabled")

    def _on_ver_propuestas(self) -> None:
        contenido = aprendizaje_reglas.listar_propuestas()
        self._render_aprendizaje(contenido)

    # ============================================================
    # PESTAÑA 4: AJUSTES
    # ============================================================
    def _tab_ajustes(self) -> None:
        tab = self.tab_ajustes
        container = ttk.Frame(tab)
        container.pack(fill="both", expand=True, padx=20, pady=18)

        # Proveedor IA
        ia = ttk.LabelFrame(container, text="  Proveedor de IA  ", style="Card.TLabelframe")
        ia.pack(fill="x", pady=(0, 12))
        ic = ttk.Frame(ia)
        ic.pack(fill="x", padx=14, pady=12)
        ttk.Label(ic, text="Proveedor principal:", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=4)
        self.combo_proveedor = ttk.Combobox(ic, state="readonly", width=50)
        self.combo_proveedor.grid(row=0, column=1, padx=4)
        self.combo_proveedor.bind("<<ComboboxSelected>>", self._on_proveedor_change)
        ttk.Button(ic, text="Verificar", style="Secondary.TButton",
                   command=self._refrescar_estado_ia).grid(row=0, column=2, padx=4)
        self.lbl_ia_estado = ttk.Label(ic, text="", style="Card.TLabel")
        self.lbl_ia_estado.grid(row=1, column=0, columnspan=3, sticky="w", padx=4, pady=(8, 0))
        ttk.Label(ic, text="Orden: ① Google Antigravity (Gemini) · ② Z.ai GLM · ③ BigModel · ④ DeepSeek · ⑤ Kimi",
                  style="Hint.TLabel").grid(row=2, column=0, columnspan=3, sticky="w", padx=4, pady=(4, 0))
        ttk.Label(ic, text="Variables: GEMINI_API_KEY · ZAI_API_KEY · BIGMODEL_API_KEY · DEEPSEEK_API_KEY · KIMI_API_KEY",
                  style="Hint.TLabel").grid(row=3, column=0, columnspan=3, sticky="w", padx=4)
        ttk.Button(ic, text="Cómo obtener API key de Google AI Studio",
                   style="Secondary.TButton",
                   command=lambda: webbrowser.open("https://aistudio.google.com/app/apikey")).grid(
            row=4, column=0, columnspan=3, sticky="w", padx=4, pady=(4, 0))

        # Plantilla
        tpl = ttk.LabelFrame(container, text="  Plantilla maestra (.docx)  ", style="Card.TLabelframe")
        tpl.pack(fill="x", pady=(0, 12))
        tc = ttk.Frame(tpl)
        tc.pack(fill="x", padx=14, pady=12)
        self.var_plantilla = tk.StringVar(value=self.settings.plantilla_maestra)
        ttk.Entry(tc, textvariable=self.var_plantilla, width=85).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(tc, text="📂  Examinar", style="Secondary.TButton",
                   command=self._examinar_plantilla).pack(side="left")

        # Carpeta de salida
        out = ttk.LabelFrame(container, text="  📁  Carpeta donde se guardan las resoluciones  ",
                             style="Card.TLabelframe")
        out.pack(fill="x", pady=(0, 12))
        oc = ttk.Frame(out)
        oc.pack(fill="x", padx=14, pady=12)
        self.var_salida = tk.StringVar(value=self.settings.directorio_salida)
        ttk.Entry(oc, textvariable=self.var_salida, width=85).pack(
            side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(oc, text="📂  Elegir", style="Secondary.TButton",
                   command=self._examinar_salida).pack(side="left")
        ttk.Button(oc, text="Abrir", style="Secondary.TButton",
                   command=self._abrir_salida).pack(side="left", padx=(8, 0))

        ttk.Button(container, text="💾  Guardar ajustes", command=self._guardar_ajustes).pack(anchor="w", pady=6)

    # ============================================================
    # Helpers
    # ============================================================
    def _refrescar_estado_ia(self) -> None:
        disponibles = ai_client.listar_proveedores_disponibles()
        valores = []
        for pid, nombre, disp, vision in disponibles:
            tag = "OK" if disp else "--"
            vis = " · vision" if vision else ""
            valores.append(f"[{tag}] {pid} — {nombre}{vis}")
        self.combo_proveedor["values"] = valores
        for i, (pid, _, _, _) in enumerate(disponibles):
            if pid == self.settings.proveedor_ia:
                self.combo_proveedor.current(i)
                break
        else:
            for i, (pid, _, disp, _) in enumerate(disponibles):
                if disp:
                    self.combo_proveedor.current(i)
                    self.settings.proveedor_ia = pid
                    break

        n_disp = sum(1 for _, _, d, _ in disponibles if d)
        n_vision = sum(1 for _, _, d, v in disponibles if d and v)
        self.lbl_ia_estado.config(
            text=f"{n_disp} proveedor(es) con API key · {n_vision} con visión.  "
                 + ("Recomendado: Google Antigravity (Gemini)." if n_vision
                    else "Configura GEMINI_API_KEY para visión."),
        )

    def _on_proveedor_change(self, _evt=None) -> None:
        sel = self.combo_proveedor.get()
        for token in sel.split():
            token = token.strip()
            if token in {"gemini", "zai", "bigmodel", "deepseek", "kimi", "openai_compat"}:
                self.settings.proveedor_ia = token
                return

    def _examinar_plantilla(self) -> None:
        path = filedialog.askopenfilename(
            title="Plantilla .docx", filetypes=[("Word", "*.docx"), ("Todos", "*.*")],
            initialdir=self.settings.directorio_plantillas,
        )
        if path:
            self.var_plantilla.set(path)

    def _examinar_salida(self) -> None:
        path = filedialog.askdirectory(title="Carpeta donde guardar las resoluciones",
                                       initialdir=self.var_salida.get() or os.path.expanduser("~"))
        if path:
            self.var_salida.set(path)

    def _abrir_salida(self) -> None:
        p = Path(self.var_salida.get())
        p.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(str(p))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(p)], check=False)
        else:
            subprocess.run(["xdg-open", str(p)], check=False)

    def _guardar_ajustes(self) -> None:
        self.settings.plantilla_maestra = self.var_plantilla.get()
        self.settings.directorio_salida = self.var_salida.get()
        self.settings.guardar()
        messagebox.showinfo("Ajustes", f"Guardado en {USER_DIR/'settings.json'}")

    # ============================================================
    # Reporte y consola
    # ============================================================
    def _mostrar_reporte(self, reporte) -> None:
        self.btn_generar.config(state="normal")
        self.consola.config(state="normal")
        self.consola.delete("1.0", "end")
        if reporte.ok:
            self._log_consola("OK - DOCUMENTO GENERADO", "OK")
            self.estado_var.set(f"● OK → {reporte.archivo_salida}")
        else:
            self._log_consola("ERROR - GENERACION INCOMPLETA", "CRITICA")
            self.estado_var.set("● Revisa el reporte.")
        if reporte.proveedor_usado:
            self._log_consola(f"Proveedor: {reporte.proveedor_usado}", "INFO")
        if reporte.archivo_salida:
            self._log_consola(f"Archivo: {reporte.archivo_salida}", "INFO")
        if reporte.error_fatal:
            self._log_consola(f"FATAL: {reporte.error_fatal}", "CRITICA")
        for e in reporte.errores_validacion:
            self._log_consola(f"[{e['severity']}] {e['rule']}: {e['message']}", e["severity"])
        for e in reporte.errores_post:
            self._log_consola(f"[POST-{e['severity']}] {e['rule']}: {e['message']}", e["severity"])
        for w in reporte.advertencias:
            self._log_consola(f"! {w}", "VALIDABLE")
        n_crit = sum(1 for e in reporte.errores_validacion + reporte.errores_post if e["severity"] == "CRITICA")
        n_avis = sum(1 for e in reporte.errores_validacion + reporte.errores_post if e["severity"] == "VALIDABLE")
        self._log_consola(f"Totales: {n_crit} bloqueo(s), {n_avis} aviso(s).", "INFO")
        self.consola.config(state="disabled")

    def _mostrar_error(self, err: str) -> None:
        self.btn_generar.config(state="normal")
        self.consola.config(state="normal")
        self.consola.delete("1.0", "end")
        self._log_consola(f"EXCEPCION: {err}", "CRITICA")
        self.consola.config(state="disabled")
        self.estado_var.set("● Error inesperado.")

    def _log_consola(self, texto: str, tag: str = "INFO") -> None:
        self.consola.insert("end", texto + "\n", tag)
        self.consola.see("end")


def main() -> int:
    root = tk.Tk()
    try:
        ico = Path(__file__).resolve().parent.parent / "build_resources" / "resadmi.ico"
        if ico.exists():
            root.iconbitmap(str(ico))
    except Exception:
        pass
    ResAdmiApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
