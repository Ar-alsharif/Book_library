from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import auth_bp
    from app.books import books_bp
    from app.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from app.models import User, Category, Book
    from app import bcrypt

    if not Category.query.first():
        cats = [
            Category(name='Fiction', description='Novels and stories'),
            Category(name='Science', description='Science and technology'),
            Category(name='History', description='Historical works'),
            Category(name='Philosophy', description='Philosophy and thought'),
        ]
        db.session.add_all(cats)
        db.session.commit()

    if not User.query.filter_by(email='admin@library.com').first():
        admin = User(
            username='admin',
            email='admin@library.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

    if not Book.query.first():
        cat1 = Category.query.filter_by(name='Fiction').first()
        cat2 = Category.query.filter_by(name='Science').first()
        cat3 = Category.query.filter_by(name='History').first()
        admin = User.query.filter_by(email='admin@library.com').first()
        books = [
            Book(title='1984', author='George Orwell', isbn='9780451524935',
                 description='A dystopian social science fiction novel.', copies=3,
                 category_id=cat1.id, added_by=admin.id),
            Book(title='Sapiens', author='Yuval Noah Harari', isbn='9780062316097',
                 description='A brief history of humankind.', copies=5,
                 category_id=cat3.id, added_by=admin.id),
            Book(title='A Brief History of Time', author='Stephen Hawking', isbn='9780553380163',
                 description='From the Big Bang to Black Holes.', copies=4,
                 category_id=cat2.id, added_by=admin.id),
            Book(title='The Republic', author='Plato', isbn='9780140455113',
                 description='A Socratic dialogue on justice.', copies=2,
                 category_id=Category.query.filter_by(name='Philosophy').first().id, added_by=admin.id),
        ]
        db.session.add_all(books)
        db.session.commit()
