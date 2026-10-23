from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """First page of the app: Gateway showing Login and Register options with transparent glassmorphic UI."""
    if session.get('user_id'):
        return redirect(url_for('dashboard.dashboard'))
    return render_template('auth.html', active_tab='login')

@main_bp.route('/home')
def home():
    """Platform marketing and environmental overview hero page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')
