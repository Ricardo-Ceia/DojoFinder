import unittest
from unittest.mock import patch
import sqlite3
from app import app

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

    def test_signup_200(self):
        response = self.app.post('/signup', data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': 'secure_password'
        })
        self.assertEqual(response.status_code, 200)

    def test_signup_400(self):
        response = self.app.post('/signup', data = {
            'username': 'test_user',
            'email': 'test_user@example.com',
            'password': 'secure_password',
            'confirm_password': 'secure_password2'
        })
        self.assertEqual(response.status_code, 400)

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