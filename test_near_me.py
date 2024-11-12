import unittest
from unittest.mock import patch, MagicMock
import time
import random
from geopy.distance import geodesic
import sqlite3
import json
from flask import Flask
from app import app  # Replace with your actual app module

class StressTestGetNearMe(unittest.TestCase):
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
            self.mock_dojos.append((i + 1, lat, lon))
        
        self.conn.commit()

    def tearDown(self):
        self.conn.close()

    def test_single_request_performance(self):
        """Test performance of a single request with different user locations"""
        print("\nTesting single request performance...")
        
        test_locations = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437), # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
            (39.9526, -75.1652)   # Philadelphia
        ]
        
        for lat, lon in test_locations:
            start_time = time.time()
            
            with patch('sqlite3.connect') as mock_connect:
                # Mock the database to return our test data
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                mock_cursor.fetchall.return_value = self.mock_dojos
                
                response = self.client.post('/get_near_me', data={
                    'latitude': str(lat),
                    'longitude': str(lon)
                })
            
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            print(f"\nLocation: ({lat}, {lon})")
            print(f"Processing time: {processing_time:.2f}ms")

    def test_bulk_performance(self):
        """Test performance with multiple requests"""
        print("\nTesting bulk performance...")
        
        num_requests = 100
        response_times = []
        
        with patch('sqlite3.connect') as mock_connect:
            # Mock the database to return our test data
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = self.mock_dojos
            
            for i in range(num_requests):
                # Generate random user location
                user_lat = random.uniform(24.396308, 49.384358)
                user_lon = random.uniform(-125.000000, -66.934570)
                
                start_time = time.time()
                
                response = self.client.post('/get_near_me', data={
                    'latitude': str(user_lat),
                    'longitude': str(user_lon)
                })
                
                end_time = time.time()
                response_times.append((end_time - start_time) * 1000)
                
                if (i + 1) % 10 == 0:
                    print(f"Completed {i + 1}/{num_requests} requests")
        
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print("\nPerformance Statistics:")
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Maximum response time: {max_time:.2f}ms")
        print(f"Minimum response time: {min_time:.2f}ms")
        
        # Performance assertions
        self.assertLess(avg_time, 1000, "Average response time exceeds 1 second")
        self.assertLess(max_time, 2000, "Maximum response time exceeds 2 seconds")

    def test_distance_calculation_accuracy(self):
        """Test the accuracy of the distance calculations"""
        print("\nTesting distance calculation accuracy...")
        
        # Test cases with known distances
        test_cases = [
            {
                'user': (40.7128, -74.0060),  # New York
                'dojo': (40.7589, -73.9851),  # Nearby location (~2.5 miles)
                'should_find': True
            },
            {
                'user': (34.0522, -118.2437),  # Los Angeles
                'dojo': (34.0522, -115.2437),  # Far location (~150 miles)
                'should_find': False
            }
        ]
        
        for test_case in test_cases:
            distance = geodesic(
                (test_case['user'][0], test_case['user'][1]),
                (test_case['dojo'][0], test_case['dojo'][1])
            ).miles
            
            within_range = distance < 10
            self.assertEqual(within_range, test_case['should_find'])
            
            print(f"Distance test: {distance:.2f} miles, Expected found: {test_case['should_find']}")

if __name__ == '__main__':
    unittest.main(verbosity=2)