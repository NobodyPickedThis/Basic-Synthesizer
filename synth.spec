# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['Synth.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Add any audio library data files if needed
        # ('path/to/audio/configs/*', 'configs'),
    ],
    hiddenimports=[
        'numpy', 'scipy', 'mido', 'pyaudio',
        'numpy._core._add_newdocs', 'numpy._core._add_newdocs_scalars',
        'numpy._core', 'numpy._core._methods', 'numpy.lib.format',
        'numpy._core.multiarray', 'numpy._core.umath',
        'numpy._core.array', 'numpy._core.asarray', 'numpy._core.zeros',
        'numpy._core.empty', 'numpy._core.add', 'numpy._core.multiply',
        'numpy._core.divide', 'numpy._core.sqrt', 'numpy._core.astype',
        'scipy.signal', 'scipy.ndimage',
        '_portaudio', 'portaudio',
        '_thread', 'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib.backends._backend_tk',
        'PIL', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'test', 'unittest',
    ],
    noarchive=False,
    optimize=2, 
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Synth',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False, 
    upx_exclude=[],
    name='Synth',
)
