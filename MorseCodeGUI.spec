# -*- mode: python -*-

block_cipher = None

a = Analysis(
    ['MorseCodeGUI.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('user_data/*.json', '.'),  # Include all JSON files in the current directory
        ('res/*', 'res')  # Include all files in the 'res' directory
    ],
    hiddenimports =['PyQt5.sip'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MorseWriter',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,  # Set to False to run without a command window
    icon='res/MorseWriterIcon.ico',
    uac_admin=True,
    uac_uiaccess=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='morsewriter'
)