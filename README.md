# Student Forum

A simple Django-based student forum application for posting discussions, commenting, and browsing by categories.

## Features

- User registration and login
- Create, edit, and delete posts
- Post categories with filtered views
- Commenting on posts
- Dashboard with user posts and comments

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies: `py -3.11 -m pip install -r requirements.txt`.
3. Apply migrations: `py -3.11 student/studentforum/manage.py migrate`.
4. Create a superuser: `py -3.11 student/studentforum/manage.py createsuperuser`.
5. Run the development server: `py -3.11 student/studentforum/manage.py runserver`.

## Project Structure

- `student/studentforum/` - Django app and project files
- `student/db.sqlite3` - SQLite database file
- `README.md` - project overview and setup instructions

## Notes

- Use the `Categories` page to browse posts by category.
- Use the `New Post` page to create posts assigned to a category.
- If `requirements.txt` is not present, install Django manually with `py -3.11 -m pip install django`.
