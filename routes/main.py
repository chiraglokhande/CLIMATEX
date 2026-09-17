from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if request.args.get('debug'):
        return jsonify({
            'request.path': request.path,
            'request.url': request.url,
            'headers': dict(request.headers),
            'environ': {k: str(v) for k, v in request.environ.items() if isinstance(v, (str, int, float, bool))}
        })
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')
