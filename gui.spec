# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('raw_data/three_dynasties.sqlite3', 'raw_data'),
        ('images/cards/3D/*.png', 'images/cards/3D'),
    ],
    hiddenimports=['wx', 'wx._xml'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

splash = Splash(
    'l5r_splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_default="v0.1 (Three Dynasties)",
    text_pos=(10,410),
    text_size=12,
    text_color="#ffffff",
    minify_script=True,
    always_on_top=False,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='l5r_proxy',
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
    icon=['icon.ico'],
)
