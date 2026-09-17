import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'climatex-super-secret-key-2026-prod-ready')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "climatex.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
