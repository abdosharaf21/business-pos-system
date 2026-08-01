#!/usr/bin/env python3
"""Build the Flask backend into a standalone executable with PyInstaller."""

import os
import sys
import shutil
import PyInstaller.__main__

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(PROJECT_ROOT, 'backend', 'dist')
WORK_DIR = os.path.join(PROJECT_ROOT, 'backend', 'build')
SPEC_DIR = os.path.join(PROJECT_ROOT, 'backend')


def clean_build_artifacts():
    for d in [DIST_DIR, WORK_DIR]:
        if os.path.isdir(d):
            shutil.rmtree(d)
    spec_file = os.path.join(SPEC_DIR, 'backend-app.spec')
    if os.path.isfile(spec_file):
        os.remove(spec_file)


def main():
    clean_build_artifacts()

    PyInstaller.__main__.run([
        'backend/app.py',
        '--name=backend-app',
        '--onedir',
        '--distpath=' + DIST_DIR,
        '--workpath=' + WORK_DIR,
        '--specpath=' + SPEC_DIR,
        '--hidden-import=mysql.connector',
        '--hidden-import=mysql.connector.locales.eng.client_error',
        '--hidden-import=bcrypt',
        '--hidden-import=flask_jwt_extended',
        '--hidden-import=dotenv',
        '--hidden-import=backend.config',
        '--hidden-import=backend.database',
        '--hidden-import=backend.database.config',
        '--hidden-import=backend.database.connection',
        '--hidden-import=backend.database.bootstrap',
        '--hidden-import=backend.middleware',
        '--hidden-import=backend.middleware.cors',
        '--hidden-import=backend.middleware.error_handlers',
        '--hidden-import=backend.middleware.exceptions',
        '--hidden-import=backend.middleware.logger',
        '--hidden-import=backend.middleware.security',
        '--hidden-import=backend.middleware.timing',
        '--hidden-import=backend.middleware.auth_context',
        '--hidden-import=backend.middleware.rbac',
        '--hidden-import=backend.modules.auth',
        '--hidden-import=backend.modules.users',
        '--hidden-import=backend.modules.dashboard',
        '--hidden-import=backend.modules.categories',
        '--hidden-import=backend.modules.products',
        '--hidden-import=backend.modules.customers',
        '--hidden-import=backend.modules.purchases',
        '--hidden-import=backend.modules.inventory',
        '--hidden-import=backend.modules.pos',
        '--hidden-import=backend.modules.reports',
        '--collect-all=mysql.connector',
        '--collect-all=bcrypt',
        '--clean',
        '--noconfirm',
    ])

    print(f'\nBuild complete: {os.path.join(DIST_DIR, "backend-app")}')


if __name__ == '__main__':
    main()
