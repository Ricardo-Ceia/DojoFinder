import unittest
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

if __name__ == '__main__':
    unittest.main()