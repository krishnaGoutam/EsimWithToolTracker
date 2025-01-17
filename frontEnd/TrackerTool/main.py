from PyQt5.QtWidgets import (
    QApplication, QListWidget,QDialog,QWidget,QFileDialog, QVBoxLayout,QScrollArea,QHeaderView, QFrame,QAbstractItemView,QPushButton, QLabel, QComboBox,QMessageBox,QHBoxLayout, QFileDialog,QInputDialog,QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
import sys,platform,os
import threading
import subprocess
import csv
from tracker import track_activity, run_esim_and_capture_logs
import sqlite3
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime

class TrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("eSim Tool Tracker")
        self.setGeometry(100, 100, 500, 400)

        # Layout
        layout = QVBoxLayout()

        # Start Tracker Button
        self.start_button = QPushButton("Start Tracker")
        self.start_button.clicked.connect(self.start_tracker)
        layout.addWidget(self.start_button)

        # Stop Tracker Button (Initially Disabled)
        self.stop_button = QPushButton("Stop Tracker")
        self.stop_button.clicked.connect(self.stop_tracker)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        # View Statistics Button
        self.view_stats_button = QPushButton("View Statistics")
        self.view_stats_button.clicked.connect(self.view_statistics)
        layout.addWidget(self.view_stats_button)

        # View User Activity Button
        self.view_user_activity_button = QPushButton("View User Activity")
        self.view_user_activity_button.clicked.connect(self.view_user_activity)
        layout.addWidget(self.view_user_activity_button)

        # View Logs Button
        self.view_logs_button = QPushButton("View Logs")
        self.view_logs_button.clicked.connect(self.view_logs)
        layout.addWidget(self.view_logs_button)

        # Quit Button
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.quit_app)
        layout.addWidget(self.quit_button)

        # Status Label
        self.status_label = QLabel("Tracker is not running", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def start_tracker(self):
        # Get the user input for username
        user, ok = QInputDialog.getText(self, "Input", "Enter your username:")
        if ok and user:
            consent = QMessageBox.question(
                self, "Consent", "Do you consent to log tracking?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if consent == QMessageBox.Yes:
                # Cross-platform support
                system_platform = platform.system()

                if system_platform == "Linux":
                    log_dir = f"/home/{os.getlogin()}/Desktop/eSimToolTracker/logs/{user}"
                elif system_platform == "Windows":
                    log_dir = f"C:\\Users\\{user}\\Documents\\eSimToolTracker\\logs"
                else:
                    QMessageBox.critical(self, "Error", "Unsupported operating system.")
                    return

                # # Create the log directory if it doesn't exist
                # if not os.path.exists(log_dir):
                #     os.makedirs(log_dir)
                #     QMessageBox.information(self, "Directory Created", f"Log directory created at: {log_dir}")
                # Create a specific log file for the user
                user_log_dir = os.path.join(log_dir, user)
                if not os.path.exists(user_log_dir):
                    os.makedirs(user_log_dir)  # Create the user directory if it doesn't exist
                
                log_dir = os.path.join(user_log_dir, f"{user}_log.txt")  # Log file for the user
                # Inform the user that the log directory is ready
                self.status_label.setText(f"Tracking is ready for user: {user}")
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                # Set the stop flag to False
                self.stop_tracking_flag = False
                # Now wait for eSim to be manually run by the user
                QMessageBox.information(self, "eSim Tracking", "Please run eSim manually. The tool will start tracking once eSim is running.")
                
                # Start tracking user activity in a separate thread
                self.track_thread = threading.Thread(target=self.start_tracking_thread, args=(user, log_dir))
                self.track_thread.daemon = True
                self.track_thread.start()

            else:
                QMessageBox.information(self, "Consent Denied", "Tracking aborted.")

    
    def start_tracking_thread(self, user, log_file_path):
        # Simulate tracking with a loop that checks the stop flag
        while not self.stop_tracking_flag:
            track_activity(user, log_file_path)
        # After tracking ends, update the status label
        self.status_label.setText("Tracker is not running")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    # def start_tracking_thread(self, user, log_file_path):
    # # Simulate tracking with a loop that checks the stop flag
    #     while not self.stop_tracking_flag:
    #         # Start tracking activity for the user
    #         self.track_activity(user, log_file_path)
            
    #         # Optionally, you can add a small delay to prevent the loop from consuming too much CPU
    #         time.sleep(1)  # Adjust the sleep time based on how often you want to track activity

        # After tracking ends, update the status label
        self.status_label.setText("Tracker is not running")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def is_esim_running(self):
        # Check if eSim is running
        try:
            process = subprocess.Popen(["pgrep", "esim"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if stdout:
                return True  # eSim is running
            else:
                return False  # eSim is not running
        except Exception as e:
            print(f"Error checking eSim process: {e}")
            return False

    def capture_logs(self, log_file_path):
        # Capture the logs (you may need to adjust how you capture logs based on your setup)
        try:
            esim_path = "/usr/bin/esim"  # Adjust path for Ubuntu or Windows
            with open(log_file_path, "w") as log_file:
                process = subprocess.Popen([esim_path], stdout=log_file, stderr=log_file)
                process.communicate()
            QMessageBox.information(self, "Tracking Started", f"Tracking started. Logs are being saved to {log_file_path}")
        except Exception as e:
            print(f"Error capturing logs: {e}")

    # def stop_tracker(self):
    #     # Check if tracking thread is running
    #     if hasattr(self, 'track_thread') and self.track_thread.is_alive():
    #         # Terminate the tracking thread gracefully
    #         self.stop_tracking_flag = True  # Use a flag to signal the thread to stop

    #         # Wait for the thread to finish
    #         self.track_thread.join(timeout=2)

    #     # Terminate the eSim subprocess if running
    #     if hasattr(self, 'esim_process') and self.esim_process.poll() is None:
    #         self.esim_process.terminate()  # Send a termination signal
    #         try:
    #             self.esim_process.wait(timeout=2)
    #         except subprocess.TimeoutExpired:
    #             self.esim_process.kill()  # Force kill if it doesn't terminate in time

    #     # Update the status label
    #     self.status_label.setText("Tracking stopped.")

    #     # Disable the stop button and enable the start button
    #     self.stop_button.setEnabled(False)
    #     self.start_button.setEnabled(True)

    #     # Display an information message
    #     QMessageBox.information(self, "Tracker Stopped", "Activity tracking has been stopped.")

    def stop_tracker(self):
        # Check if tracking thread is running
        if hasattr(self, 'track_thread') and self.track_thread.is_alive():
            # Terminate the tracking thread gracefully
            self.stop_tracking_flag = True  # Use a flag to signal the thread to stop

            # Wait for the thread to finish
            self.track_thread.join(timeout=2)

        # Save session details to the database
        self.save_session_details()

        # Save log details to the database
        log_file_path = '/path/to/log/file.log'  # Update with the actual log file path
        self.store_log_in_database(self.current_user, log_file_path)

        # Terminate the eSim subprocess if running
        if hasattr(self, 'esim_process') and self.esim_process.poll() is None:
            self.esim_process.terminate()  # Send a termination signal
            try:
                self.esim_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.esim_process.kill()  # Force kill if it doesn't terminate in time

        # Update the status label
        self.status_label.setText("Tracking stopped.")

        # Disable the stop button and enable the start button
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

        # Display an information message
        QMessageBox.information(self, "Tracker Stopped", "Activity tracking has been stopped.")


    def store_log_in_database(self, user, log_file_path):
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


    def save_session_details(self):
        """Log session details to the database."""
        # Assuming `start_time` and `end_time` are stored as datetime objects
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds() / 3600  # Convert to hours

        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (user, start_time, end_time, duration)
            VALUES (?, ?, ?, ?)
        ''', (self.current_user, self.start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S'), duration))
        conn.commit()
        conn.close()
        print(f"Session data stored in the database for user: {self.current_user}")


    def view_statistics(self):
        # Create the Statistics window
        stats_window = QDialog(self)
        stats_window.setWindowTitle("Statistics")
        stats_window.setGeometry(100, 100, 700, 500)
        
        layout = QVBoxLayout(stats_window)

        # User filter dropdown
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT user FROM sessions")
        users = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.selected_user = "All Users"

        # User dropdown setup
        user_dropdown = QComboBox()
        user_dropdown.addItems(["All Users"] + users)
        user_dropdown.setCurrentText("All Users")
        user_dropdown.currentTextChanged.connect(lambda user: self.display_summary(stats_window, user))

        layout.addWidget(user_dropdown)

        # Export Data Button
        export_button = QPushButton("Export Data")
        export_button.clicked.connect(lambda: self.export_data(user_dropdown.currentText()))
        layout.addWidget(export_button)

        # Delete Data Button
        delete_button = QPushButton("Delete Data")
        delete_button.clicked.connect(lambda: self.delete_data(user_dropdown.currentText(), stats_window))
        layout.addWidget(delete_button)

        # Add a placeholder for the summary and table layout
        self.summary_container = QVBoxLayout()
        layout.addLayout(self.summary_container)

        stats_window.setLayout(layout)

        # Display the summary metrics for the first load
        self.display_summary(stats_window, "All Users")
        stats_window.exec_()


    def export_data(self, user_filter):
        """Exports session data to a CSV file."""
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()

        if user_filter == "All Users":
            cursor.execute("SELECT user, start_time, end_time, duration FROM sessions")
        else:
            cursor.execute("SELECT user, start_time, end_time, duration FROM sessions WHERE user = ?", (user_filter,))
        
        records = cursor.fetchall()
        conn.close()

        # Ask user for file location and name using QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save File", 
            "", 
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["User", "Start Time", "End Time", "Duration"])
                for record in records:
                    writer.writerow(record)

            QMessageBox.information(self, "Export Successful", "Data exported successfully!")
    
    def delete_data(self, user_filter,event=None):
        """Deletes a session by prompting the user to select a session based on available data."""
        # Fetch data from the database
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        if user_filter == "All Users":
            cursor.execute("SELECT user, start_time FROM sessions")
        else:
            cursor.execute("SELECT user, start_time FROM sessions WHERE user = ?", (user_filter,))
        
        records = cursor.fetchall()
        conn.close()

        if not records:
            QMessageBox.warning(self, "No Data", "No sessions available to delete.")
            return

        # Create a selection dialog to choose a session
        items = [f"{user} - {start_time}" for user, start_time in records]
        item, ok = QInputDialog.getItem(self, "Select Session", "Select a session to delete:", items, 0, False)

        if ok and item:
            user, start_time = item.split(" - ")
            # Confirm deletion
            confirmation = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the session for user '{user}' at '{start_time}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if confirmation == QMessageBox.Yes:
                # Delete from the database
                conn = sqlite3.connect('esim_tracker.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE user = ? AND start_time = ?", (user, start_time))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Deletion Successful", "Session deleted successfully.")
                # Refresh the summary view
                self.display_summary(self, user_filter)
    def clear_layout_recursive(self, layout):
        # Loop through all items in the layout
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()  # Remove the widget
            elif item.layout():
                self.clear_layout_recursive(item.layout())  # Recursively clear nested layouts

    def display_summary(self, stats_window, user_filter):
       #Clear The Existing Data in the Summary Layout
        self.clear_layout_recursive(self.summary_container)
        summary_layout = QVBoxLayout()
        # Fetch data based on user filter
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()

        if user_filter == "All Users":
            cursor.execute("SELECT COUNT(*), COUNT(DISTINCT user), SUM(duration), AVG(duration) FROM sessions")
        else:
            cursor.execute("SELECT COUNT(*), 1, SUM(duration), AVG(duration) FROM sessions WHERE user = ?", (user_filter,))

        total_sessions, total_users, total_hours, avg_duration = cursor.fetchone()
        #These are where I am having error. What I want is evertime a different user's stastics is selected , It displayes data related to that only.
        # Handle cases where there are no records
        total_sessions = total_sessions or 0
        total_users = total_users or 0
        total_hours = total_hours or 0.0
        avg_duration = avg_duration or 0.0

        # Display summary metrics
        metrics = [
            ("Total Hours Logged:", f"{total_hours:.2f} hours"),
            ("Average Duration per Session:", f"{avg_duration:.2f} hours"),
            ("Total Number of Sessions:", total_sessions),
            ("Total Active Users:", total_users)
        ]

        # Create a new layout for the summary
        #summary_layout = QVBoxLayout()

        for label_text, value_text in metrics:
            metric_layout = QHBoxLayout()
            label = QLabel(f"<b>{label_text}</b>")
            value = QLabel(str(value_text))
            metric_layout.addWidget(label)
            metric_layout.addWidget(value)
            summary_layout.addLayout(metric_layout)

        # Add the new summary layout to the summary container
        self.summary_container.addLayout(summary_layout)
        #layout.addLayout(self.summary_container)
        # Create the table for individual session details
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["User", "Start Time", "End Time", "Duration"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Make table cells non-editable

        # Fetch and insert data into the table
        if user_filter == "All Users":
            cursor.execute("SELECT user, start_time, end_time, duration FROM sessions")
        else:
            cursor.execute("SELECT user, start_time, end_time, duration FROM sessions WHERE user = ?", (user_filter,))

        records = cursor.fetchall()
        conn.close()

        table.setRowCount(len(records))
        for row_index, record in enumerate(records):
            table.setItem(row_index, 0, QTableWidgetItem(record[0]))
            table.setItem(row_index, 1, QTableWidgetItem(record[1]))
            table.setItem(row_index, 2, QTableWidgetItem(record[2]))
            table.setItem(row_index, 3, QTableWidgetItem(f"{record[3]:.2f} hrs"))

        # Add the table to the summary container
        self.summary_container.addWidget(table)

    def view_user_activity(self):
        # Create a new window for activity
        activity_window = QDialog(self)
        activity_window.setWindowTitle("User Activity")
        activity_window.setGeometry(100, 100, 1000, 600)  # Increased size for better visualization

        layout = QVBoxLayout(activity_window)

        # Dropdown for selecting chart type
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Bar Chart", "Pie Chart", "Line Chart"])
        self.chart_type.setCurrentText("Bar Chart")
        layout.addWidget(self.chart_type)

        # Button to generate chart
        generate_btn = QPushButton("Generate Chart")
        generate_btn.clicked.connect(lambda: self.generate_chart(activity_window))
        layout.addWidget(generate_btn)

        # Placeholder frame for the chart
        #self.chart_frame = QFrame(activity_window)
        #layout.addWidget(self.chart_frame)
        # Scrollable area for the chart
        self.scroll_area = QScrollArea(activity_window)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Placeholder widget inside the scrollable area
        self.chart_container = QWidget()
        self.scroll_area.setWidget(self.chart_container)

        # Layout for the chart container
        self.chart_layout = QVBoxLayout(self.chart_container)
        
        activity_window.setLayout(layout)
        activity_window.exec_()

    def generate_chart(self, activity_window):
        chart_type = self.chart_type.currentText()

        # Fetch data from the database
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT user, SUM(duration) FROM sessions GROUP BY user")
        records = cursor.fetchall()
        conn.close()

        users, durations = zip(*records) if records else ([], [])
        if not users:
            # Show an error message if no data
            QMessageBox.information(activity_window, "No Data", "No activity data to display.")
            return

        # Clear previous chart
        for i in reversed(range(self.chart_layout.count())):
            widget = self.chart_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Create a Matplotlib figure
        fig, ax = plt.subplots(figsize=(15, 6))  # Larger figure size

        # Generate the selected chart type
        if chart_type == "Bar Chart":
            ax.bar(users, durations, color='skyblue')
            ax.set_title('User Activity (Bar Chart)', fontsize=14)
            ax.set_xlabel('Users', fontsize=12)
            ax.set_ylabel('Duration (hours)', fontsize=12)
        elif chart_type == "Pie Chart":
            ax.pie(durations, labels=users, autopct='%1.1f%%', startangle=90)
            ax.set_title('User Activity (Pie Chart)', fontsize=14)
        elif chart_type == "Line Chart":
            ax.plot(users, durations, marker='o', color='blue')
            ax.set_title('User Activity (Line Chart)', fontsize=14)
            ax.set_xlabel('Users', fontsize=12)
            ax.set_ylabel('Duration (hours)', fontsize=12)

        # Embed the Matplotlib figure into the PyQt5 window
        canvas = FigureCanvas(fig)
        self.chart_layout.addWidget(canvas)

        # Draw the updated chart
        canvas.draw()

    def view_logs(self):
        # Create the logs window
        logs_window = QDialog(self)
        logs_window.setWindowTitle("View Logs")
        logs_window.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(logs_window)

        # Fetch logs from the database
        conn = sqlite3.connect('esim_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, user, timestamp, log_content FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()
        conn.close()

        if not logs:
            no_logs_label = QLabel("No logs available.", logs_window)
            no_logs_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(no_logs_label)
            logs_window.setLayout(layout)
            logs_window.exec_()
            return

        # List widget for displaying logs
        log_list_widget = QListWidget(logs_window)
        for log in logs:
            log_list_widget.addItem(f"ID: {log[0]}, User: {log[1]}, Timestamp: {log[2]}")

        layout.addWidget(log_list_widget)

        # Function to show selected log details
        def show_selected_log():
            selected_item = log_list_widget.currentItem()
            if selected_item:
                # Get the index of the selected log and retrieve its details
                selected_index = log_list_widget.row(selected_item)
                log = logs[selected_index]
                log_details = f"User: {log[1]}\nTimestamp: {log[2]}\n\nLog Content:\n{log[3]}"
                
                # Show the log details in a message box
                QMessageBox.information(logs_window, "Log Details", log_details)

        # View button to show the selected log's details
        view_btn = QPushButton("View Selected Log", logs_window)
        view_btn.clicked.connect(show_selected_log)

        layout.addWidget(view_btn)

        logs_window.setLayout(layout)
        logs_window.exec_()

    def quit_app(self):
        self.root.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrackerApp()
    window.show()
    sys.exit(app.exec_())