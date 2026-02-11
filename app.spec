# -*- mode: python ; coding: utf-8 -*-

import webbrowser
import threading

def open_browser():
    """Automatically open the app in browser after build launch"""
    threading.Timer(1.5, lambda: webbrowser.open_new("http://127.0.0.1:5000")).start()


# PyInstaller Build Configuration
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('Static', 'Static'),
        ('.env', '.'),
        ('data_entry.db', '.')
    ],
    hiddenimports=[],
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
    name='DataEntryManager',      # 👑 Your app’s executable name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                # 🔇 No console window when running
)

# Launch the browser automatically when app starts
open_browser()
