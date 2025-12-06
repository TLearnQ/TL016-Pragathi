import json
import os

def split_by_key(input_file, key_name, output_dir):
    # Load JSON file
    with open(input_file, "r") as f:
        items = json.load(f)

    os.makedirs(output_dir, exist_ok=True)

    groups = {}


    for item in items:
        value = item.get(key_name, "unknown")
        groups.setdefault(value, []).append(item)


    for value, data in groups.items():
        path = os.path.join(output_dir, f"{value}.json")
        with open(path, "w") as f:
            json.dump(data, f, i
