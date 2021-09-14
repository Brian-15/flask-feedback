from typing import ContextManager
import bcrypt
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect database"""
    
    db.app = app
    db.init_app(app)

def add_and_commit(model):
    """Add model and commit"""

    db.session.add(model)
    db.session.commit()

class User(db.Model):
    """User model class"""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                         primary_key=True,
                         unique=True)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable=False,
                      unique=True)
    
    first_name = db.Column(db.String(30),
                           nullable=False)
    
    last_name = db.Column(db.String(30),
                          nullable=False)

    def get_full_name(self):
        """Return string of user full name"""

        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Display user instance"""

        return f"<User {self.username} {self.get_full_name()}>"
    
    @classmethod
    def register(cls, user_data):
        """Registers new user. Returns class instance of new user."""

        hashed = bcrypt.generate_password_hash(user_data["password"])
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=user_data["username"],
                   password=hashed_utf8,
                   email=user_data["email"],
                   first_name=user_data["first_name"],
                   last_name=user_data["last_name"])
    
    @classmethod
    def authenticate(cls, username, pwd):
        """Log in user. If user exists, return user instance. Else, return False"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        
        else:
            return False
    
    @classmethod
    def delete(cls, username):
        """Remove user of username and all their feedback"""

        Feedback.delete_from_user(username)
        cls.query.filter_by(username=username).delete()
        db.session.commit()

        

class Feedback(db.Model):

    __tablename__ = "feedback"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    title = db.Column(db.String(100),
                      nullable=False)

    content = db.Column(db.Text,
                        nullable=False)

    username = db.Column(db.String(20),
                         db.ForeignKey("users.username"))
    
    @classmethod
    def delete(cls, id):
        """Removes feedback of id"""
        
        cls.query.filter_by(id=id).delete()
        db.session.commit()

    @classmethod
    def delete_from_user(cls, username):
        """Removes all feedback authored by user of username"""

        cls.query.filter_by(username=username).delete()
        db.session.commit()
        

    