from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length, Email

class UserRegistrationForm(FlaskForm):
    """User registration form"""

    username = StringField("Username", validators=[
        InputRequired(),
        Length(min=1, max=20, message=f"Length must not exceed 20 characters.")
    ])

    email = StringField("Email Address", validators=[
        InputRequired(),
        Email(),
        Length(min=1, max=50)
    ])
    
    password = PasswordField("Password", validators=[
        InputRequired(),
        EqualTo("confirm_password", message="Password fields must match.")
    ])
    
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired()])
    
    first_name = StringField("First Name", validators=[
        InputRequired(),
        Length(min=1, max=30, message=f"Length must not exceed 50 characters.")
    ])
    
    last_name = StringField("Last Name", validators=[
        InputRequired(),
        Length(min=1, max=30, message=f"Length must not exceed 50 characters.")
    ])

class UserLoginForm(FlaskForm):
    """User login form"""

    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators = [InputRequired()])