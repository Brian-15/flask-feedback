from models import User, Feedback
from app import app, db

db.drop_all()
db.create_all()

user1 = User.register({
    "username": "test_user1",
    "email": "test1@test.net",
    "password": "test123",
    "first_name": "Test1",
    "last_name": "Tests"
})
user2 = User.register({
    "username": "test_user2",
    "email": "test2@test.net",
    "password": "test123",
    "first_name": "Test2",
    "last_name": "Tests"
})

user3 = User.register({
    "username": "test_user3",
    "email": "test3@test.net",
    "password": "test123",
    "first_name": "Test3",
    "last_name": "Tests"
})

db.session.add_all([user1, user2, user3])
db.session.commit()

feedback1_1 = Feedback(
    title="Feedback1",
    content="This is an example feedback",
    username="test_user1"
)

feedback2_1 = Feedback(
    title="Feedback2",
    content="This is an example feedback",
    username="test_user1"
)

feedback3_2 = Feedback(
    title="Feedback3",
    content="This is an example feedback",
    username="test_user2"
)

db.session.add_all([feedback1_1, feedback2_1, feedback3_2])
db.session.commit()