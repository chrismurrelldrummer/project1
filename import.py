import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# set up database tables
db.execute(CREATE TABLE books(id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL))

db.execute(CREATE TABLE users(id SERIAL PRIMARY KEY, firstname VARCHAR NOT NULL, surname VARCHAR NOT NULL, username VARCHAR UNIQUE NOT NULL, hash TEXT NOT NULL))

db.execute(CREATE TABLE reviews(id SERIAL PRIMARY KEY, userID INTEGER NOT NULL REFERENCES users, bookID INTEGER NOT NULL REFERENCES books, rating INTEGER NOT NULL CHECK(rating <= 5 AND rating >= 1), comment TEXT))

# create file variable
fname = "books.csv"

# read and insert csv data
with open(fname, 'r') as data:
    read = csv.reader(data)

    for isbn, title, author, year in read:

        if isbn == 'isbn':
            continue
        else:
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                       {"isbn": isbn, "title": title, "author": author, "year": year})

    db.commit()

print('Import Successful!')

# Query database for import check of first item
book = db.execute("SELECT * FROM books").fetchone()
print(book)
