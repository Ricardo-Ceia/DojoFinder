import unittest
from unittest.mock import patch
import sqlite3
from app import app
import time

class TestDojosApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_get_dojos_404(self):
        response = self.app.post('/get_dojos', data={'location': 'New York'})
        self.assertEqual(response.status_code, 404)
    
    def test_get_dojos_200(self):
        response = self.app.post('/get_dojos', data={'location': 'Lisboa'})
        self.assertEqual(response.status_code, 200) 

    def test_dojo_details(self):
        response = self.app.get('/dojo_details?dojo_id=1')
        self.assertEqual(response.status_code, 200)

    def test_premium_dojo_form(self):
        response = self.app.get('/premium_dojo_form')
        self.assertEqual(response.status_code, 200)

    def test_signup_302(self):
       # Generate unique username and email for the test
        unique_username = f"user_{int(time.time())}"
        unique_email = f"user{int(time.time())}@example.com"

        response = self.app.post('/signup', data={
            'username': unique_username,
            'email': unique_email,
            'password': 'secure_password',
            'confirm_password': 'secure_password'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(response.headers['Location'],'/premium_dojo_form')


    def test_signup_400_email_or_username_already_exists(self):
        response = self.app.post('/signup', data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': 'secure_password'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'email or username already exists!',response.data)

    def test_signup_400_password_different_confirm_password(self):
        response = self.app.post('/signup', data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': 'secure_password2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'password and confirm password do not match!',response.data)

    def test_signup_400_missing_username(self):
        response = self.app.post('/signup', data = {
            'username': '',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': 'secure_password2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'username, email, password and confirm password are required!',response.data)

    def test_signup_400_missing_password(self):
        response = self.app.post('/signup', data = {
            'username': '',
            'email': 'test_user@example.com',
            'password': '',
            'confirm_password': 'secure_password2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'username, email, password and confirm password are required!',response.data)

    def test_signup_400_missing_email(self):
        response = self.app.post('/signup', data = {
            'username': '',
            'email': '',
            'password': 'secure_password',
            'confirm_password': 'secure_password2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'username, email, password and confirm password are required!',response.data)

    def test_signup_400_missing_confirm_password(self):
        response = self.app.post('/signup', data = {
            'username': '',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': ''
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'username, email, password and confirm password are required!',response.data)

    def test_signup_500(self):
    # Simulate a database error by mocking the `sqlite3.connect` method
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database connection failed")

            response = self.app.post('/signup', data={
                'username': 'test_user',
                'email': 'test_user@example.com',
                'password': 'secure_password',
                'confirm_password': 'secure_password'
            })
            self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main()