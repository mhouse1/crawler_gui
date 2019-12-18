# -*- mode: python ; coding: utf-8 -*-
import os
import site

block_cipher = None

typelib_path = os.path.join(site.getsitepackages()[1], 'gnome', 'lib', 'girepository-1.0')

a = Analysis(['main.py'],
             pathex=['C:\\Users\\chizz\\Documents\\Projects\\crawler_gui\\GUI'],
             binaries=[(os.path.join(typelib_path, tl), 'gi_typelibs') for tl in os.listdir(typelib_path)],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='main')
