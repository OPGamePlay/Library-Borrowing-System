# src/main.py
import datetime
import time
from flask import Flask, render_template, request, make_response, redirect
import db

app = Flask(__name__)
db_user = db.db_user()
db_book = db.db_book()


@app.route("/add_book", methods=["GET"])
def add_book_page():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    

    if db_user.authenticate(username,password) == 'admin':
        error = request.args.get("error", -1)
        error_message = None

        error_messages = ['ISBN already exists.', 'Pages must be a positive integer.', 'Publication Year invalid.']
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]
        
        
        return render_template("add_book.html", error = error_message)
        
        
    else:
        return redirect('/booklist?message=Permission denied.')
    
@app.route('/lib_return_book', methods=["GET"])
def return_book_page():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    role = db_user.authenticate(username,password)
    if role == 'admin':
        code = request.args.get("message", -1)
        message = None
        messages = ['Book returned successfully.','Book ID not exist.', 'Book no need to return.']
        if int(code) < len(messages) and int(code) >= 0:
            message = messages[int(code)]


        return render_template('lib_return.html', message=message, user_role = role, username = username)
    else:
        return redirect('/booklist?message=Permission denied.')

@app.route('/lib_return_book', methods=['POST'])
def return_book():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    bookid = request.form['bookid']
    role = db_user.authenticate(username,password)
    if role == 'admin':
        lib_book = db_book.bookAsset.get(bookid, None)
        if lib_book:
            Book_info, _ = db_book.query_book_by('isbn', lib_book['isbn'], 1, 1)
            if lib_book['Due_date'] is not None:
                Duedate = datetime.datetime.strptime(lib_book['Due_date'], '%Y-%m-%d')
                diff = datetime.datetime.now() - Duedate
                if diff.days > 0:
                    days_late = diff.days
                    fine = days_late * 5
                else:
                    days_late = 0
                    fine = 0
                return render_template('lib_return_confirm.html', book = Book_info[0], bookid=bookid, fine=fine, days_late=days_late, user_role = role, username = username)
            else:
                return redirect('/lib_return_book?message=2')
                
        else:
            return redirect('/lib_return_book?message=1')
    else:
        return redirect('/booklist?message=Permission denied.')
@app.route('/lib_return_confirm', methods=['GET'])
def lib_return_confirm():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    if db_user.authenticate(username,password) == 'admin':
        bookid = request.args.get("bookid", '')
        db_book.return_book(bookid)
        return redirect('/lib_return_book?message=0')
        
    else:
        return redirect('/booklist?message=Permission denied.')

@app.route('/lib_book_register', methods=['GET'])
def lib_book_register():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)

    if db_user.authenticate(username,password) == 'admin':
        p = request.args.get("p", '')
        error = request.args.get("error", -1)
        message = None

        messages = ['Book registered successfully.', 'Book registration failed.']
        if int(error) < len(messages) and int(error) >= 0:
            message = messages[int(error)]
        
        
        return render_template("lib_book_register.html", message = message, previous_isbn = p)
    else:
        return redirect('/booklist?message=Permission denied.')
    
@app.route("/lib_book_register", methods=["POST"])
def lib_book_registry():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)

    if db_user.authenticate(username,password) == 'admin':
        isbn = request.form.get('isbn', None)
        book_id = request.form.get('bookid', None)
        print(isbn, book_id)
        if db_book.library_book_registry(isbn, book_id):
            return redirect(f'/lib_book_register?message=0&p={isbn}')

        else:
            return redirect(f'/lib_book_register?message=1&p={isbn}')

    else:
        return redirect('/booklist?message=Permission denied.')
    
