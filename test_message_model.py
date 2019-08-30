"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages"""

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

        self.client = app.test_client()

    def tearDown(self):
        """Remove all db data"""
        db.session.rollback()

    def test_message_start(self):
        """Does the user start with zero messages?"""

        u = User.query.filter(User.username == 'testuser').first()

        # User should have no messages
        self.assertEqual(len(u.messages), 0)

    def test_add_message(self):
        """Can the user add a message?"""

        u = User.query.filter(User.username == 'testuser').first()

        new_message = Message(text="Dasterly depths round the arrow.", user_id=u.id)
        
        db.session.add(new_message)
        db.session.commit()

        self.assertEqual(Message.query.count(), 1)
        
    def test_relationship_of_messages_and_user(self):
        """Can we access the user from the message?"""
        u = User.query.filter(User.username == 'testuser').first()

        new_message = Message(text="Dasterly depths round the arrow.", user_id=u.id)
        
        db.session.add(new_message)
        db.session.commit()
        self.assertEqual(new_message.user.id, u.id)

    def test_fail_to_create_message_user_error(self):
        """If we fail to put in the user required does the message still get created?"""
        with self.assertRaises(IntegrityError):

            fail_message = Message(text="Nothing fails further calling. Computer job seeking")
            db.session.add(fail_message)
            db.session.commit()

            self.assertEqual(Message.query.count(), 0)

    def test_fail_to_create_message_text_error(self):
        """If we fail to put in the text required does the message still get created?"""
        with self.assertRaises(IntegrityError):

            cow = User.query.filter(User.username == 'cowabunga').first()
            fail_message = Message(user_id=cow.id)
            db.session.add(fail_message)
            db.session.commit()

            self.assertEqual(Message.query.count(), 0)
