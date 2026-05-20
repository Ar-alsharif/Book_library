from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Book, Category, User, Borrowing

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_books = Book.query.count()
    total_users = User.query.filter_by(is_admin=False).count()
    active_borrowings = Borrowing.query.filter_by(returned=False).count()
    total_borrowings = Borrowing.query.count()
    recent_borrowings = Borrowing.query.order_by(Borrowing.borrowed_at.desc()).limit(8).all()
    return render_template('admin/dashboard.html',
                           total_books=total_books,
                           total_users=total_users,
                           active_borrowings=active_borrowings,
                           total_borrowings=total_borrowings,
                           recent_borrowings=recent_borrowings)


@admin_bp.route('/books')
@login_required
@admin_required
def manage_books():
    books = Book.query.all()
    return render_template('admin/manage_books.html', books=books)


@admin_bp.route('/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        isbn = request.form.get('isbn', '').strip()
        description = request.form.get('description', '').strip()
        copies = int(request.form.get('copies', 1))
        category_id = int(request.form.get('category_id'))
        cover_url = request.form.get('cover_url', '').strip()

        if not title or not author or not isbn:
            flash('Title, Author, and ISBN are required.', 'danger')
            return render_template('admin/book_form.html', categories=categories, book=None)

        if Book.query.filter_by(isbn=isbn).first():
            flash('A book with this ISBN already exists.', 'danger')
            return render_template('admin/book_form.html', categories=categories, book=None)

        book = Book(title=title, author=author, isbn=isbn, description=description,
                    copies=copies, category_id=category_id, added_by=current_user.id,
                    cover_url=cover_url or None)
        db.session.add(book)
        db.session.commit()
        flash(f'Book "{title}" added successfully!', 'success')
        return redirect(url_for('admin.manage_books'))

    return render_template('admin/book_form.html', categories=categories, book=None)


@admin_bp.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    categories = Category.query.all()
    if request.method == 'POST':
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.isbn = request.form.get('isbn', '').strip()
        book.description = request.form.get('description', '').strip()
        book.copies = int(request.form.get('copies', 1))
        book.category_id = int(request.form.get('category_id'))
        book.cover_url = request.form.get('cover_url', '').strip() or None

        existing = Book.query.filter_by(isbn=book.isbn).first()
        if existing and existing.id != book_id:
            flash('Another book with this ISBN already exists.', 'danger')
            return render_template('admin/book_form.html', categories=categories, book=book)

        db.session.commit()
        flash(f'Book "{book.title}" updated successfully!', 'success')
        return redirect(url_for('admin.manage_books'))

    return render_template('admin/book_form.html', categories=categories, book=book)


@admin_bp.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    title = book.title
    Borrowing.query.filter_by(book_id=book_id).delete()
    db.session.delete(book)
    db.session.commit()
    flash(f'Book "{title}" deleted.', 'info')
    return redirect(url_for('admin.manage_books'))


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@admin_bp.route('/categories')
@login_required
@admin_required
def manage_categories():
    categories = Category.query.all()
    return render_template('admin/manage_categories.html', categories=categories)


@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Name is required.', 'danger')
            return render_template('admin/category_form.html', category=None)
        if Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'danger')
            return render_template('admin/category_form.html', category=None)
        db.session.add(Category(name=name, description=description))
        db.session.commit()
        flash(f'Category "{name}" added!', 'success')
        return redirect(url_for('admin.manage_categories'))
    return render_template('admin/category_form.html', category=None)


@admin_bp.route('/categories/edit/<int:cat_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    if request.method == 'POST':
        category.name = request.form.get('name', '').strip()
        category.description = request.form.get('description', '').strip()
        db.session.commit()
        flash(f'Category updated!', 'success')
        return redirect(url_for('admin.manage_categories'))
    return render_template('admin/category_form.html', category=category)


@admin_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    category = Category.query.get_or_404(cat_id)
    if category.books:
        flash('Cannot delete — category has books assigned to it.', 'danger')
        return redirect(url_for('admin.manage_categories'))
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('admin.manage_categories'))