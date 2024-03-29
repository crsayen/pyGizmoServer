# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['pyGizmoServer\\run.py'],
             pathex=['C:\\dev\\pyGizmoServer'],
             binaries=[('C:\\Windows\\System32\\libusb0.dll', '.')],
             datas=[
                 ("TestCubeUSB/schema.json","."),
                 ("webdist", "webdist"),
                 ("config/production.yml","config\\production.yml"),
                 ("TestCubeUSB/TestCubeUSB.py","TestCubeUSB"),
                 ("TestCubeUSB/TestCubeComponents","TestCubeUSB\\TestCubeComponents"),
                 ("TestCubeUSB/getter.py", "TestCubeUSB"),
                 ("pyGizmoServer/controller.py", "pyGizmoServer")
             ],
             hiddenimports=['usb'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='TestCubeServer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True, icon="icon.ico")
