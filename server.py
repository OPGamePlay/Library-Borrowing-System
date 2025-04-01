from flask import Flask, redirect, url_for


def run_app():
    app = Flask(__name__)

    from app.routes import auth, books, library, users

    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(library.bp)
    app.register_blueprint(users.bp)
    return app


app = run_app()
app.secret_key = "secret_key_for_session"


@app.route("/")
def index():
    return redirect(url_for("books.book_list"))


if __name__ == "__main__":
    app.run(debug=True)
