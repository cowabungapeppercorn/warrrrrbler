"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from psycopg2 import IntegrityError
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.othertester = User.signup(username="testing",
                            email="test@testp.com",
                            password="testuser",
                            image_url=None)

        db.session.commit()

    def tearDown(self):
        """Remove all db data"""
        db.session.rollback()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_user_auth_add_message(self):
        "Can a non-user add a message?"
        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"},
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            messages = Message.query.all()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(messages), 0)
            self.assertIn('<h4>New to Warbler?</h4>', html)

    def test_user_auth_delete_message(self):
        "Can a non-user delete a message?"
        with self.client as c:
            otheruser = User.query.filter(User.username == "testing").first()
            new_message = Message(text="Whatevas", user_id=otheruser.id)
            
            db.session.add(new_message)
            db.session.commit()

            resp = c.post(f"/messages/{new_message.id}/delete",
                          follow_redirects=True)

            html = resp.get_data(as_text=True)

            messages = Message.query.all()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(messages), 1)
            self.assertIn('<h4>New to Warbler?</h4>', html)

    def test_user_delete_message(self):
        """Can the user delete their own message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})

            message = Message.query.first()

            resp = c.post(f"/messages/{message.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            messages = Message.query.all()


            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(messages), 0)
            self.assertIn('col-sm-6', html)

    def test_other_user_delete_message(self):
        """Can a user who is not the creator delete a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            otheruser = User.query.filter(User.username == "testing").first()
            new_message = Message(text="Whatevas", user_id=otheruser.id)

            db.session.add(new_message)
            db.session.commit()

            resp = c.post(f"/messages/{new_message.id}/delete", follow_redirects=True)

            messages = Message.query.all()
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(messages), 1)
            self.assertIn('col-md-8', html)

