from flask import Flask, request, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
from models import db, connect_db, add_and_commit, User, Feedback
from forms import UserRegistrationForm, UserLoginForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SECRET_KEY"] = "secret123"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)
db.create_all()

def user_logged_in():
    """Redirects to user profile if user is logged in"""
    
    return session.get("username", False)

@app.route("/")
def home():
    """Redirect to register route if not logged in, to user profile otherwise"""
    username = user_logged_in()

    if user_logged_in():
        return redirect(f"/users/{username}")
    else:
        return redirect("/register")

@app.route("/users/<username>", methods=["GET"])
def user(username):
    """Display user profile"""

    if not user_logged_in():
        return redirect("/")

    user = User.query.filter_by(username=username).first()
    feedbacks = Feedback.query.filter_by(username=username).all()
    return render_template("user.html",
                            title=f"{username}'s Profile",
                            user=user,
                            username=session["username"],
                            feedbacks=feedbacks)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Remove user and feedback from database"""

    if username != session.get("username", None):
        flash("You do not have permission to delete this user.", "danger")
        return redirect(f"/users/{username}")

    User.delete(username)

    flash(f"User {username} has been successfully deleted.", "success")

    session.clear()

    return redirect("/login")

@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Display new feedback form. If validated, add feedback to database, redirect to user profile."""

    if not user_logged_in():
        flash("You must be logged in to view this.", "danger")
        return redirect("/")

    if username != session.get("username", None):
        flash("You do not have permission to add feedback on behalf of another user", "danger")
        return redirect(f"/users/{username}")

    form = FeedbackForm()

    if form.validate_on_submit():
        feedback = Feedback(
            title=form.title.data,
            content=form.content.data,
            username=username
        )
        add_and_commit(feedback)
        flash("Successfully submitted feedback.", "success")
        return redirect("/")
    else:
        return render_template("form.html",
                               title="Add Feedback",
                               form=form,
                               post_url=f"/users/{username}/feedback/add",
                               exit_name="Cancel",
                               exit_path=f"/users/{username}")

@app.route("/feedback/<int:id>/update", methods=["GET", "POST"])
def update_feedback(id):
    """Update feedback form.

        Checks that the author of feedback is logged in.
        Updates feedback upon form validation."""

    if not user_logged_in():
        return redirect("/")
    
    feedback = Feedback.query.get_or_404(id)
    if feedback.username != session["username"]:
        flash("You do not have permission to do this.", "danger")
        return redirect("/")

    form = FeedbackForm()

    if form.validate_on_submit():
        if form.title.data is "" and form.content.data is "":
            return redirect(f"/feedback/{id}/update")
        
        if form.title.data:
            feedback.title = form.title.data
        
        if form.content.data:
            feedback.content = form.content.data
        
        db.session.add(feedback)
        db.session.commit()
        flash("Successfully updated feedback.", "success")
        return redirect("/")
    else:
        return render_template("form.html",
                               title="Update Feedback",
                               form=form,
                               post_url=f"/feedback/{id}/update",
                               exit_name="Cancel",
                               exit_path=f"/users/{feedback.username}")

@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
    """Remove feedback from database."""

    if not user_logged_in():
        return redirect("/")

    if Feedback.query.get_or_404(id).username != session["username"]:
        flash("You do not have permission to do this.", "danger")
    else:
        Feedback.delete(id)
        flash("Successfully deleted feedback.", "success")

    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Display register form, send registration data upon validation"""
    
    if session.get("username", False):
        return redirect("/")

    form = UserRegistrationForm()

    if form.validate_on_submit():
        # POST route
        
        user = User.register(request.form)
        
        add_and_commit(user)

        flash("User account created successfully. Please login to access account features.", "success")

        return redirect("/login")

    else:
        # GET route
        return render_template("form.html",
                               title="Register",
                               post_url="/register",
                               form=form,
                               exit_name="Login",
                               exit_path="/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Display login form, send login credentials upon form validation"""

    if session.get("username", False):
        return redirect("/")
    
    form = UserLoginForm()

    if form.validate_on_submit():
        # POST route
        
        username = form.username.data
        pwd = form.password.data

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
                               form=form,
                               exit_name="Register",
                               exit_path="/register")

@app.route("/logout", methods=["GET"])
def logout():
    """Clears user information from the session, redirect to home"""

    session.clear()
    return redirect("/")

@app.errorhandler(HTTPException)
def handle_exception(e):

    if isinstance(e, HTTPException):
        return render_template("error.html", title=f"Error", err=e)
    else:
        return render_template("error.html", title=f"Error"), 500