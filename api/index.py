import sys
import os

# Insert repository root to sys.path so all modules (app, models, routes, services, config) resolve properly
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import urllib.parse

class VercelPathMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        
        # Check if the rewritten path was forwarded via __path__
        if '__path__' in params and params['__path__']:
            real_path = params['__path__'][0]
            while real_path.startswith('//'):
                real_path = real_path[1:]
            if not real_path.startswith('/'):
                real_path = '/' + real_path
            environ['PATH_INFO'] = real_path

            # Remove __path__ so the Flask app receives pristine query parameters
            del params['__path__']
            environ['QUERY_STRING'] = urllib.parse.urlencode(params, doseq=True)
        else:
            # Fallback path extraction
            matched_path = environ.get('HTTP_X_MATCHED_PATH')
            path_info = environ.get('PATH_INFO', '')
            if path_info in ('/api/index.py', '/api/index', '/api', '/api/'):
                if matched_path and matched_path not in ('/api/index.py', '/api/index', '/api', '/api/'):
                    environ['PATH_INFO'] = matched_path
                else:
                    environ['PATH_INFO'] = '/'
            elif path_info.startswith('/api/index.py/'):
                environ['PATH_INFO'] = path_info[len('/api/index.py'):]
            elif path_info.startswith('/api/index/'):
                environ['PATH_INFO'] = path_info[len('/api/index'):]
            elif not path_info:
                environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

try:
    from app import app
    handler = VercelPathMiddleware(app)
    app = handler
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
