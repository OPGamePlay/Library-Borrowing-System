from flask import Blueprint, request, redirect, render_template, make_response
import time
from app.models.user import db_user

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET"])
def login_required():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    error = request.args.get("error", -1)
    if username and password and db_user.authenticate(username, password) != "guest":
        return redirect("/booklist")
    else:
        error_message = None

        error_messages = [
            "Username and Password are required",
            "Invalid Username or Password",
        ]
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]

        return render_template("login.html", error=error_message)


@bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", None)
    password = request.form.get("password", None)
    print(username, password)
    if username and password:
        if db_user.authenticate(username, password):
            res = make_response(redirect("/booklist"))
            res.set_cookie("username", username, expires=time.time() + 3600)
            res.set_cookie("password", password, expires=time.time() + 3600)

            return res
        else:
            return redirect("/login?error=1")

    else:
        return redirect("/login?error=0")


@bp.route("/register", methods=["POST"])
def registration():
    username = request.form.get("username", None)
    password = request.form.get("password", None)
    if username and password:
        if db_user.register(username, password):
            res = make_response(redirect("/booklist"))
            res.set_cookie(key="username", value=username, expires=time.time() + 3600)
            res.set_cookie(key="password", value=password, expires=time.time() + 3600)
            return res
        else:
            return redirect("/register?error=1")

    else:
        return redirect("/register?error=0")


@bp.route("/register", methods=["GET"])
def register():
    username = request.cookies.get("username", None)
    password = request.cookies.get("password", None)
    error = request.args.get("error", -1)
    if username and password and db_user.authenticate(username, password) != "guest":
        return redirect("/booklist")
    else:
        error_message = None
        error_messages = [
            "Username and Password are required",
            "Invalid Username or Password",
        ]
        if int(error) < len(error_messages) and int(error) >= 0:
            error_message = error_messages[int(error)]

        return render_template("register.html", error=error_message)


@bp.route("/logout")
def logout():
    res = make_response(redirect("/booklist"))
    res.set_cookie("username", "None", expires=0)
    res.set_cookie("password", "None", expires=0)
    return res
