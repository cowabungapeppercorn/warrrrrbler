"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        cp = User(
            email="cow@pep.corn",
            username="cowabunga",
            password="peppercorn"
        )

        db.session.add(u)
        db.session.add(cp)
        db.session.commit()

        self.user1 = u
        self.user2 = cp

        self.client = app.test_client()

    def tearDown(self):
        """Remove all db data"""
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        users = User.query.all()
        u = User.query.filter(User.username == self.user1.username).first()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        self.assertIn(u, users)
        self.assertEqual(len(users), 2)

    def test_repr(self):
        """Does repr return what we want?"""

        cow = User.query.filter(User.username == self.user2.username).first()

        self.assertEqual(f'{cow}', f'<User #{cow.id}: cowabunga, cow@pep.corn>')
        self.assertNotEqual(f'{cow}', '<User #51517: user, user@user.user')

    def test_is_following_and_followers(self):
        """Does is_following detect following relationship"""
        u = User.query.filter(User.username == self.user1.username).first()
        cow = User.query.filter(User.username == self.user2.username).first()

        follower = Follows(
            user_being_followed_id=cow.id,
            user_following_id=u.id
        )

        db.session.add(follower)
        db.session.commit()

        self.assertEqual(u.following, [cow])
        self.assertNotEqual(cow.following, [u])
        self.assertEqual(cow.followers, [u])
        self.assertNotEqual(u.followers, [cow])
        self.assertEqual(u.is_following(cow), True)
        self.assertEqual(cow.is_following(u), False)
        self.assertEqual(u.is_followed_by(cow), False)
        self.assertEqual(cow.is_followed_by(u), True)

    def test_User_signup_method(self):
        """Test that User.signup creates a valid user w/ valid credentials"""
        User.signup('new_user', 'email@email.mail', 'passhword', 'picshure.pic')
        db.session.commit()
        users = User.query.all()

        self.assertEqual(len(users), 3)

    def test_cant_create_duplicate_user(self):
        """Test that you cant create user with duplicate username"""
        with self.assertRaises(IntegrityError):

            User.signup(self.user1.username, 'email.com', 'pass', 'somethiß')
            db.session.commit()

    def test_authenticate_valid_user(self):
        """Test that authenticate will return user repr for valid user"""
        test1 = User.signup('test', 'email.com', 'password1', 'pic.url')
        db.session.commit()
        test2 = User.authenticate('test', 'password1')

        self.assertEqual(test1, test2)

    def test_authentication_invalid(self):
        """Test that authentication fails on invalid username or password"""
        User.signup('test', 'email.com', 'password1', 'pic.url')
        db.session.commit()
        test2 = User.authenticate('fail', 'password1')
        test3 = User.authenticate('test', 'badword')

        self.assertEqual(test2, False)
        self.assertEqual(test3, False)
