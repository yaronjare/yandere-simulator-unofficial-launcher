# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('ayano.png', '.'),
    ('logo.png', '.'),
    ('icon.ico', '.'),
    ('futura_mediumcyrusbyme.ttf', '.')
]

a = Analysis(
    ['yandere_launcher.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=['config', 'customtkinter', 'PIL', 'requests', 'customtkinter.windows.widgets.themes', 'customtkinter.windows.widgets.utility'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter.test', 'unittest', 'pydoc'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Yandere Simulator Launcher',
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
    icon='icon.ico'
)
