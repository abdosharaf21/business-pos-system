# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['mysql.connector', 'mysql.connector.locales.eng.client_error', 'bcrypt', 'flask_jwt_extended', 'dotenv', 'backend.config', 'backend.database', 'backend.database.config', 'backend.database.connection', 'backend.database.bootstrap', 'backend.middleware', 'backend.middleware.cors', 'backend.middleware.error_handlers', 'backend.middleware.exceptions', 'backend.middleware.logger', 'backend.middleware.security', 'backend.middleware.timing', 'backend.middleware.auth_context', 'backend.middleware.rbac', 'backend.modules.auth', 'backend.modules.users', 'backend.modules.dashboard', 'backend.modules.categories', 'backend.modules.products', 'backend.modules.customers', 'backend.modules.purchases', 'backend.modules.inventory', 'backend.modules.pos', 'backend.modules.reports']
tmp_ret = collect_all('mysql.connector')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('bcrypt')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app.py'],
    pathex=[],
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
    [],
    exclude_binaries=True,
    name='backend-app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='backend-app',
)
