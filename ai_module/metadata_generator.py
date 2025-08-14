import json
from datetime import datetime

def generate_metadata(title, description, author, tags):
    metadata = {
        "name": title,
        "description": description,
        "author": author,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    return json.dumps(metadata, indent=2)