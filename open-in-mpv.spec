# -*- mode: python ; coding: utf-8 -*-

"""PyInstaller spec file for building open-in-mpv Windows executable."""

block_cipher = None

a = Analysis(
    ['open_in_mpv/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['open_in_mpv', 'open_in_mpv.main', 'open_in_mpv.constants'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='open-in-mpv',
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
