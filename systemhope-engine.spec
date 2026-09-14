# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\systemhope_engine.py'],
    pathex=[],
    binaries=[],
    datas=[('docs/plantillas_maestras_index.json', 'docs'), ('docs/MATRIZ_MAESTRA_PHOENYX_POPPERIANA.md', 'docs'), ('docs/MEMORIA_ESTILO_VISUAL_PAGINAS.md', 'docs')],
    hiddenimports=[],
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
    name='systemhope-engine',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
