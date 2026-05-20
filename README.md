#  Bibliotheca — Flask Book Library System

A full-featured book library management system built with Flask, SQLAlchemy, and SQLite. Features user authentication, admin dashboard, and book borrowing system.

---

## Features

- **User Authentication** — Register, Login, Logout with hashed passwords (bcrypt)
- **Role-Based Access** — Regular users vs Admin with protected routes
- **Book Browsing** — Search by title/author, filter by category
- **Borrowing System** — Borrow and return books with availability tracking
- **Admin Dashboard** — Full CRUD for books, user management, borrowing stats
- **Responsive UI** — Dark elegant theme, works on mobile

---

## Database Schema (4 Tables)

| Table | Description |
|-------|-------------|
| `users` | User accounts with admin flag |
| `books` | Book catalog with metadata |
| `categories` | Book categories |
| `borrowings` | Borrowing records with return tracking |

---

## API Endpoints (9 Total)

| Method | Route | Description | Access |
|--------|-------|-------------|--------|
| GET/POST | `/register` | User registration | Public |
| GET/POST | `/login` | User login | Public |
| GET | `/logout` | User logout | Logged-in |
| GET | `/books` | Browse/search books | Public |
| GET | `/books/<id>` | Book detail page | Public |
| POST | `/borrow/<id>` | Borrow a book | User |
| POST | `/return/<id>` | Return a book | User |
| GET | `/my-books` | User's borrowed books | User |
| GET | `/admin/dashboard` | Admin overview | Admin |
| GET | `/admin/books` | Manage all books | Admin |
| GET/POST | `/admin/books/add` | Add a new book | Admin |
| GET/POST | `/admin/books/edit/<id>` | Edit a book | Admin |
| POST | `/admin/books/delete/<id>` | Delete a book | Admin |
| GET | `/admin/users` | View all users | Admin |

---

## Quick Start

### Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/bibliotheca.git
cd bibliotheca

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python run.py
```

Visit `http://localhost:5000`

### Default Admin Account
- **Email:** admin@library.com
- **Password:** admin123

---

## Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or with plain Docker
docker build -t bibliotheca .
docker run -p 5000:5000 bibliotheca
```

---

## Project Structure

```
book-library/
├── app/
│   ├── __init__.py        ← App factory + DB seeding
│   ├── models.py          ← SQLAlchemy models
│   ├── auth.py            ← Login / Register / Logout
│   ├── books.py           ← Browse / Borrow / Return
│   ├── admin.py           ← Admin CRUD + Dashboard
│   └── templates/
│       ├── base.html
│       ├── login.html
│       ├── register.html
│       ├── books.html
│       ├── book_detail.html
│       ├── my_books.html
│       └── admin/
│           ├── dashboard.html
│           ├── manage_books.html
│           ├── book_form.html
│           └── manage_users.html
├── static/
│   └── style.css
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

- **Backend:** Python 3.11, Flask 3.0
- **Database:** SQLite via Flask-SQLAlchemy
- **Auth:** Flask-Login + Flask-Bcrypt
- **Frontend:** Jinja2 templates, Vanilla CSS
- **Deployment:** Docker / Docker Compose

---

## License

MIT License — free to use and modify.
