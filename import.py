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

# import books from CSV file into database
fname = "books.csv"

# read csv data
with open(fname, 'r') as data:
    read = csv.DictReader(data)

    for row in read:
        isbn = row['isbn']
        title = row['title']
        author = row['author']
        year = row['year']

        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :ti, :auth, :y)",
                   isbn=isbn, title=title, auth=author, y=year)
