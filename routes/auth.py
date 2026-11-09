from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timezone
import re
from models.database import db
from models.models import User

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = re.compile(r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$")
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method in ('GET', 'HEAD'):
        return render_template('auth.html', active_tab='login')

    # Handle POST
    is_json = request.is_json
    data = request.get_json(silent=True) or request.form

    identifier = (data.get('identifier') or data.get('username') or data.get('email') or '').strip()
    password = data.get('password', '')
    req_next = data.get('next') or request.args.get('next')
    next_url = req_next if (req_next and req_next not in ['/dashboard', url_for('dashboard.dashboard')]) else url_for('main.home')

    if not identifier or not password:
        msg = "Please enter your username/email and password."
        if is_json:
            return jsonify({'status': 'error', 'message': msg}), 400
        flash(msg, 'danger')
        return render_template('auth.html', active_tab='login', identifier=identifier), 400

    # Query user by username or email (case-insensitive for email)
    user = User.query.filter(
        (User.username == identifier) | (db.func.lower(User.email) == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        msg = "Invalid credentials. Please verify your username/email and password."
        if is_json:
            return jsonify({'status': 'error', 'message': msg}), 401
        flash(msg, 'danger')
        return render_template('auth.html', active_tab='login', identifier=identifier), 401

    # Login Success: establish secure session
    session.clear()
    session['user_id'] = user.id
    session['username'] = user.username
    session['user_role'] = user.role
    session['user_email'] = user.email

    try:
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
    except Exception as e:
        print(f"[Auth] Warning recording last_login: {e}")
        db.session.rollback()

    msg = f"Welcome back, {user.full_name or user.username}!"
    if is_json:
        return jsonify({'status': 'success', 'message': msg, 'redirect': next_url, 'user': user.to_dict()})

    flash(msg, 'success')
    return redirect(next_url)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method in ('GET', 'HEAD'):
        return render_template('auth.html', active_tab='register')

    # Handle POST
    is_json = request.is_json
    data = request.get_json(silent=True) or request.form

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip().lower()
    full_name = (data.get('full_name') or '').strip()
    role = (data.get('role') or 'Environmental Analyst').strip()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')

    errors = []

    # Validations
    if not username:
        errors.append("Username is required.")
    elif not USERNAME_REGEX.match(username):
        errors.append("Username must be 3-30 characters long and contain only letters, numbers, and underscores.")

    if not email:
        errors.append("Email address is required.")
    elif not EMAIL_REGEX.match(email):
        errors.append("Please provide a valid email address.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters long.")

    if password != confirm_password:
        errors.append("Passwords do not match.")

    # Check database uniqueness
    if not errors:
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            errors.append(f"Username '{username}' is already in use. Please choose another.")

        existing_email = User.query.filter(db.func.lower(User.email) == email).first()
        if existing_email:
            errors.append(f"Email '{email}' is already registered. Please sign in.")

    if errors:
        msg = " ".join(errors)
        if is_json:
            return jsonify({'status': 'error', 'message': msg, 'errors': errors}), 400
        for err in errors:
            flash(err, 'danger')
        return render_template('auth.html', active_tab='register', username=username, email=email, full_name=full_name, role=role), 400

    # Create & Save User in Database
    try:
        new_user = User(
            username=username,
            email=email,
            full_name=full_name or username,
            role=role,
            created_at=datetime.now(timezone.utc),
            last_login=datetime.now(timezone.utc)
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Automatically log the new user in
        session.clear()
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['user_role'] = new_user.role
        session['user_email'] = new_user.email

        msg = f"Account registered successfully in database! Welcome to CLIMATEX, {new_user.full_name}."
        if is_json:
            return jsonify({'status': 'success', 'message': msg, 'redirect': url_for('main.home'), 'user': new_user.to_dict()})

        flash(msg, 'success')
        return redirect(url_for('main.home'))

    except Exception as e:
        db.session.rollback()
        print(f"[Auth] Database error creating user: {e}")
        msg = f"An error occurred saving your profile to the database: {e}"
        if is_json:
            return jsonify({'status': 'error', 'message': msg}), 500
        flash(msg, 'danger')
        return render_template('auth.html', active_tab='register', username=username, email=email, full_name=full_name, role=role), 500

@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """One-click instant login as official Demo Analyst for testing and evaluation."""
    demo_user = User.query.filter_by(username='analyst_demo').first()
    if not demo_user:
        # Create on demand if not yet seeded
        demo_user = User(
            username="analyst_demo",
            email="analyst@climatex.org",
            full_name="Dr. Aisha Roy",
            role="Senior Environmental Analyst"
        )
        demo_user.set_password("Climatex2026!")
        db.session.add(demo_user)
        db.session.commit()

    session.clear()
    session['user_id'] = demo_user.id
    session['username'] = demo_user.username
    session['user_role'] = demo_user.role
    session['user_email'] = demo_user.email

    try:
        demo_user.last_login = datetime.now(timezone.utc)
        db.session.commit()
    except Exception:
        db.session.rollback()

    msg = f"Signed in as Benchmark Analyst: {demo_user.full_name} ({demo_user.role})."
    if request.is_json:
        return jsonify({'status': 'success', 'message': msg, 'redirect': url_for('main.home'), 'user': demo_user.to_dict()})

    flash(msg, 'success')
    return redirect(url_for('main.home'))

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('main.index'))
