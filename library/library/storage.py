import json
import os

DATA_FILE = os.path.join("data", "library.json")

def initialize_storage():
    """Ensure the data directory and library.json file exist."""
    if not os.path.exists("data"):
        os.makedirs("data")
        
    if not os.path.exists(DATA_FILE):
        default_data = {
            "books": [],
            "members": [],
            "transactions": []
        }
        _save(default_data)

def _save(data):
    """Write data to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def _load():
    """Read data from the JSON file."""
    if not os.path.exists(DATA_FILE):
        initialize_storage()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_data(key: str) -> list:
    """Retrieve a specific section of data (books, members, transactions)."""
    data = _load()
    return data.get(key, [])

def save_data(key: str, updated_list: list):
    """Update a specific section of data."""
    data = _load()
    data[key] = updated_list
    _save(data)
