import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    """Loads data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Saves data to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'analytics.json')

def load_analytics():
    if not os.path.exists(ANALYTICS_FILE):
        return {
            "daily_visits": {},
            "page_views": {},
            "section_views": {},
            "interactions": {}
        }
    with open(ANALYTICS_FILE, 'r') as f:
        return json.load(f)

def save_analytics(data):
    with open(ANALYTICS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
