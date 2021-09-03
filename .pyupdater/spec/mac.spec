# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['/Users/sand/PycharmProjects/cli3/main.py'],
             pathex=['/Users/sand/PycharmProjects/cli3', '/Users/sand/PycharmProjects/cli3/.pyupdater/spec'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/sand/PycharmProjects/cli3/venv/lib/python3.7/site-packages/pyupdater/hooks'],
             hooksconfig={},
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
          name='mac',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mac')
app = BUNDLE(coll,
             name='mac.app',
             icon=None,
             bundle_identifier=None)
