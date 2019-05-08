import collections
import csv
import json
import data


def parse_experiments(filename):
    with open(filename) as f:
        data = json.load(f)
        return [d["label"] for d in data["ResultSet"]["Result"]]

def parse_cdr_ratings(filename):
    cdr_mapping = collections.defaultdict(list)
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            subject_id = row['Subject']
            day = int(row['Label'][-4:])
            cdr = float(row['cdr'])
            cdr_mapping[subject_id].append(data.CDRData(day, cdr))
    return cdr_mapping
