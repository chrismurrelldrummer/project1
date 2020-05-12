import os
import csv

import requests

from flask import Flask, session, jsonify, redirect, render_template, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

    # Access test goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "q6gj5umJdwuDCz5OX61pwg", "isbns": "9781632168146"})

    return render_template("index.html", res=res.json())
