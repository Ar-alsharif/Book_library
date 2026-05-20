from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Book, Category, Borrowing
from datetime import datetime


books_bp = Blueprint('books', __name__)


@books_bp.route('/books')
def browse():
    search = request.args.get('search', '')
    cat_id = request.args.get('category', '')
    query = Book.query
    if search:
        query = query.filter(
            (Book.title.ilike(f'%{search}%')) | (Book.author.ilike(f'%{search}%'))
        )
    if cat_id:
        query = query.filter_by(category_id=cat_id)
    books = query.all()
    categories = Category.query.all()
    return render_template('books.html', books=books, categories=categories,
                           search=search, selected_cat=cat_id)


@books_bp.route('/books/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    user_borrowed = False
    if current_user.is_authenticated:
        user_borrowed = Borrowing.query.filter_by(
            user_id=current_user.id, book_id=book_id, returned=False
        ).first() is not None
    return render_template('book_detail.html', book=book, user_borrowed=user_borrowed)


@books_bp.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow(book_id):
    book = Book.query.get_or_404(book_id)
    already = Borrowing.query.filter_by(
        user_id=current_user.id, book_id=book_id, returned=False
    ).first()
    if already:
        flash('You already have this book borrowed.', 'warning')
        return redirect(url_for('books.book_detail', book_id=book_id))
    if book.available_copies <= 0:
        flash('No copies available right now.', 'danger')
        return redirect(url_for('books.book_detail', book_id=book_id))

    borrowing = Borrowing(
        user_id=current_user.id,
        book_id=book_id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(borrowing)
    db.session.commit()
    flash(f'You borrowed "{book.title}" successfully! Due in 14 days.', 'success')
    return redirect(url_for('books.my_books'))


@books_bp.route('/return/<int:borrowing_id>', methods=['POST'])
@login_required
def return_book(borrowing_id):
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    if borrowing.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('books.my_books'))
    borrowing.returned = True
    borrowing.returned_at = datetime.utcnow()
    db.session.commit()
    flash(f'"{borrowing.book.title}" returned successfully!', 'success')
    return redirect(url_for('books.my_books'))


@books_bp.route('/my-books')
@login_required
def my_books():
    active = Borrowing.query.filter_by(user_id=current_user.id, returned=False).all()
    history = Borrowing.query.filter_by(user_id=current_user.id, returned=True)\
        .order_by(Borrowing.returned_at.desc()).limit(10).all()
    # return render_template('my_books.html', active=active, history=history)
    return render_template('my_books.html', active=active, history=history, now=datetime.utcnow())
