import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'climatex-super-secret-key-2026-prod-ready')
    
    # In Vercel / serverless environments, the filesystem is read-only except /tmp
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        default_db = 'sqlite:////tmp/climatex.db'
    else:
        default_db = f'sqlite:///{os.path.join(BASE_DIR, "climatex.db")}'

    db_url = os.environ.get('DATABASE_URL', default_db)
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False if os.environ.get('VERCEL') else True
