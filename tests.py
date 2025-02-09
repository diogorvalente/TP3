"""
Tests the application API
"""

import base64
import unittest

from app import app, db, recreate_db


def auth_header(username, password):
    """Returns the authorization header."""
    credentials = f'{username}:{password}'
    b64credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    return {'Authorization': f'Basic {b64credentials}'}


class TestBase(unittest.TestCase):
    """Base for all tests."""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
        self.client = app.test_client()
        with app.app_context():
            recreate_db()

    def tearDown(self):
        pass


class TestUsers(TestBase):
    """Tests for the user endpoints."""

    def setUp(self):
        super().setUp()

    def test_correct_credentials(self):
        """Tests the user with correct credentials."""
        # First, create a user
        user_data = {
            'name': 'Homer Simpson',
            'email': 'homer@example.com',
            'username': 'homer',
            'password': '1234'
        }
        self.client.post('/api/user/register/', json=user_data)

        # Now, test with correct credentials
        credentials = auth_header('homer', '1234')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 200)

    def test_wrong_credentials(self):
        """Tests the user with incorrect credentials."""
        credentials = auth_header('no-user', 'no-password')
        res = self.client.get('/api/user/', headers=credentials)
        self.assertEqual(res.status_code, 403)


class TestProjects(TestBase):
    """Tests for the project endpoints."""

    def setUp(self):
        super().setUp()


class TestTasks(TestBase):
    """Tests for the tasks endpoints."""

    def setUp(self):
        super().setUp()


if __name__ == '__main__':
    unittest.main()