@app.route("/add_book", methods=["POST"])
def add_book():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    if db_user.authenticate(username,password) == 'admin':
        title = request.form.get('title', None)
        author = request.form.get('author', None)
        publication_year = request.form.get('publication_year', None)
        genre = request.form.get('genre', None)
        isbn = request.form.get('isbn', None)
        pages = request.form.get('pages', None)
        publisher = request.form.get('publisher', None)
        cover_image_url = request.form.get('cover_image_url', None)
        rating = request.form.get('rating', None)
        available = request.form.get('available', 'True')

        ok, message_code = db_book.addBook(title, author, publication_year, genre, isbn, pages, publisher, cover_image_url, rating, available)
        if ok:
            # print("Book added successfully!")
            return redirect("/booklist")
        else:
            return redirect(f"/add_book?error={message_code}")

        
    else:
        return redirect('/booklist?message=Permission denied.')
    


@app.route("/login", methods=["GET"])
def login_required():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    error = request.args.get('error', -1)
    if username and password and db_user.authenticate(username, password) != 'guest':
            return redirect('/booklist')
    else:
        error_message = None

        error_messages = ['Username and Password are required', 'Invalid Username or Password']
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]
            
        return render_template('login.html', error=error_message)

@app.route("/register", methods=["GET"])
def register():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    error = request.args.get('error', -1)
    if username and password and db_user.authenticate(username, password) != 'guest':
        return redirect('/booklist')
    else:
        error_message = None
        error_messages = ['Username and Password are required', 'Invalid Username or Password']
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]
            
        return render_template('register.html', error=error_message)



@app.route("/logout")
def logout():
    res = make_response(redirect('/booklist'))
    res.set_cookie("username", 'None', expires=0)
    res.set_cookie("password", 'None', expires=0)
    return res


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    print(username, password)
    if username and password:
        if db_user.authenticate(username, password):
            res = make_response(redirect('/booklist'))
            res.set_cookie("username", username, expires=time.time()+3600)
            res.set_cookie("password", password, expires=time.time()+3600)
            
            return res
        else:
            return redirect('/login?error=1')
            
    else:
        return redirect('/login?error=0')

@app.route("/register", methods=["POST"])
def registration():
    username = request.form.get('username', None)
    password = request.form.get('password', None)
    if username and password:
        if db_user.register(username, password):
            res = make_response(redirect('/booklist'))
            res.set_cookie(key="username", value=username, expires=time.time()+3600)
            res.set_cookie(key="password", value=password, expires=time.time()+3600)
            return res
        else:
            return redirect('/register?error=1')

    else:
        return redirect('/register?error=0')

@app.route("/users")
def users():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    query = request.args.get("query", '')
    page = request.args.get("page", 1)
    count_per_page = 10
    skip = (int(page) - 1) * count_per_page
    
    user_role = db_user.authenticate(username,password)
    results = []
    if user_role == 'admin':
        for user in db_user.authJson.keys():
            if skip > 0:
                skip -= 1
                continue
            if len(results) == count_per_page:
                break
            if query in user:
                results.append(user)
                
        total_pages = len(db_user.authJson.keys()) // count_per_page + (1 if len(db_user.authJson) % count_per_page != 0 else 0)
        return render_template('users.html', current_page=page, total_pages = total_pages , users=results, user_role=user_role, username=username)
    else:
        return redirect('/booklist?message=Permission denied.')


@app.route("/set_password")
def set_password():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    user_role = db_user.authenticate(username,password)
    if user_role == 'admin':
        target_username = request.args.get('username', None)
        new_password = request.args.get('new_password', None)
        db_user.set_password(target_username, new_password)
        return redirect('/booklist?message=Password updated successfully.')
    else:
        return redirect('/booklist?message=Permission denied.')


@app.route("/delete_user", methods=["GET"])
def users_delete():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    user_role = db_user.authenticate(username,password)
    if user_role == 'admin':
        username_to_delete = request.args.get('username', None)
        if username_to_delete in db_user.authJson.keys():
            db_user.delete_user(username_to_delete)
            return redirect('/booklist?message=User deleted successfully.')
        else:
            return redirect('/booklist?message=User not found.')
    else:
        return redirect('/booklist?message=Permission denied.')






