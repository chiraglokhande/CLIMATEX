import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def ensure_mysql_database(app):
    """If configured for MySQL, automatically create the database schema if it doesn't exist."""
    mysql_cfg = app.config.get('MYSQL_CONFIG')
    if not mysql_cfg:
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'mysql' not in uri:
            return True

    try:
        import pymysql
        if mysql_cfg:
            host = mysql_cfg['host']
            port = mysql_cfg['port']
            user = mysql_cfg['user']
            password = mysql_cfg['password']
            dbname = mysql_cfg['database']
        else:
            # Parse from URI
            from urllib.parse import urlparse
            parsed = urlparse(app.config.get('SQLALCHEMY_DATABASE_URI'))
            host = parsed.hostname or '127.0.0.1'
            port = parsed.port or 3306
            user = parsed.username or 'root'
            password = parsed.password or ''
            dbname = parsed.path.lstrip('/').split('?')[0] or 'climatex'

        # Connect to MySQL server without database selected to create db if needed
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        print(f"[Database] MySQL database '{dbname}' ready on {host}:{port}.")
        return True
    except Exception as e:
        print(f"[Database] MySQL connection note: {e}")
        return False

def init_db(app):
    uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    is_mysql = 'mysql' in uri

    if is_mysql:
        success = ensure_mysql_database(app)
        if not success:
            # Fallback to SQLite if MySQL credentials are not provided or access is denied
            fallback_sqlite = f"sqlite:///{os.path.join(app.config.get('BASE_DIR', os.getcwd()), 'climatex.db')}"
            print(f"[Database] Falling back to SQLite for seamless execution ({fallback_sqlite}).")
            print("[Database] To activate MySQL, set valid MYSQL_USER and MYSQL_PASSWORD in .env.")
            app.config['SQLALCHEMY_DATABASE_URI'] = fallback_sqlite

    db.init_app(app)

    with app.app_context():
        try:
            db.create_all()
            # Perform lightweight column check for SQLite users table
            active_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if 'sqlite' in active_uri:
                with db.engine.connect() as connection:
                    result = connection.execute(text("PRAGMA table_info(users)"))
                    cols = [row[1] for row in result]
                    if 'password_hash' not in cols:
                        connection.execute(text("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)"))
                    if 'full_name' not in cols:
                        connection.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(120)"))
                    if 'last_login' not in cols:
                        connection.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME"))
                    connection.commit()
            print(f"[Database] Connected & initialized: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        except Exception as e:
            print(f"[Database] Warning initializing tables: {e}")
