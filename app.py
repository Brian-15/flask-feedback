from flask import Flask, request, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from models import db, connect_db, add_and_commit, User, Feedback
from forms import UserRegistrationForm, UserLoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)
db.create_all()

def check_user():
    """Redirects to user profile if user is logged in"""
    username = session.get("username", False)

    if username:
        return redirect(f"/users/{username}")

@app.route("/")
def home():
    """Redirect to register route"""
    return redirect("/register")

@app.route("/users/<username>", methods=["GET"])
def user(username):
    """Display user profile"""

    if session.get("username", False):
        user = User.query.filter_by(username=username).first()
        feedbacks = Feedback.query.filter_by(username=username).all()
        return render_template("user.html", title=f"{username}'s Profile", user=user, feedbacks=feedbacks)
    else:
        flash("You must be logged in to view user profiles.", "danger")
        return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Display register form, send registration data upon validation"""
    
    check_user()

    form = UserRegistrationForm()

    if form.validate_on_submit():
        # POST route
        
        user = User.register(request.form)
        
        add_and_commit(user)

        return redirect("/login")

    else:
        # GET route
        return render_template("form.html",
                               title="Register",
                               post_url="/register",
                               form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login form, send login credentials upon form validation"""

    check_user()
    
    form = UserLoginForm()

    if form.validate_on_submit():
        # POST route
        
        username = request.form["username"]
        pwd = request.form["password"]

        user = User.authenticate(username, pwd)

        if user:
            session["username"] = username
            flash(f"Successfully logged in as {username}", "success")
            return redirect(f"/users/{username}")
        
        else:
            flash("Failed to login.", "danger")
            return redirect("/login")
    
    else:
        # GET route
        return render_template("form.html",
                               title="Login",
                               post_url="/login",
                               form=form)

@app.route("/logout", methods=["GET"])
def logout():
    """Clears user information from the session, redirect to home"""

    session.clear()
    return redirect("/")

@app.errorhandler(HTTPException)
def handle_exception(e):

    if isinstance(e, HTTPException):
        return render_template("error.html", title=f"Error: {e.name}", err=e)
    else:
        return render_template("error.html", title=f"Error: {e.name}"), 500