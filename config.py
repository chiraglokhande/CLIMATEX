import os
from urllib.parse import quote_plus

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))
except ImportError:
    pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'climatex-super-secret-key-2026-prod-ready')
    
    # In Vercel / serverless environments, the filesystem is read-only except /tmp
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        default_db = 'sqlite:////tmp/climatex.db'
    else:
        default_db = f'sqlite:///{os.path.join(BASE_DIR, "climatex.db")}'

    # Check for MySQL configuration
    mysql_user = os.environ.get('MYSQL_USER')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    mysql_host = os.environ.get('MYSQL_HOST', '127.0.0.1')
    mysql_port = os.environ.get('MYSQL_PORT', '3306')
    mysql_db = os.environ.get('MYSQL_DB', 'climatex')
    mysql_url = os.environ.get('MYSQL_URL')
    
    database_url = os.environ.get('DATABASE_URL')

    if mysql_url:
        target_db = mysql_url
    elif mysql_user:
        encoded_pass = quote_plus(mysql_password) if mysql_password else ''
        target_db = f'mysql+pymysql://{mysql_user}:{encoded_pass}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4'
    elif database_url:
        target_db = database_url
    else:
        target_db = default_db

    if target_db.startswith('postgres://'):
        target_db = target_db.replace('postgres://', 'postgresql://', 1)
    elif target_db.startswith('mysql://'):
        target_db = target_db.replace('mysql://', 'mysql+pymysql://', 1)

    SQLALCHEMY_DATABASE_URI = target_db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False if os.environ.get('VERCEL') or os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production' else True

    MYSQL_CONFIG = {
        'host': mysql_host,
        'port': int(mysql_port) if str(mysql_port).isdigit() else 3306,
        'user': mysql_user,
        'password': mysql_password,
        'database': mysql_db
    } if mysql_user else None
