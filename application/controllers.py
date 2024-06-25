from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify, flash
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

@app.route('/request/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def request_book(user_id,book_id):

    # Assuming this is inside a Flask route function
    book = Book.query.get(book_id)
    user = User.query.get(user_id)
    if not book or not user:
        return redirect('/some-error-page')

    if request.method == 'POST':
        # Check if the book is already issued and not returned
        existing_issue = BookIssue.query.filter_by(book_id=book_id, status='issued').first()
        if existing_issue:
            return render_template('request_send.html', book=book, user=user)

        # Check if the user has already issued 5 or more books
        issued_books_count = BookIssue.query.filter_by(user_id=user_id, status='issued').count()
        if issued_books_count >= 5:
            # You can use flash to show a message to the user or handle this case as needed
            return render_template('request_send.html', book=book, user=user, error="You cannot issue more than 5 books.")

        req_days = int(request.form.get('req_days'))
        issue_date = datetime.now()
        return_date = issue_date + timedelta(days=req_days)
        
        # Create a new BookIssue instance
        new_issue = BookIssue(book_id=book_id, user_id=user_id, issue_date=issue_date, return_date=return_date, status='hold')
        
        # Add the new issue to the session and commit
        db.session.add(new_issue)
        db.session.commit()
        return redirect(f'/download/{book_id}')
    return render_template('request_send.html', book = book, user = user)
@app.route('/userprofile/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    user = User.query.get(user_id)
    book_issues = BookIssue.query.filter_by(user_id=user_id).all()
    books = [Book.query.get(book_issue.book_id) for book_issue in book_issues]
    return render_template('user_profile.html', user = user, user_issues = book_issues)

@app.route("/cancelrequest/<int:user_id>/<int:book_id>", methods=['GET', 'POST'])
def cancel_request(user_id, book_id):
    book_issue = BookIssue.query.filter_by(user_id=user_id, book_id=book_id, status='hold').first()
    if book_issue:
        db.session.delete(book_issue)
        db.session.commit()
    return redirect(f'/user/{user_id}')

@app.route('/return/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def return_book(user_id, book_id):
    book_issue = BookIssue.query.filter_by(user_id=user_id, book_id=book_id, status='issued').first()
    if book_issue:
        book_issue.status = 'returned'
        book_issue.return_date = datetime.now()
        db.session.commit()

    return redirect(f'/user/{user_id}')

@app.route('/viewbookhistory/<int:user_id>/<int:book_id>', methods=['GET', 'POST'])
def view_book_history(user_id, book_id):
    book_issues = BookIssue.query.filter_by(user_id=user_id, book_id=book_id).all()
    user = User.query.get(user_id)
    return render_template('user_book_history.html', book_issues=book_issues, user = user)

@app.route('/delete/<int:book_id>', methods=['GET', 'POST'])
def delete_book(book_id):
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
    return "Book deleted successfully"

@app.route('/view/<int:book_id>', methods=['GET', 'POST'])
def view_book(book_id):
    # Query for the book's issue details
    book_issues = BookIssue.query.filter_by(book_id=book_id).all()

    # Pass the data to the template
    return render_template('view_book.html', book_issues=book_issues)
@app.route('/librarian', methods=['GET', 'POST'])
def librarian():
    librarian = User.query.filter_by(role='librarian').first()
    books = Book.query.all()
    sections = Section.query.all()
    return render_template('librarian_dashboard.html' , user = librarian, books = books,sections = sections)

# Function to get books by status for a user
def get_books_by_status(user_id, status):
    book_issues = BookIssue.query.filter_by(user_id=user_id, status=status).all()
    books = [Book.query.get(book_issue.book_id) for book_issue in book_issues]
    return books

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_login(user_id):
    user = User.query.get(user_id)
    issued_books = get_books_by_status(user_id = user_id, status='issued')
    returned_books = get_books_by_status(user_id= user_id, status='returned')
    hold_books = get_books_by_status(user_id = user_id, status='hold')
    return render_template('user_mybooks.html' , user = user, issued_books = issued_books, hold_books = hold_books, returned_books = returned_books)

@app.route('/admin_req', methods=['GET', 'POST'])
def admin_req():
    # Assuming BookIssue model has book_id and user_id as foreign keys to Book and User models respectively
    books_on_hold = db.session.query(Book, User, BookIssue).join(BookIssue, BookIssue.book_id == Book.id).join(User, BookIssue.user_id == User.id).filter(BookIssue.status == 'hold').all()
    books_issued = db.session.query(Book, User, BookIssue).join(BookIssue, BookIssue.book_id == Book.id).join(User, BookIssue.user_id == User.id).filter(BookIssue.status == 'issued').all()
    return render_template('request_admin.html', requests=books_on_hold, issued=books_issued)

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


@app.route('/add_book/<int:section_id>', methods=['GET', 'POST'])
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


@app.route('/lib_book/<int:user_id>/<int:section_id>', methods=['GET', 'POST'])
def lib_book(user_id, section_id):
    books = Book.query.filter_by(section_id = section_id).all()
    section = Section.query.get(section_id)
    user = User.query.get(user_id)
    return render_template('librarian_book.html', books = books,section = section, user = user)