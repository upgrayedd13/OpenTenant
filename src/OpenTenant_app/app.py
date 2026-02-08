# from flask import Flask
# from .config import Config
# from .blueprints.main.routes import main_bp

from flask import Flask, render_template, request, redirect, url_for
from .models import db, Submission

# def create_app():
    # app = Flask(__name__)

    # app.register_blueprint(main_bp)

    # return app

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev"

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/", methods=["GET", "POST"])
    def form():
        if request.method == "POST":
            submission = Submission(
                name=request.form["name"],
                email=request.form["email"],
            )
            db.session.add(submission)
            db.session.commit()
            return redirect(url_for("form"))

        return render_template("form.html")

    @app.route("/submissions")
    def submissions():
        all_submissions = Submission.query.all()
        return render_template("submissions.html", submissions=all_submissions)

    return app
