import sqlite3

# Function to create the database and tables
def create_database():
    # Connect to SQLite database (this will create the database file if it doesn't exist)
    conn = sqlite3.connect('dojo_listings.db')
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()


    # Create the premium_listings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dojos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
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
        longitude REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dojo_id INTEGER NOT NULL,
            day_of_week TEXT NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            instructor TEXT,
            competition_only BOOLEAN,
            age_range TEXT,
            FOREIGN KEY (dojo_id) REFERENCES dojos(id) ON DELETE CASCADE
        );
        ''')
    cursor.execute('''CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    print("Database and tables created successfully.")

# Main function
if __name__ == "__main__":
    create_database()