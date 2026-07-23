# -*- mode: python ; coding: utf-8 -*-
# Spec de PyInstaller para el ejecutable de Fedora (Python 3.14 + pygame-ce).
from PyInstaller.utils.hooks import collect_all

datas = [('Resource', 'Resource')]
binaries = []
hiddenimports = ['primes', 'animacion', 'AimLabs.Menu']
tmp_ret = collect_all('OpenGL')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['PyPrimes3D.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
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
    name='PyPrimes3D_Fedora',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
