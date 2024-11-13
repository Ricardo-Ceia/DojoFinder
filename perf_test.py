import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_dojos_performance(client, benchmark):
    benchmark(client.post, '/get_dojos', data={'location': 'New York'})

def test_dojo_details_performance(client, benchmark):
    benchmark(client.get, '/dojo_details?dojo_id=1')

def test_premium_dojo_form_performance(client, benchmark):
    benchmark(client.get, '/premium_dojo_form')