import sys
import os

# Insert repository root to sys.path so all modules (app, models, routes, services, config) resolve properly
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Vercel serverless WSGI entry point
handler = app
