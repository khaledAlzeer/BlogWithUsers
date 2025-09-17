# Khaled Blog – Full Project Description

## Project Overview
Khaled Blog is a Flask-based blogging platform where users can register, log in, read posts, and leave comments. The admin (Khaled) can manage posts and comments.

## Features

**Regular Users:**  
- Register, login, read posts, leave comments (with Gravatar).

**Admin (Khaled):**  
- Create, edit, delete posts, moderate comments, access admin-only routes.

## Database Structure

- **Users:** id, name, email, hashed_password  
- **Posts:** id, title, subtitle, date, body, img_url, author_id, project_link (optional URL)  
- **Comments:** id, text, author_id, post_id  
- **Messages:** id, name, email, phone, message, date  

## Security

- Passwords hashed with Werkzeug  
- Sessions managed with Flask-Login  
- Admin-only routes protected  
- Forms validated with Flask-WTF (CSRF protection)  

## Front-End

- Bootstrap 5 for responsive design  
- Clean Blog template, post headers with background images  
- Comment section with avatars  

## Back-End

- Flask app structure with SQLAlchemy ORM  
- Routes for registration, login, logout, posts, commenting, admin management  
- CKEditor for rich text  
- Authentication with Flask-Login  

## Additional Notes

- `project_link` in posts is optional: use it if the post represents a live website.  
- Regular users can only comment and read posts.  
- Admin (Khaled) has full control.  
