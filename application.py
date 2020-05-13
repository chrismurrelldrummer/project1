import os

import requests

from flask import Flask, session, jsonify, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

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

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template('error', err="Invalid username and/or password", code=403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to search page
        return redirect("/search/search")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id and username
    session.clear()

    # Redirect user to home page
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register new user"""

    # User submitted form
    if request.method == "POST":

        password = request.form.get("password")
        confirm = request.form.get("confirm-password")

        if not password == confirm:
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

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/search/<string:type>", methods=["GET", "POST"])
def search(type):

    if request.method == 'post':
        if type == 'isbn':

            isbn = request.form.get('isbn')

            # Access goodreads API
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": isbn})
            res = re.json()

            return render_template('results', res=res)

        elif type == 'title':

            title = request.form.get('title')

            # query API for title or partial
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "q6gj5umJdwuDCz5OX61pwg", "titles": title})
            res = re.json()

            return render_template('results', res=res)

        elif type == 'author':

            author = request.form.get('author')

            # query API for author or partial
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "q6gj5umJdwuDCz5OX61pwg", "authors": author})
            res = re.json()

            return render_template('results', res=res)

        else:
            return render_template('error', err='Something went wrong!')

    else:
        return render_template('search.html')
