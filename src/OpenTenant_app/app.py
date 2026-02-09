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
    print(os.getenv("FLASK_SECRET_KEY"))
    print(app.config['SECRET_KEY'])

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Routes
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

        return render_template("register.html", form=form)

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
        return render_template("login.html", form=form)

    @app.route("/", methods=["GET", "POST"])
    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", user=current_user)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
