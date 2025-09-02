# ===============================
# Built-in Python modules
# ===============================
from datetime import date, datetime # To handle dates
from functools import wraps  # To create custom decorators

# ===============================
# Flask core and extensions
# ===============================
from flask import Flask, abort, request, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import (
    UserMixin,
    login_user,
    logout_user,
    LoginManager,
    login_required,
    current_user
)
from flask_sqlalchemy import SQLAlchemy

# ===============================
# SQLAlchemy specific
# ===============================
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text

# ===============================
# Security
# ===============================
from werkzeug.security import generate_password_hash, check_password_hash

# ===============================
# Custom modules (Forms)
# ===============================
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm


# ===============================
# Flask app configuration
# ===============================
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# ===============================
# Configure Flask-Login
# ===============================
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Load a user by ID (required by Flask-Login)
    return db.get_or_404(User, user_id)

# For adding profile images to comments
gravatar = Gravatar(app, size=100, rating='g', default='retro')


# ===============================
# Database configuration
# ===============================
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# ===============================
# DATABASE TABLES
# ===============================

# BlogPost table: Stores blog posts
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    project_url: Mapped[str] = mapped_column(String(250), nullable=True)
    comments = relationship("Comment", back_populates="parent_post")  # Relationship to comments


# User table: Stores registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")  # Relationship to user's posts
    comments = relationship("Comment", back_populates="comment_author")  # Relationship to user's comments


# Comment table: Stores comments for blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")


# Message table: Stores messages from contact form
class Message(db.Model):
    __tablename__ = "messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    phone: Mapped[str] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.now)


with app.app_context():
    db.create_all()  # Create all tables in database


# ===============================
# Admin-only decorator
# ===============================
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:  # Check if user is logged in
            return abort(403)  # Forbidden
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ===============================
# ROUTES
# ===============================

# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    # Allows new users to sign up
    form = RegisterForm()
    if form.validate_on_submit():
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(email=form.email.data, name=form.name.data, password=hash_and_salted_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


# Login route
@app.route('/login', methods=["GET", "POST"])
def login():
    # Authenticate existing users
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)


# Logout route
@app.route('/logout')
def logout():
    # Log out current user
    logout_user()
    return redirect(url_for('get_all_posts'))


# Home route
@app.route('/')
def get_all_posts():
    # Display all blog posts
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route("/how-it-works")
def how_it_works():
    return render_template("how_it_works.html", current_user=current_user)


# Show post with comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    # Display single blog post and handle comment submission
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))
        new_comment = Comment(text=comment_form.comment_text.data, comment_author=current_user, parent_post=requested_post)
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


# Create new post (admin only)
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    # Admin can create a new blog post
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            project_url=form.project_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


# Edit post route
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    # Admin can edit an existing post
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(title=post.title, subtitle=post.subtitle, img_url=post.img_url, author=post.author, body=post.body)
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


# Delete post route (admin only)
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# About page route
@app.route("/about")
def about():
    # Render the about page
    return render_template("about.html", current_user=current_user)


# Contact page route
@app.route("/contact", methods=["GET", "POST"])
def contact():
    # Handle contact form submission
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message_text = request.form.get("message")
        new_message = Message(name=name, email=email, phone=phone, message=message_text)
        db.session.add(new_message)
        db.session.commit()
        flash("✅ Your message has been sent successfully!", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", current_user=current_user)


# Admin messages route
@app.route("/admin/messages")
@admin_only
@login_required
def admin_messages():
    # Admin can view all contact messages
    messages = Message.query.order_by(Message.date.desc()).all()
    return render_template("admin_messages.html", messages=messages, current_user=current_user)


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)

# Day 71: publishing Our Flask Website --> Git and Githup and HEROKU and gunicorn --> the final khaled-flask-blog-herokuapp.com
