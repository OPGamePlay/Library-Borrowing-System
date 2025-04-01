from flask import Blueprint, request, redirect, render_template
from app.models.user import db_user

bp = Blueprint("users", __name__)


@bp.route("/users")
def users():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    query = request.args.get("query", "")
    page = request.args.get("page", 1)
    count_per_page = 10
    skip = (int(page) - 1) * count_per_page

    user_role = db_user.authenticate(username, password)
    results = []
    if user_role == "admin":
        for user in db_user.authJson.keys():
            if skip > 0:
                skip -= 1
                continue
            if len(results) == count_per_page:
                break
            if query in user:
                results.append(user)

        total_pages = len(db_user.authJson.keys()) // count_per_page + (
            1 if len(db_user.authJson) % count_per_page != 0 else 0
        )
        return render_template(
            "users.html",
            current_page=page,
            total_pages=total_pages,
            users=results,
            user_role=user_role,
            username=username,
        )
    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/set_password")
def set_password():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    user_role = db_user.authenticate(username, password)
    if user_role == "admin":
        target_username = request.args.get("username", None)
        new_password = request.args.get("new_password", None)
        db_user.set_password(target_username, new_password)
        return redirect("/booklist?message=Password updated successfully.")
    else:
        return redirect("/booklist?message=Permission denied.")


@bp.route("/delete_user", methods=["GET"])
def users_delete():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    user_role = db_user.authenticate(username, password)
    if user_role == "admin":
        username_to_delete = request.args.get("username", None)
        if username_to_delete in db_user.authJson.keys():
            db_user.delete_user(username_to_delete)
            return redirect("/booklist?message=User deleted successfully.")
        else:
            return redirect("/booklist?message=User not found.")
    else:
        return redirect("/booklist?message=Permission denied.")
