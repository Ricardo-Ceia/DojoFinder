import unittest
from unittest.mock import patch, MagicMock
import time
import random
import sqlite3
import threading
from flask import Flask
from app import app, get_dojos_by_city  # Replace with your actual app and function

class StressTestGetDojos(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        
        # Create test database in memory
        self.conn = sqlite3.connect(':memory:')
        self.cursor = self.conn.cursor()
        
        # Create dojos table matching your schema
        self.cursor.execute('''
            CREATE TABLE dojos (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                city TEXT,
                website TEXT,
                phone TEXT,
                email TEXT,
                sensei_path TEXT,
                athletes_path TEXT,
                image_path TEXT,
                price_per_month TEXT,
                head_instructor TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        
        # Generate 1000 random dojos across the USA
        self.mock_dojos = []
        for i in range(1000):
            lat = random.uniform(24.396308, 49.384358)
            lon = random.uniform(-125.000000, -66.934570)
            self.cursor.execute('''
                INSERT INTO dojos (
                    name, address, city, website, phone, email,
                    sensei_path, athletes_path, image_path,
                    price_per_month, head_instructor, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f'Test Dojo {i}',
                f'Address {i}',
                'Test City',
                'http://test.com',
                '123-456-7890',
                'test@test.com',
                None,
                None,
                None,
                '100',
                'Sensei Test',
                lat,
                lon
            ))
            self.mock_dojos.append((i + 1, 'Test Dojo', 'Test City'))
        
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_concurrent_requests(self):
        """Test performance with multiple concurrent requests"""
        print("\nTesting concurrent requests...")
        
        num_clients = 10
        num_requests_per_client = 100
        self.response_times = []
        
        with patch('sqlite3.connect') as mock_connect:
            # Mock the database to return our test data
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = self.mock_dojos
            
            threads = []
            for _ in range(num_clients):
                t = threading.Thread(target=self.run_client_requests, args=(num_requests_per_client,))
                t.start()
                threads.append(t)
            
            for thread in threads:
                thread.join()
        
        # Calculate statistics
        avg_time = sum(self.response_times) / len(self.response_times)
        max_time = max(self.response_times)
        min_time = min(self.response_times)
        
        print("\nPerformance Statistics:")
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Maximum response time: {max_time:.2f}ms")
        print(f"Minimum response time: {min_time:.2f}ms")
        
        # Performance assertions
        self.assertLess(avg_time, 1000, "Average response time exceeds 1 second")
        self.assertLess(max_time, 2000, "Maximum response time exceeds 2 seconds")

    def run_client_requests(self, num_requests):
        for i in range(num_requests):
            # Generate random city
            city = random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Philadelphia"])
            
            start_time = time.time()
            
            response = self.client.post('/get_dojos', data={
                'location': city
            })
            
            end_time = time.time()
            self.response_times.append((end_time - start_time) * 1000)
            
            if (i + 1) % 10 == 0:
                print(f"Client {threading.get_ident()} completed {i + 1}/{num_requests} requests")

if __name__ == '__main__':
    unittest.main(verbosity=2)