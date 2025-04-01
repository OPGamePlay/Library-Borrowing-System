from flask import Blueprint, request, redirect, render_template, url_for
from flask import session
from app.models.user import db_user
from app.models.book import db_book

bp = Blueprint("books", __name__)


@bp.route("/booklist")
def book_list():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)

    user_role = db_user.authenticate(username, password)

    count_per_page = 10
    query_type = request.args.get("query_type", "title")
    query = request.args.get("query", "")
    page = request.args.get("page", 1)
    use_fuzzy = request.args.get("fuzzy", "false").lower() == "true"
    message = request.args.get("message", None)

    try:
        page = int(page)
    except Exception:
        page = 1

    books, total_pages = db_book.query_book_by(
        query_type, query, count_per_page, page, use_fuzzy
    )
    for book in books:
        if isinstance(book.get("publishedDate"), dict):
            book["publishedDate"] = book["publishedDate"]["date"][:10]
        elif book.get("publishedDate"):
            book["publishedDate"] = book["publishedDate"][:10]
        else:
            book["publishedDate"] = "N/A"
    return render_template(
        "book_list.html",
        books=books,
        user_role=user_role,
        username=username,
        current_page=page,
        total_pages=total_pages,
        message=message,
    )


@bp.route("/book_details", methods=["GET"])
def detail():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)

    user_role = db_user.authenticate(username, password)

    isbn = request.args.get("isbn", None)
    book = None
    if isbn:
        books, _ = db_book.query_book_by("isbn", isbn, 1, 1, use_fuzzy=False)
    else:
        return redirect("/booklist?message=ISBN Invalid")

    if books:
        book = books.copy()[0]

        if isinstance(book.get("publishedDate"), dict):
            book["publishedDate"] = book["publishedDate"]["date"][:10]
        elif book.get("publishedDate"):
            book["publishedDate"] = book["publishedDate"][:10]
        else:
            book["publishedDate"] = "N/A"

        isAvailable = db_book.getAvailable_bookid(isbn) is not None

        return render_template(
            "book_details.html",
            book=book,
            user_role=user_role,
            username=username,
            isAvailable=isAvailable,
        )
    else:
        return redirect("/booklist?message=Book not found")


@bp.route("/add_book", methods=["GET"])
def add_book_page():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    role = db_user.authenticate(username, password)
    if role == "admin":
        error = request.args.get("error", -1)
        error_message = None

        error_messages = [
            "ISBN already exists.",
            "Pages must be a positive integer.",
            "Publication Year invalid.",
        ]
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]

        return render_template("add_book.html", error=error_message, user_role=role, username = username)

    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/add_book", methods=["POST"])
def add_book():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    if db_user.authenticate(username, password) != "admin":
        return redirect("/booklist?message=Permission denied.")

    title = request.form.get("title", None)
    authors = [a.strip() for a in request.form.get("authors", "").split(",")]
    categories = [c.strip() for c in request.form.get("categories", "").split(",")]
    isbn = request.form.get("isbn", None)
    pageCount = request.form.get("pageCount", None)
    publishedDate = request.form.get("publishedDate", None)
    thumbnailUrl = request.form.get("thumbnailUrl", "")
    shortDescription = request.form.get("shortDescription", "")
    longDescription = request.form.get("longDescription", "")

    ok, message_code = db_book.addBook(
        title,
        authors,
        categories,
        isbn,
        pageCount,
        publishedDate,
        thumbnailUrl,
        shortDescription,
        longDescription,
    )
    if ok:
        return redirect("/booklist")
    return redirect(f"/add_book?error={message_code}")


@bp.route("/edit_book", methods=["GET"])
def edit_book_page():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    user_role = db_user.authenticate(username, password)
    if user_role != "admin":
        return redirect("/booklist?message=Permission denied.")
    isbn = request.args.get("isbn", None)
    book = None
    if isbn:
        books, _ = db_book.query_book_by("isbn", isbn, 1, 1, use_fuzzy=False)
    else:
        return redirect("/booklist?message=ISBN Invalid")
    if books:
        book = books.copy()[0]

        session["original_authors"] = book["authors"]
        session["original_categories"] = book["categories"]
        formatted_book = book.copy()
        formatted_book["authors_string"] = (
            ", ".join(book["authors"])
            if isinstance(book["authors"], list)
            else book["authors"]
        )
        formatted_book["categories_string"] = (
            ", ".join(book["categories"])
            if isinstance(book["categories"], list)
            else book["categories"]
        )

        return render_template(
            "edit_book.html",
            book=formatted_book,
            user_role=user_role,
            username=username,
        )
    else:
        return redirect("/booklist?message=Book not found")


@bp.route("/edit_book", methods=["POST"])
def edit_book():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    if db_user.authenticate(username, password) != "admin":
        return redirect("/booklist?message=Permission denied.")
    print(request.form)

    book_id = request.form.get("book_id", "")
    title = request.form.get("title", None)
    authors_input = request.form.get("authors", "")
    categories_input = request.form.get("categories", "")
    isbn = request.form.get("isbn", None)
    pageCount = request.form.get("pageCount", None)
    publishedDate = request.form.get("publishedDate", None)
    thumbnailUrl = request.form.get("thumbnailUrl", "")
    shortDescription = request.form.get("shortDescription", "")
    longDescription = request.form.get("longDescription", "")

    original_authors = session.get("original_authors", [])
    original_categories = session.get("original_categories", [])

    if authors_input == ", ".join(original_authors):
        authors = original_authors
    else:
        authors = [a.strip() for a in authors_input.split(",") if a.strip()]

    if categories_input == ", ".join(original_categories):
        categories = original_categories
    else:
        categories = [c.strip() for c in categories_input.split(",") if c.strip()]

    session.pop("original_authors", None)
    session.pop("original_categories", None)

    ok, message_code = db_book.editBook(
        book_id,
        title,
        authors,
        categories,
        isbn,
        pageCount,
        publishedDate,
        thumbnailUrl,
        shortDescription,
        longDescription,
    )
    if ok:
        return redirect("/booklist")
    return redirect(f"/edit_book?error={message_code}")


@bp.route("/delete_book")
def delete_book():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    if db_user.authenticate(username, password) == "admin":
        isbn = request.args.get("isbn", None)
        print(isbn)

        if db_book.deleteBook(isbn):
            return redirect(f"/booklist?message={isbn} is deleted successfully.")
        else:
            return redirect(
                "/booklist?message=Failed to delete the book. Please try again later."
            )

    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/")
def index():
    return redirect(url_for("books.book_list"))
