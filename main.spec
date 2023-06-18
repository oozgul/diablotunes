# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('tesseract/tesseract.exe', 'tesseract'), ('tesseract/tessdata', 'tessdata')],
    datas=[('libvlc.dll', '.'), ('libvlccore.dll', '.'), ('plugins', 'plugins'), ('output.json', '.'), ('tesseract', 'tesseract')],
    hiddenimports=[
        'os', 'json', 'random', 'time', 'cv2', 'numpy', 'pyautogui',
        'PIL.Image', 'pytesseract', 'sys', 'vlc', 'yt_dlp.YoutubeDL',
        'collections', 'threading', 'tkinter', 'tkinter.ttk', 'tkinter.scrolledtext',
        'queue', 'datetime', 'atexit'],
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
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
