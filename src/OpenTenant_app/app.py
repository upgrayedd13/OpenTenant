from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os

from .config import DevelopmentConfig, ProductionConfig
from .models import db, User
from .forms import LoginForm, RegisterForm

# Initialize extensions (without app yet)
login_manager = LoginManager()
login_manager.login_view = "login"

def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_prefixed_env()

    env = os.getenv("FLASK_ENV", "development")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # TODO: Clean all of this up with routes

    # Routes
    @app.route("/")
    def homepage():
        return render_template('pages/index.html')

    @app.route("/about")
    def about():
        return render_template('pages/about.html')

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                remember = request.form.get("remember") == "on"  # True if checkbox checked
                login_user(user, remember=remember)  # <-- remember=True keeps session across browser restarts
                return redirect(url_for("dashboard"))
            flash("Invalid credentials")
        return render_template("pages/login.html", form=form)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash("Username already exists")
                return redirect(url_for("register"))

            user = User(username=form.username.data)
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash("Account created. Please log in.")
            return redirect(url_for("login"))

        return render_template("pages/register.html", form=form)

    @app.route("/account")
    @login_required
    def account():
        return render_template("pages/account.html", user=current_user)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/contact")
    def contact():
        return render_template('pages/contact.html')

    @app.route("/bug")
    def bug():
        return render_template('pages/bug_report.html')

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
