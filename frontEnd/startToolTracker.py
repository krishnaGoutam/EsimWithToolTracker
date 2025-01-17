import sys
import os
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore
from datetime import datetime  # Ensure other necessary imports are here
from Application import Application  # Import your Application class

# Function to start the Tool Tracker
def start_tool_tracker():
    """Start the Tool Tracker application."""
    try:
        tracker_process = subprocess.Popen(
            ['python3', 'src/frontEnd/TrackerTool/main.py'],  # Replace with the actual path
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Tool Tracker started successfully.")
        return tracker_process
    except Exception as e:
        print("Error starting Tool Tracker:", e)
        return None

# Main function for eSim
def main(args):
    """
    The splash screen and application initialization for eSim.
    """
    # Step 1: Start the Tool Tracker
    tracker_process = start_tool_tracker()
    if not tracker_process:
        print("Failed to start Tool Tracker. Exiting.")
        return

    # Wait for Tool Tracker to initialize (Optional)
    try:
        tracker_process.wait(timeout=15)  # Adjust timeout if necessary
    except subprocess.TimeoutExpired:
        print("Tool Tracker is running, proceeding to start eSim...")

    # Step 2: Start eSim
    print("Starting eSim......")
    app = QtWidgets.QApplication(args)
    app.setApplicationName("eSim")

    appView = Application()
    appView.hide()
    splash_pix = QtGui.QPixmap(os.path.join('images', 'splash_screen_esim.png'))
    splash = QtWidgets.QSplashScreen(
        appView, splash_pix, QtCore.Qt.WindowStaysOnTopHint
    )
    splash.setMask(splash_pix.mask())
    splash.setDisabled(True)
    splash.show()

    appView.splash = splash
    appView.obj_workspace.returnWhetherClickedOrNot(appView)

    try:
        if os.name == 'nt':
            user_home = os.path.join('library', 'config')
        else:
            user_home = os.path.expanduser('~')

        file = open(os.path.join(user_home, ".esim/workspace.txt"), 'r')
        work = int(file.read(1))
        file.close()
    except IOError:
        work = 0

    if work != 0:
        appView.obj_workspace.defaultWorkspace()
    else:
        appView.obj_workspace.show()

    # Step 3: Close Tool Tracker process if necessary (Optional)
    if tracker_process.poll() is None:
        tracker_process.terminate()
        tracker_process.wait()

    sys.exit(app.exec_())

# Call main function
if __name__ == '__main__':
    # Run the eSim application
    try:
        main(sys.argv)
    except Exception as err:
        print("Error:", err)
