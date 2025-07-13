# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('utils', 'utils'), ('core', 'core'), ('ui', 'ui')],
    hiddenimports=['tkinterdnd2', 'utils.constants', 'utils.config', 'utils.logging', 'core.extraction', 'core.reconstruction', 'core.validation', 'core.file_manager', 'core.coherence_checker', 'ui.backup_manager', 'ui.interface', 'ui.tutorial'],
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
    name='TraducteurRenPyPro',
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
