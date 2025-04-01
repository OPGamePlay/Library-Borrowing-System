from flask import Blueprint, request, redirect, render_template
import datetime
from app.models.user import db_user
from app.models.book import db_book

bp = Blueprint("library", __name__)


@bp.route("/lib_return_book", methods=["GET"])
def return_book_page():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    role = db_user.authenticate(username, password)
    if role == "admin":
        code = request.args.get("message", -1)
        message = None
        messages = [
            "Book returned successfully.",
            "Book ISBN does not exist.",
            "Book has not been borrowed yet.",
        ]
        if int(code) < len(messages) and int(code) >= 0:
            message = messages[int(code)]

        return render_template(
            "lib_return.html", message=message, user_role=role, username=username
        )
    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/lib_return_book", methods=["POST"])
def return_book():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    book_id = request.form["book_id"]
    isbn = request.form["isbn"]
    role = db_user.authenticate(username, password)
    if role == "admin":
        _, lib_book = db_book.get_borrowed_book(book_id, isbn)

        if lib_book:
            Book_info, _ = db_book.query_book_by(
                "isbn", lib_book["isbn"], 1, 1, use_fuzzy=False
            )
            if Book_info and lib_book["due_date"] is not None:
                Duedate = datetime.datetime.strptime(lib_book["due_date"], "%Y-%m-%d")
                diff = datetime.datetime.now() - Duedate
                if diff.days > 0:
                    days_late = diff.days
                    fine = days_late * 5
                else:
                    days_late = 0
                    fine = 0
                return render_template(
                    "lib_return_confirm.html",
                    book=Book_info[0],
                    book_id=book_id,
                    isbn=isbn,
                    fine=fine,
                    days_late=days_late,
                    user_role=role,
                    username=username,
                )
            else:
                return redirect("/lib_return_book?message=2")

        else:
            return redirect("/lib_return_book?message=1")
    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/lib_return_confirm", methods=["GET"])
def lib_return_confirm():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    role = db_user.authenticate(username, password)
    if role == "admin":
        book_id = request.args.get("book_id", "")
        isbn = request.args.get("isbn", "")
        db_book.return_book(book_id, isbn)
        return redirect("/lib_return_book?message=0")

    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/borrow")  # type: ignore
def book_borrow():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    user_role = db_user.authenticate(username, password)
    if user_role == "user" or user_role == "admin":
        isbn = request.args.get("isbn", None)
        bookID = db_book.getAvailable_bookid(isbn)

        if bookID is not None:
            _, due_date = db_book.library_book_borrow(bookID, username)
            return redirect(
                f"/booklist?message=Book ID ({bookID}) has been lent to you. Please return before {due_date}."
            )
        else:
            return redirect("/book_details?isbn=%s" % isbn)


# @bp.route("/lib_book_register", methods=["GET"])
# def lib_book_register():
#     username = request.cookies.get("username", None)
#     password = request.cookies.get("password", None)
#     role = db_user.authenticate(username, password)
#     if role == "admin":
#         p = request.args.get("p", "")
#         error = request.args.get("error", -1)
#         message = None
#
#         messages = ["Book registered successfully.", "Book registration failed."]
#         if int(error) < len(messages) and int(error) >= 0:
#             message = messages[int(error)]
#
#         return render_template(
#             "lib_book_register.html", message=message, previous_isbn=p, user_role=role
#         )
#     else:
#         return redirect("/booklist?message=Permission denied.")
#
#
# @bp.route("/lib_book_register", methods=["POST"])
# def lib_book_registry():
#     username = request.cookies.get("username", None)
#     password = request.cookies.get("password", None)
#
#     if db_user.authenticate(username, password) == "admin":
#         isbn = request.form.get("isbn", None)
#         book_id = request.form.get("bookid", None)
#         print(isbn, book_id)
#         if db_book.library_book_registry(isbn, book_id):
#             return redirect(f"/lib_book_register?message=0&p={isbn}")
#
#         else:
#             return redirect(f"/lib_book_register?message=1&p={isbn}")
#
#     else:
#         return redirect("/booklist?message=Permission denied.")
#
