# -*- mode: python ; coding: utf-8 -*-
import os

# EXE 옆에 data.json 등이 없으면 빈 파일로 초기화되므로
# 기존 파일이 있을 때만 번들에 포함합니다.
_here = os.path.dirname(os.path.abspath(SPEC))
_data_files = []
for _fname in ('data.json', 'orders.json', 'users.json', 'commands.txt'):
    _src = os.path.join(_here, _fname)
    if os.path.exists(_src):
        _data_files.append((_src, '.'))

a = Analysis(
    ['LogisticsWeb.py'],
    pathex=[],
    binaries=[],
    datas=_data_files,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PySide6', 'PySide2', 'PyQt6',
        'tkinter', '_tkinter',
        'numpy', 'pandas', 'scipy', 'matplotlib',
        'IPython', 'jupyter', 'notebook',
        'pytest', 'sphinx', 'docutils',
        'PIL', 'Pillow',
        'zmq', 'tornado',
    ],
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
    name='LogisticsWeb',
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
