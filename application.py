import os

import requests

from flask import Flask, session, jsonify, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

from functions import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username": username}).fetchone()

        # Ensure username exists and password is correct
        if not rows or not check_password_hash(rows["hash"], password):
            return render_template('error.html', err="Invalid username and/or password", code=403)

        # Remember which user has logged in
        session["user_id"] = rows["id"]
        session["username"] = rows["username"]

        # Redirect user to search page
        return redirect("/search")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id and username
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""

    # Forget any user_id and username
    session.clear()

    # User submitted form
    if request.method == "POST":

        firstname = request.form.get("firstname")
        surname = request.form.get("surname")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Query database for existing username
        users = db.execute("SELECT * FROM users WHERE username = :username",
                           {"username": username}).fetchone()

        if users:
            err = "Sorry! There is an account already registered with this username. Please select another or log in."
            return render_template("register.html", error='yes', err=err)
        elif not password == confirm:
            err = "Sorry! These passwords don't match."
            return render_template("register.html", error='yes', err=err)
        elif len(password) < 8 or len(password) > 16:
            err = "Sorry! Passwords must be 8 - 16 characters long."
            return render_template("register.html", error='yes', err=err)
        elif password.isalpha():
            err = "Sorry! Passwords must contain both letters and numbers."
            return render_template("register.html", error='yes', err=err)
        elif password.isnumeric():
            err = "Sorry! Passwords must contain both letters and numbers."
            return render_template("register.html", error='yes', err=err)

        # hash password
        passhash = generate_password_hash(password)

        # insert user into db
        db.execute("INSERT INTO users (firstname, surname, username, hash) VALUES (:fn, :sn, :un, :h)",
                   {"fn": firstname, "sn": surname, "un": username, "h": passhash})
        db.commit()

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/search", methods=["GET"])
@login_required
def search():
    return render_template('search.html')


@app.route("/search/<string:type>", methods=["POST"])
@login_required
def results(type):

    if request.method == 'POST':

        if type == 'isbn':

            # define initial variables
            isbn = request.form.get('isbn')

            # query db
            result = db.execute(
                "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

            if result:

                search = f'Exact match for "{isbn}"'

                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + isbn + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE isbn LIKE :isbn", {"isbn": part}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE isbn LIKE :isbn", {"isbn": part}).fetchone()
                matches = matches[0]

                if not others:
                    search = f'No matches for "{isbn}"'
                    return render_template('results.html', result=result, others=others, search=search)
                else:
                    search = f'Exact results for "{isbn}" could not be found.'
                    return render_template('results.html', result=result, others=others, search=search, matches=matches)

        elif type == 'title':

            # define initial variables
            title = request.form.get('title')

            # query db
            result = db.execute(
                "SELECT * FROM books WHERE title = :title", {"title": title}).fetchall()

            if result:

                search = f'Exact match for "{title}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + title + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE title LIKE :title", {"title": part}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE title LIKE :title", {"title": part}).fetchone()
                matches = matches[0]

                if not others:
                    search = f'No matches for "{title}"'
                    return render_template('results.html', result=result, others=others, search=search)
                else:
                    search = f'Exact results for "{title}" could not be found.'
                    return render_template('results.html', result=result, others=others, search=search, matches=matches)

        elif type == 'author':

            # define initial variables
            author = request.form.get('author')

            # query db
            result = db.execute(
                "SELECT * FROM books WHERE author = :author", {"author": author}).fetchall()

            if result:

                search = f'Exact match for "{author}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + author + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE author LIKE :author", {"author": part}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE author LIKE :author", {"author": part}).fetchone()
                matches = matches[0]

                if not others:
                    search = f'No matches for "{author}"'
                    return render_template('results.html', result=result, others=others, search=search)
                else:
                    search = f'Exact results for "{author}" could not be found.'
                    return render_template('results.html', result=result, others=others, search=search, matches=matches)

        elif type == 'quicksearch':

            # define unknown type variable
            search = request.form.get('quicksearch')

            # query db
            result = db.execute(
                "SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author", {"isbn": search, "title": search, "author": search}).fetchall()

            if result:

                search = f'Exact match for "{search}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + search + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": part, "title": part, "author": part}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE isbn LIKE :isbn OR title LIKE :title OR author LIKE :author", {"isbn": part, "title": part, "author": part}).fetchone()
                matches = matches[0]

                if not others:
                    search = f'No matches for "{search}"'
                    return render_template('results.html', result=result, others=others, search=search)
                else:
                    search = f'Exact results for "{search}" could not be found.'
                    return render_template('results.html', result=result, others=others, search=search, matches=matches)

        else:
            return render_template('error', err='Something went wrong!')

    else:
        return redirect(url_for('search', error='yes', err='Something went wrong!'))


@app.route("/book/<string:isbn>", methods=["POST"])
@login_required
def book(isbn):

    if request.method == 'POST':

        # query db
        book = db.execute(
            "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchall()

        # Search goodreads API
        api = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": isbn})

        if api:
            api = api.json()
        else:
            api = 'Unknown'

        return render_template('book.html', book=book, api=api)
