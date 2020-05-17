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

# define class for percentages in user ratings


class Perc:
    def __init__(self, five, four, three, two, one):
        self.five = five
        self.four = four
        self.three = three
        self.two = two
        self.one = one


@app.route("/")
def index():

    # Forget any user_id and username
    session.clear()

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

        # password and username complexity conditions
        if users:
            err = "Sorry! There is an account already registered with this username. Please select another or log in."
            return render_template("register.html", error='yes', err=err)
        elif password == username:
            err = "Sorry! Your password must be different to your username."
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
        elif len(username) < 8:
            err = "Sorry! Usernames must be at least 8 characters long."
            return render_template("register.html", error='yes', err=err)
        elif username.isalpha():
            err = "Sorry! Usernames must contain both letters and numbers."
            return render_template("register.html", error='yes', err=err)
        elif username.isnumeric():
            err = "Sorry! Usernames must contain both letters and numbers."
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
    """display search page"""
    return render_template('search.html')


@app.route("/search/<string:type>", methods=["POST"])
@login_required
def results(type):
    """display search results """

    if request.method == 'POST':

        if type == 'isbn':

            # define initial variables
            isbn = request.form.get('isbn')

            if not isbn.isnumeric():
                err = 'Invalid ISBN: Must contain only numbers.'
                return render_template('search.html', error='yes', err=err)

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
                    "SELECT * FROM books WHERE isbn LIKE :isbn ORDER BY isbn", {"isbn": part}).fetchall()

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
                "SELECT * FROM books WHERE UPPER(title) = :title", {"title": title.upper()}).fetchall()

            if result:

                search = f'Exact match for "{title}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + title + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE UPPER(title) LIKE :title ORDER BY title", {"title": part.upper()}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE UPPER(title) LIKE :title", {"title": part.upper()}).fetchone()
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
                "SELECT * FROM books WHERE UPPER(author) = :author", {"author": author.upper()}).fetchall()

            if result:

                search = f'Exact match for "{author}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + author + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE UPPER(author) LIKE :author ORDER BY author", {"author": part.upper()}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE UPPER(author) LIKE :author", {"author": part.upper()}).fetchone()
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
                "SELECT * FROM books WHERE isbn = :isbn OR UPPER(title) = :title OR UPPER(author) = :author", {"isbn": search, "title": search.upper(), "author": search.upper()}).fetchall()

            if result:

                search = f'Exact match for "{search}"'
                return render_template('results.html', result=result, search=search)

            elif not result:

                # Look for partial match in db
                part = '%' + search + '%'

                others = db.execute(
                    "SELECT * FROM books WHERE isbn LIKE :isbn OR UPPER(title) LIKE :title OR UPPER(author) LIKE :author", {"isbn": part, "title": part.upper(), "author": part.upper()}).fetchall()

                matches = db.execute(
                    "SELECT COUNT(*) FROM books WHERE isbn LIKE :isbn OR UPPER(title) LIKE :title OR UPPER(author) LIKE :author", {"isbn": part, "title": part.upper(), "author": part.upper()}).fetchone()
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


@app.route("/book/<string:isbn>", methods=["GET", "POST"])
@login_required
def book(isbn):
    """display book details and reviews"""

    if request.method == 'GET':

        # query db for book details
        book = db.execute(
            "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()

        # query db for rating details
        counts = db.execute(
            "SELECT COUNT(rating), AVG(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book", {"book": book['id']}).fetchone()

        coms = db.execute(
            "SELECT COUNT(comment) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND reviews.comment != '' ", {"book": book['id']}).fetchone()

        if not counts[0] == 0:

            five = db.execute(
                "SELECT COUNT(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND rating = '5'", {"book": book['id']}).fetchone()

            four = db.execute(
                "SELECT COUNT(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND rating = '4'", {"book": book['id']}).fetchone()

            three = db.execute(
                "SELECT COUNT(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND rating = '3'", {"book": book['id']}).fetchone()

            two = db.execute(
                "SELECT COUNT(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND rating = '2'", {"book": book['id']}).fetchone()

            one = db.execute(
                "SELECT COUNT(rating) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book AND rating = '1'", {"book": book['id']}).fetchone()

            # get percentage share of ratings
            percfive = (five[0] / counts[0])*100
            percfour = (four[0] / counts[0])*100
            percthree = (three[0] / counts[0])*100
            perctwo = (two[0] / counts[0])*100
            percone = (one[0] / counts[0])*100

            perc = Perc(percfive, percfour, percthree, perctwo, percone)

            # query db for review details
            reviews = db.execute(
                "SELECT username, comment, rating FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book", {"book": book['id']}).fetchall()

            # Search goodreads API
            api = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": isbn})

            if api:
                api = api.json()
            else:
                api = 'Unknown'

            return render_template('book.html', book=book, api=api, reviews=reviews, counts=counts, five=five, four=four, three=three, two=two, one=one, perc=perc, coms=coms[0])
        else:
            # Search goodreads API
            api = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": isbn})

            if api:
                api = api.json()
            else:
                api = 'Unknown'

            return render_template('book.html', book=book, api=api)

    else:
        # Search goodreads API
        api = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": isbn})

        if api:
            api = api.json()
        else:
            api = 'Unknown'

        return render_template('book.html', api=api)


@app.route("/review/<string:ident>/<string:isbn>/add", methods=["POST"])
def addreview(ident, isbn):
    """Add review to db"""

    # get user submitted info
    userID = session['user_id']
    comment = request.form.get("addcomment")
    rating = request.form.get("rating")

    # Query database for existing user review
    exist = db.execute("SELECT * FROM reviews WHERE userID = :user AND bookID = :book",
                       {"user": userID, "book": ident}).fetchone()

    if exist:
        err = f'Sorry! Could not post this review for book with isbn: {isbn}. You have already reviewed this book. We only allow one review per book per user.'
        return render_template('error.html', isbn=isbn, error='yes', err=err)

    # insert into db
    db.execute("INSERT INTO reviews (userID, bookID, comment, rating) VALUES (:uid, :book, :com, :rat)",
               {"uid": userID, "book": ident, "com": comment, "rat": rating})
    db.commit()

    return redirect(url_for('book', isbn=isbn))


# Access via API route
@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    """call api response"""

    if request.method == 'GET':

        # query db for book details
        book = db.execute(
            "SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        
        if not book:
            return jsonify('Book not found.'), 404

        counts = db.execute(
            "SELECT COUNT(rating), ROUND(AVG(rating),1) FROM ((reviews JOIN books on reviews.bookID = books.id) JOIN users ON reviews.userID = users.id) WHERE books.id = :book", {"book": book['id']}).fetchone()

        # define response details
        data = jsonify({
            "title": book[2],
            "author": book[3],
            "year": book[4],
            "isbn": book[1],
            "review_count": counts[0],
            "average_score": float(counts[1])
        })

        return data, 200