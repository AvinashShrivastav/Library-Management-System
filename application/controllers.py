from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify
from flask import current_app as app
from .models import *
from datetime import datetime, timedelta
from io import BytesIO
# from .models import User, Book, Section


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        this_user = User.query.filter_by(name=name).first()
        if this_user:
            if this_user.password == password:
                if this_user.role == 'librarian':
                    return redirect('/librarian')
                return redirect(f'/user/{this_user.id}')
            else:
                return render_template('user_login.html',error = 'Invalid password')
        else:
            return render_template('user_login.html',error = 'Invalid username')
    return render_template('user_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        this_user = User.query.filter_by(name=name).first()
        if this_user:
            return render_template('user_registration.html',error = 'Username already exists')
        else:
            new_user = User(name = name, password = password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('user_registration.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    return render_template('user_dashboard.html')
@app.route('/books<int:user_id>', methods=['GET', 'POST'])
def books(user_id):
    books = Book.query.all()
    user = User.query.get(user_id)
    return render_template('user_books.html', books = books, user = user)

@app.route('/download<int:book_id>', methods=['GET', 'POST'])
def download(book_id):
    book = Book.query.get(book_id)
    return send_file(BytesIO(book.content), as_attachment=True, download_name=f'{book.name}.pdf')

@app.route('/request<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def request_book(user_id,book_id):
    book = Book.query.get(book_id)
    user = User.query.get(user_id)
    if request.method == 'POST':
        book.user_id = user_id
        req_days = int(request.form.get('req_days'))
        book.date_issued = datetime.now()
        book.return_date = datetime.now() + timedelta(days=req_days)
        book.status = 'hold'
        db.session.commit()
        return render_template('allwell.html')
        return redirect(f'/download{book_id}')
    return render_template('request_send.html', book = book, user = user)

@app.route('/librarian', methods=['GET', 'POST'])
def librarian():
    librarian = User.query.filter_by(role='librarian').first()
    books = Book.query.all()
    sections = Section.query.all()
    return render_template('librarian_dashboard.html' , username = librarian.name, books = books,sections = sections)

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_login(user_id):
    user = User.query.get(user_id)

    
    return render_template('user_mybooks.html' , user = user)

@app.route('/admin_req', methods=['GET', 'POST'])
def admin_req():
    books_on_hold = db.session.query(Book, User).join(User, User.id == Book.user_id).filter(Book.status == 'hold').all()
    books_issued = db.session.query(Book, User).join(User, User.id == Book.user_id).filter(Book.status == 'issued').all()
    return render_template('request_admin.html', requests=books_on_hold, issued = books_issued)


@app.route('/grant/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def grant(user_id, book_id):
    book = Book.query.get(book_id)
    book.status = 'issued'
    db.session.commit()
    return redirect('/admin_req')

@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'POST':
        name = request.form.get('sec_title')
        sec_date = datetime.strptime(request.form.get('sec_date'), "%Y-%m-%d").date()
        print(sec_date)
        sec_desc = request.form.get('sec_desc')
        # sec_img = request.files['sec_img']
        new_section = Section(name = name, description = sec_desc, date_created = sec_date)
        db.session.add(new_section)
        db.session.commit()
        return redirect('/librarian')
    return render_template('add_new_sec.html')


@app.route('/add_book<int:section_id>', methods=['GET', 'POST'])
def add_book(section_id):
    section = Section.query.get(section_id)
    if request.method == 'POST':
        name = request.form.get('book_name')
        authors = request.form.get('book_author')
        content = request.files['book_content'].read()
        new_book = Book(name = name, content = content)
        new_book.section = section
        for author in authors.split(','):
            new_author = Author(name = author)
            new_book.authors.append(new_author)
        db.session.add(new_book)
        db.session.commit()
        return redirect('/librarian')
    return render_template('add_new_book.html', section = section)


@app.route('/lib_book/<int:section_id>', methods=['GET', 'POST'])
def lib_book(section_id):
    books = Book.query.filter_by(section_id = section_id).all()
    return render_template('librarian_book.html', books = books,section_id = section_id)