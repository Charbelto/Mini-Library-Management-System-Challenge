# app/books/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_required, current_user
from app import db
from app.models import Book, BorrowRecord, AuditLog
from datetime import datetime, timedelta
from functools import wraps

books_bp = Blueprint('books', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'librarian']:
            flash('Access denied.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@books_bp.route('/')
@login_required
def dashboard():
    books = Book.query.all()
    borrowed_books = BorrowRecord.query.filter_by(
        user_id=current_user.id,
        status='borrowed'
    ).all()
    now = datetime.utcnow()
    return render_template('books/dashboard.html', books=books, borrowed_books=borrowed_books, now=now)

@books_bp.route('/books')
@login_required
def book_list():
    query = Book.query
    search = request.args.get('search')
    genre = request.args.get('genre')
    status = request.args.get('status')

    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )
    if genre:
        query = query.filter_by(genre=genre)
    if status:
        query = query.filter_by(status=status)

    books = query.all()
    return render_template('books/book_list.html', books=books)

@books_bp.route('/book/new', methods=['GET', 'POST'])
@librarian_required
def new_book():
    if request.method == 'POST':
        book = Book(
            title=request.form['title'],
            author=request.form['author'],
            isbn=request.form['isbn'],
            publication_date=datetime.strptime(request.form['publication_date'], '%Y-%m-%d'),
            genre=request.form['genre'],
            description=request.form['description'],
            cover_image=request.form['cover_image']
        )
        db.session.add(book)
        db.session.commit()

        log = AuditLog(
            user_id=current_user.id,
            action='create',
            table_name='book',
            record_id=book.id,
            details=f'Created book: {book.title}'
        )
        db.session.add(log)
        db.session.commit()

        flash('Book added successfully!')
        return redirect(url_for('books.book_list'))

    return render_template('books/book_form.html', book=None)

@books_bp.route('/book/<int:id>/edit', methods=['GET', 'POST'])
@librarian_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.isbn = request.form['isbn']
        book.publication_date = datetime.strptime(request.form['publication_date'], '%Y-%m-%d')
        book.genre = request.form['genre']
        book.description = request.form['description']
        book.cover_image = request.form['cover_image']
        
        db.session.commit()

        log = AuditLog(
            user_id=current_user.id,
            action='update',
            table_name='book',
            record_id=book.id,
            details=f'Updated book: {book.title}'
        )
        db.session.add(log)
        db.session.commit()

        flash('Book updated successfully!')
        return redirect(url_for('books.book_list'))

    return render_template('books/book_form.html', book=book)

@books_bp.route('/book/<int:id>/delete', methods=['POST'])
@librarian_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    
    log = AuditLog(
        user_id=current_user.id,
        action='delete',
        table_name='book',
        record_id=book.id,
        details=f'Deleted book: {book.title}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Book deleted successfully!')
    return redirect(url_for('books.book_list'))

@books_bp.route('/book/<int:id>/checkout', methods=['POST'])
@login_required
def checkout_book(id):
    book = Book.query.get_or_404(id)
    if book.status != 'available':
        flash('Book is not available for checkout!')
        return redirect(url_for('books.book_list'))

    book.status = 'borrowed'
    borrow_record = BorrowRecord(
        user_id=current_user.id,
        book_id=book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(borrow_record)
    
    log = AuditLog(
        user_id=current_user.id,
        action='checkout',
        table_name='book',
        record_id=book.id,
        details=f'Checked out book: {book.title}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Book checked out successfully!')
    return redirect(url_for('books.dashboard'))

@books_bp.route('/book/<int:id>/return', methods=['POST'])
@login_required
def return_book(id):
    borrow_record = BorrowRecord.query.filter_by(
        book_id=id,
        user_id=current_user.id,
        status='borrowed'
    ).first_or_404()

    book = Book.query.get_or_404(id)
    book.status = 'available'
    borrow_record.status = 'returned'
    borrow_record.return_date = datetime.utcnow()

    log = AuditLog(
        user_id=current_user.id,
        action='return',
        table_name='book',
        record_id=book.id,
        details=f'Returned book: {book.title}'
    )
    db.session.add(log)
    db.session.commit()

    flash('Book returned successfully!')
    return redirect(url_for('books.dashboard'))

@books_bp.route('/export/csv')
@librarian_required
def export_csv():
    books = Book.query.all()
    csv_data = "Title,Author,ISBN,Genre,Status\n"
    for book in books:
        csv_data += f"{book.title},{book.author},{book.isbn},{book.genre},{book.status}\n"
    
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=books.csv"}
    )