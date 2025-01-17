import psutil
import time
from datetime import datetime
import sqlite3
import os
import subprocess

def store_log_in_database(user, log_file_path):
    """
    Reads the log file and stores its content in the database.

    Args:
        user (str): The username associated with the log.
        log_file_path (str): The path to the log file.
    """
    if not os.path.exists(log_file_path):
        print(f"Log file not found: {log_file_path}")
        return

    # Read the log file content
    with open(log_file_path, 'r') as file:
        log_content = file.read()

    # Store the log content in the database
    conn = sqlite3.connect('esim_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (user, timestamp, log_content)
        VALUES (?, ?, ?)
    ''', (user, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), log_content))
    conn.commit()
    conn.close()
    print(f"Log data stored in the database for user: {user}")


def run_esim_and_capture_logs(esim_path, log_dir, user):
        """
        Runs eSim, captures its output and errors, and saves them to a log file.

        Args:
            esim_path (str): The full path to the eSim executable.
            log_dir (str): The directory where logs will be stored.
            user (str): The username to associate with the log file.
        """
        # Ensure the log directory exists
        if not os.path.exists(log_dir):
            print(f"Creating log directory: {log_dir}")
            os.makedirs(log_dir)

        # Create a log file with a timestamp
        log_file_path = os.path.join(log_dir, f"{user}_esim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        print(f"Log file path: {log_file_path}")

        try:
            # Run eSim and redirect stdout and stderr to the log file
            with open(log_file_path, 'w') as log_file:
                print(f"Running eSim: {esim_path}")
                process = subprocess.Popen(
                    esim_path,
                    stdout=log_file,
                    stderr=log_file,
                    shell=True
                )
                process.wait()  # Wait for the process to complete

            print(f"Log file created: {log_file_path}")
            return log_file_path

        except Exception as e:
            print(f"Error running eSim: {e}")
            return None

def is_esim_running():
    """Check if eSim is currently running."""
    for process in psutil.process_iter(['name']):
        if 'esim' in process.info['name'].lower():
            return True
    return False

def log_session(user, start_time, end_time):
    """Log session details to the database."""
    duration = (end_time - start_time).total_seconds() / 3600  # Convert to hours
    conn = sqlite3.connect('esim_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (user, start_time, end_time, duration)
        VALUES (?, ?, ?, ?)
    ''', (user, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), duration))
    conn.commit()
    conn.close()

def backup_logs(user, log_file_path="path/to/esim_log.txt"):
    """Backup log file content to the database."""
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as file:
            log_content = file.read()
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (user, timestamp, log_content)
            VALUES (?, ?, ?)
        ''', (user, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), log_content))
        conn.commit()
        conn.close()
        print("Log data saved to the database.")
    else:
        print("Log file not found.")
#running = True
# Main activity monitoring loop

def track_activity(user, log_file_path="logs/esim_default.log"):
    start_time = None
    print(f"Tracking started for user: {user}")

    try:
        while True:
            if is_esim_running():
                if start_time is None:
                    start_time = datetime.now()
                    print(f"Session started at {start_time}")
            else:
                if start_time:
                    end_time = datetime.now()
                    log_session(user, start_time, end_time)
                    store_log_in_database(user, log_file_path)
                    print(f"Session ended at {end_time}")
                    print(f"Duration: {(end_time - start_time)}")
                    start_time = None
            time.sleep(10)  # Check every 10 seconds
    except KeyboardInterrupt:
        print("Tracking stopped.")


# Run tracker
if __name__ == "__main__":
    user = input("Enter your username: ")
    consent = input("Do you consent to activity tracking? (yes/no): ")
    if consent.lower() == 'yes':
        track_activity(user)
    else:
        print("Tracking aborted. Consent not given.")