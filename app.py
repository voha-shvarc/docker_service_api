import app
from app import database

if __name__ == '__main__':
    app = app.create_app()
    database.init_database()
    print("inited database")
    app.run()

