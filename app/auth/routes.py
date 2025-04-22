# app/auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User
from urllib.parse import urlsplit
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

from functools import wraps
from flask import abort

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Configure OAuth providers
oauth.register(
    name='google',
    client_id='your-google-client-id',
    client_secret='your-google-client-secret',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/google')
def google():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    
    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(
            username=user_info['name'],
            email=user_info['email'],
            oauth_provider='google',
            oauth_id=user_info['id']
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('main.index'))

@auth_bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.all()
    print(f"Admin {current_user.username} accessed user management page.")
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_users_add():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Admin {current_user.username} added user {username} with role {role}.")
        flash('User added successfully.')
        return redirect(url_for('auth.admin_users'))
    
    return render_template('auth/admin_users_add.html')

@auth_bp.route('/admin/users/remove/<int:user_id>')
@login_required
@role_required('admin')
def admin_users_remove(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    print(f"Admin {current_user.username} removed user {user.username}.")
    flash('User removed successfully.')
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        
        if current_user.check_password(old_password):
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password changed successfully.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid old password.')
            return render_template('auth/change_password.html')
    
    return render_template('auth/change_password.html')