@app.route("/borrow")
def book_borrow():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    user_role = db_user.authenticate(username,password)
    if user_role == 'user' or user_role == 'admin':
        isbn = request.args.get('isbn', None)
        bookID = db_book.getAvailable_bookid(isbn)
        
        if bookID is not None:
            _, due_date = db_book.library_book_borrow(bookID,username)
            return redirect(f'/booklist?message=Book ID ({bookID}) has been lent to you. Please return before {due_date}.')
        else:
            return redirect('/book_details?isbn=%s'%isbn)


                



        
@app.route("/booklist", methods=["GET"])
def book_list():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)

    user_role = db_user.authenticate(username,password)

    count_per_page = 10
    query_type = request.args.get("query_type", 'title')
    query = request.args.get("query", '')
    page = request.args.get("page", 1)
    message = request.args.get("message", None)
    

    try:
        page = int(page)
    except Exception:
        page = 1
    
    books, total_pages = db_book.query_book_by(query_type, query, count_per_page, page)

    return render_template('book_list.html', books=books, user_role=user_role, username=username, current_page = page, total_pages=total_pages, message = message)

@app.route("/edit_book", methods=["GET"])
def edit_book_page():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    user_role = db_user.authenticate(username,password)
    if user_role != 'admin':
        return redirect('/booklist?message=Permission denied.')
    book_id = request.args.get("isbn", None)
    book = None
    Genre = ''
    
    
    if book_id:
        books, _ = db_book.query_book_by('isbn', book_id, 1, 1)

    if books:
        book = books.copy()[0]
        for genre in book['genre']:
            Genre += genre + ', '
        book['genre'] = Genre[:-2]
        return render_template('edit_book.html', book=book, user_role=user_role, username=username)
    else:
        return redirect("/booklist?message=Book not found")


@app.route("/edit_book", methods=["POST"])
def edit_book():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    if db_user.authenticate(username,password) == 'admin':
        title = request.form.get('title', None)
        author = request.form.get('author', None)
        publication_year = request.form.get('publication_year', None)
        genre = request.form.get('genre', None)
        isbn = request.form.get('isbn', None)
        pages = request.form.get('pages', None)
        publisher = request.form.get('publisher', None)
        cover_image_url = request.form.get('cover_image_url', None)
        rating = request.form.get('rating', None)
        available = request.form.get('available', None)
        ok, message_code = db_book.editBook(title, author, publication_year, genre, isbn, pages, publisher, cover_image_url, rating, available)
        if ok:
            # print("Book added successfully!")
            return redirect("/booklist")
        else:
            return redirect(f"/edit_book?error={message_code}")
        
    else:
        return redirect('/booklist?message=Permission denied.')


    
@app.route("/delete_book")
def delete_book():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)
    if db_user.authenticate(username,password) == 'admin':

        isbn = request.args.get('isbn', None)
        print(isbn)

        if db_book.deleteBook(isbn):
            return redirect(f"/booklist?message={isbn} is deleted successfully.")
        else:
            return redirect("/booklist?message=Failed to delete the book. Please try again later.")

        
    else:
        return redirect('/booklist?message=Permission denied.')

        
@app.route("/book_details", methods=["GET"])
def detail():
    username = request.cookies.get('username', None)
    password = request.cookies.get('password', None)

    user_role = db_user.authenticate(username,password)
    
    isbn = request.args.get("isbn", None)
    book = None
    if isbn:
        books, _ = db_book.query_book_by('isbn', isbn, 1, 1)
        
    if books:
        book = books.copy()[0]
        if db_book.getAvailable_bookid(isbn) is None:
            isAvailable = False
        else:
            isAvailable = True

        return render_template('book_details.html', book=book, user_role=user_role, username=username, isAvailable=isAvailable)
    else:
        return redirect("/booklist?message=Book not found")


        
        

@app.route("/")
def index():
    return redirect('/booklist')


if __name__ == '__main__':
    app.run(debug=True)