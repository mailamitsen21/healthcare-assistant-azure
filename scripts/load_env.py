"""
Helper to load environment variables from local.settings.json or Azure
"""
import os
import json

def load_local_settings(file_path: str = "../src/specialized-tools/local.settings.json"):
    """Load environment variables from local.settings.json"""
    try:
        with open(file_path, 'r') as f:
            settings = json.load(f)
            values = settings.get('Values', {})
            
            for key, value in values.items():
                if not os.getenv(key):  # Don't override existing env vars
                    os.environ[key] = value
            
            return True
    except Exception as e:
        print(f"Could not load local.settings.json: {e}")
        return False

if __name__ == "__main__":
    load_local_settings()

