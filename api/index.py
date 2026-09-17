import sys
import os

# Insert repository root to sys.path so all modules (app, models, routes, services, config) resolve properly
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from app import app
    handler = app
except Exception as e:
    import traceback
    err_trace = traceback.format_exc()
    print("FATAL INITIALIZATION ERROR:\n", err_trace)
    def handler(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, response_headers)
        html = f"""<!DOCTYPE html>
<html>
<head><title>CLIMATEX Startup Error</title></head>
<body style="font-family: sans-serif; padding: 2rem; background: #0f172a; color: #f8fafc;">
  <h2 style="color: #ef4444;">CLIMATEX Serverless Startup Error</h2>
  <pre style="background: #1e293b; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #fca5a5;">{err_trace}</pre>
</body>
</html>"""
        return [html.encode('utf-8')]
    app = handler
