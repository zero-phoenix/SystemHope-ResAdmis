# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['win32com.client', 'pywintypes', 'src.main', 'src.app', 'src.ai_client', 'src.builder', 'src.config', 'src.extractor_pdfs', 'src.footnote_injector', 'src.rules_engine', 'src.system_prompt', 'src.aprendizaje_reglas']
hiddenimports += collect_submodules('docx')
hiddenimports += collect_submodules('src')


a = Analysis(
    ['C:\\Users\\Admin\\.gemini\\antigravity\\scratch\\ResAdmi\\run.py'],
    pathex=['C:\\Users\\Admin\\.gemini\\antigravity\\scratch\\ResAdmi'],
    binaries=[],
    datas=[('templates', 'templates'), ('docs', 'docs')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ResAdmi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
