import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('esim_tracker.db')
cursor = conn.cursor()

# Create sessions table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration REAL
)
''')

# Create logs table to store log file data
cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    log_content TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete. Tables 'sessions' and 'logs' created successfully.")