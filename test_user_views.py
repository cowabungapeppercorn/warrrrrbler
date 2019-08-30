"""User View tests."""

import os
from unittest import TestCase
from psycopg2 import IntegrityError
from models import db, connect_db, Message, User

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for Users"""
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
        db.session.rollback()

    def test_visit_other_user_pages_logged_in(self):
        """Can user vist other users' follower and following pages?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}/followers')
            resp2 = c.get(f'/users/{self.testuser.id}/following')
            html = resp.get_data(as_text=True)
            html2 = resp2.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.testuser.username}', html)
            self.assertEqual(resp2.status_code, 200)
            self.assertIn(f'{self.testuser.username}', html2)

    def test_visit_user_page_not_logged_in(self):
        """Can non-logged in user visit other user's follower and following pages?"""
        with self.client as c:

            resp = c.get(f'/users/{self.testuser.id}/followers',
                         follow_redirects=True)
            resp2 = c.get(f'/users/{self.testuser.id}/following',
                          follow_redirects=True)
            html = resp.get_data(as_text=True)
            html2 = resp2.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp2.status_code, 200)
            self.assertIn('<h4>New to Warbler?</h4>', html)
            self.assertIn('<h4>New to Warbler?</h4>', html2)
