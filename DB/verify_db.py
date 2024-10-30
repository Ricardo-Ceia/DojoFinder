import sqlite3
import os

def delete_db(confirm=False):
    if confirm:
        os.remove('dojo_listings.db')
        print("database deleted!")

def inspect_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("\n---------DATABASE---------")   

    for table in tables:
        table_name = table[0]
        print(f"\nTable {table_name}")

        cursor.execute(f"PRAGMA table_info({table_name});")
        collums = cursor.fetchall()

        print("collums:")

        for collum in collums:
            print(f" {collum[1]}  ({collum[2]})") 

    conn.close()
 

def check_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('dojo_listings.db')
    cursor = conn.cursor()

    '''cursor.execute('SELECT * FROM dojos;')
    # Fetch all results
    rows = cursor.fetchall()

    # Print the results
    for row in rows:
        print(row)
'''
    cursor.execute('SELECT * FROM schedules;')
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

def delete_by_id(id):
    # Connect to the SQLite database
    conn = sqlite3.connect('dojo_listings.db')
    cursor = conn.cursor()

    # Execute a DELETE query
    cursor.execute('DELETE FROM dojos WHERE id = ?;', (id,))

    # Commit the changes
    conn.commit()

    # Close the connection
    conn.close()


def update_premium_listing(id, column_name, new_value):
    """
    Update a specific column for a premium listing
    
    Args:
        id (int): The ID of the listing to update
        column_name (str): The name of the column to update
        new_value: The new value to set
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('dojo_listings.db')
        cursor = conn.cursor()

        # Create the SQL query using string formatting for the column name
        # The column name is included in the SQL string directly since it can't be parameterized
        # The value still uses parameter binding for security
        query = f'UPDATE premium_listings SET {column_name} = ? WHERE id = ?'
        
        # Execute the update query
        cursor.execute(query, (new_value, id))
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully updated {column_name} for listing ID {id}")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Close the connection
        conn.close()


def clear_all_data(confirm=False):
    """
    Delete all data from all tables while preserving the database structure.
    
    Args:
        confirm (bool): Safety parameter that must be True to execute the deletion
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not confirm:
        print("Warning: This will delete ALL data from ALL tables.")
        print("Set confirm=True to proceed with deletion.")
        return False
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('dojo_listings.db')
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION;")
        
        # Delete data from each table
        for table in tables:
            table_name = table[0]
            if table_name != 'sqlite_sequence':  # Skip SQLite internal tables
                cursor.execute(f"DELETE FROM {table_name};")
                print(f"Cleared all data from {table_name}")
        
        # Reset auto-increment counters if they exist
        cursor.execute("DELETE FROM sqlite_sequence;")
        
        # Commit the transaction
        conn.commit()
        print("Successfully cleared all data while preserving database structure")
        return True
        
    except sqlite3.Error as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
        return False
        
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    check_data()
    #clear_all_data(confirm=True)
    #delete_by_id(1)
    #inspect_database('dojo_listings.db')
    #delete_db(confirm=True)    