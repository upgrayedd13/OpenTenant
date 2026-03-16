from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def homepage():
    return render_template('pages/index.html')


@main_bp.route("/about")
def about():
    return render_template('pages/about.html')


@main_bp.route("/contact")
def contact():
    return render_template('pages/contact.html')


@main_bp.route("/bug")
def bug():
    return render_template('pages/bug_report.html')


@main_bp.route("/admin")
def admin():
    return render_template("pages/admin.html")
