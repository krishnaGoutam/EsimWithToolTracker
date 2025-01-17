import json
import os

preferences_file = os.path.expanduser("~/.esim/preferences.json")

try:
    with open(preferences_file, "r") as file:
        preferences = json.load(file)
        print(json.dumps(preferences, indent=4))  # Pretty-print JSON
except FileNotFoundError:
    print("Preferences file not found.")
except json.JSONDecodeError:
    print("Error decoding the JSON file.")
