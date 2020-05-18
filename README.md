# Project 1

Web Programming with Python and JavaScript


I named this book review site "BookLook" and it allows you to register and leave reviews.

The main functionality is found in application.py where each page and the API route are defined. The functions.py file is imported by this main file to allow a restriction to pages that non-logged in users can view. This function was taken directly from the CS50 finance project and has not been written by me.

Import.py was used to insert the books into the database. I have included a commented section of SQL commands that I used to create the database tables, however these were run separately.

Styling is found in the "styles" CSS file and "altstyles" SCSS file, however most of the styling used is from Bootstrap 4 classes. The star rating inputs are adapted from the sites quoted in the comment line above their style section.

The gitignore file excludes any setup files (env for vscode) and also my config file which is where I store text versions os database url etc. This was intended for me to copy and paste for faster set up.