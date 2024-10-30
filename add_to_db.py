import sqlite3
import csv

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('dojos.db')
cursor = conn.cursor()

# Create the dojos table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS dojos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    martial_art_style TEXT
)
''')

# Read the CSV file and insert data into the database
with open('spain_judo_clubs.csv', 'r', encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=';')
    next(csvreader)  # Skip the header row
    for row in csvreader:
        # Ensure we have all fields, even if some are empty
        row += [''] * (6 - len(row))
        cursor.execute('''
        INSERT INTO dojos (name, address, phone, email, website, martial_art_style)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', row)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Data has been successfully imported into the database.")