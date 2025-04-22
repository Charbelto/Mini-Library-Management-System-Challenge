from app import create_app

import init_db
app = create_app()
print("Initializing database...")
init_db.init_database()
print("Database initialized.")

if __name__ == '__main__':
    app.run(debug=True)