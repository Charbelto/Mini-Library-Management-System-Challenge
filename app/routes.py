from flask import Blueprint, jsonify, redirect, url_for, render_template

main_bp = Blueprint('main', __name__)

from flask_login import current_user

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('books.dashboard'))
    else:
        return render_template('guest_index.html')

@main_bp.route('/health')
def health():
    return jsonify({"status": "healthy"}) 