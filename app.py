from flask import Flask, request, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, add_and_commit, User
from forms import UserRegistrationForm, UserLoginForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)
db.create_all()

@app.route("/")
def home():
    """Redirect to register route"""
    session.clear()
    return redirect("/register")

@app.route("/secret")
def secret():

    if session.get("username", False):
        return render_template("secret.html", title="Secret")
    else:
        flash("You do not have permission to view this.", "danger")
        return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Display register form, send registration data upon validation"""

    form = UserRegistrationForm()

    if form.validate_on_submit():
        # POST route
        
        user = User.register(request.form)
        
        add_and_commit(user)

        return redirect("/secret")

    else:
        # GET route
        return render_template("form.html",
                               title="Register",
                               post_url="/register",
                               form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login form, send login credentials upon form validation"""

    form = UserLoginForm()

    if form.validate_on_submit():
        # POST route
        
        username = request.form["username"]
        pwd = request.form["password"]

        user = User.authenticate(username, pwd)

        if user:
            session["username"] = username
            flash(f"Successfully logged in as {username}", "success")
            return redirect("/secret")
        
        else:
            flash("Failed to login.", "danger")
            return redirect("/login")
    
    else:
        # GET route
        return render_template("form.html",
                               title="Login",
                               post_url="/login",
                               form=form)
