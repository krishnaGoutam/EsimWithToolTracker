import sqlite3
import random
from datetime import datetime, timedelta

# Path to your SQLite database
db_path = 'esim_tracker.db'

# Function to generate random datetime within a range
def random_datetime(start, end):
    delta = end - start
    random_seconds = random.randint(0, delta.total_seconds())
    return start + timedelta(seconds=random_seconds)

# Function to generate dummy data for sessions
def generate_sessions_data(conn, num_records=10):
    cursor = conn.cursor()
    users = ['user1', 'user2', 'user3', 'user4', 'user5']
    
    now = datetime.now()
    past = now - timedelta(days=30)  # Generate data from the last 30 days
    
    for _ in range(num_records):
        user = random.choice(users)
        start_time = random_datetime(past, now)
        end_time = start_time + timedelta(minutes=random.randint(10, 120))  # Random duration 10-120 mins
        duration = (end_time - start_time).total_seconds() / 3600  # Duration in hours
        
        cursor.execute('''
        INSERT INTO sessions (user, start_time, end_time, duration)
        VALUES (?, ?, ?, ?)
        ''', (user, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), duration))
    
    conn.commit()
    print(f"{num_records} dummy records added to the 'sessions' table.")

# Function to generate dummy data for logs
def generate_logs_data(conn, num_records=20):
    cursor = conn.cursor()
    users = ['user1', 'user2', 'user3', 'user4', 'user5']
    
    now = datetime.now()
    past = now - timedelta(days=30)  # Generate data from the last 30 days
    
    for _ in range(num_records):
        user = random.choice(users)
        timestamp = random_datetime(past, now)
        log_content = f"Log entry for {user} at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        
        cursor.execute('''
        INSERT INTO logs (user, timestamp, log_content)
        VALUES (?, ?, ?)
        ''', (user, timestamp.strftime('%Y-%m-%d %H:%M:%S'), log_content))
    
    conn.commit()
    print(f"{num_records} dummy records added to the 'logs' table.")

# Main function to insert dummy data
def main():
    conn = sqlite3.connect(db_path)
    
    # Generate dummy data
    generate_sessions_data(conn, num_records=10)
    generate_logs_data(conn, num_records=20)
    
    conn.close()

if __name__ == "__main__":
    main()
