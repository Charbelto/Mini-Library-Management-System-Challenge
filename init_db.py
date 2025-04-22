from flask import Flask
from app import create_app, db
from app.models import User, Book
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

def init_database():
    app = create_app()

    with app.app_context():
        logging.info("Creating database tables...")
        db.create_all()
        logging.info("Database tables created.")

        # Check if admin user already exists
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@library.com')
        if User.query.filter_by(email=admin_email).first() is None:
            logging.info("Creating default users...")
            # Create admin user
            admin = User(
                username=os.environ.get('ADMIN_USERNAME', 'admin'),
                email=admin_email,
                role='admin'
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)

            # Create librarian user
            librarian = User(
                username='librarian',
                email='librarian@library.com',
                role='librarian'
            )
            librarian.set_password('librarian123')
            db.session.add(librarian)

            # Create regular user
            user = User(
                username='user',
                email='user@library.com',
                role='user'
            )
            user.set_password('user123')
            db.session.add(user)

            # Create new user
            new_user_email = 'charbeltoumieh1@gmail.com'
            if User.query.filter_by(email=new_user_email).first() is None:
                new_user = User(
                    username='charbeltoumieh',
                    email=new_user_email,
                    role='user'
                )
                new_user.set_password('Charbel')
                db.session.add(new_user)
                db.session.commit()
                logging.info('New user charbeltoumieh1@gmail.com created.')
            else:
                logging.info('User charbeltoumieh1@gmail.com already exists.')

            db.session.commit()
            logging.info('Database initialized with admin, librarian, and regular user accounts.')
        else:
            logging.info('Admin user already exists. Skipping initialization.')

        # Add 100 sample books
        if Book.query.count() == 0:
            import random
            logging.info("Adding 100 sample books...")
            genres = ['Fiction', 'Non-Fiction', 'Science', 'History']
            authors = ['Jane Austen', 'Charles Dickens', 'J.R.R. Tolkien', 'Isaac Asimov', 'Agatha Christie']
            titles = ['Pride and Prejudice', 'Oliver Twist', 'The Hobbit', 'Foundation', 'Murder on the Orient Express']
            for i in range(100):
                book = Book(
                    title=random.choice(titles),
                    author=random.choice(authors),
                    isbn=f'ISBN{i+1}',
                    genre=random.choice(genres),
                    description='Sample description',
                    status='available'
                )
                db.session.add(book)
                print(f"Adding book with ISBN: {book.isbn}")
            db.session.commit()
        logging.info("100 sample books added.")

if __name__ == '__main__':
    load_dotenv()
    init_database()