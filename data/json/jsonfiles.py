import os
import json


def load_json(file_name: str) -> dict:
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Build an absolute path to the JSON file
    json_path = os.path.join(dir_path, file_name)

    with open(json_path, 'r') as file:
        data = json.load(file)

    return data


countries: dict = load_json("countries.json")
customers: dict = load_json("customers.json")
companies: dict = load_json("companies.json")
