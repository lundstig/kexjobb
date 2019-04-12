import json


def parse_experiments(filename):
    with open(filename) as f:
        data = json.load(f)
        return [d["label"] for d in data["ResultSet"]["Result"]]

