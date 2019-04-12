import json
import logging
import parsing

root = "/mnt/data/oasis-3/"


class Subject:
    def __init__(self, subject_id, experiments=[]):
        self.subject_id = subject_id
        self.experiments = experiments
        self.gds_data = [GDSData.load(gds_path) for gds_path in self.get_gds_paths()]

    def build_path(self, filename):
        return root + self.subject_id + "/" + filename

    def get_mri_paths(self):
        return [
            self.build_path(experiment)
            for experiment in self.experiments
            if "_MR_" in experiment
        ]

    def get_gds_paths(self):
        return [
            self.build_path(experiment + '.json')
            for experiment in self.experiments
            if "_USDb6" in experiment
        ]

    @classmethod
    def load(cls, subject_id):
        path = root + subject_id + "/"
        experiments = parsing.parse_experiments(path + "experiments.json")
        return cls(subject_id, experiments)


def load_subjects():
    logging.info("Loading subjects...")
    with open(root + "subjects") as f:
        patients = [Subject.load(line.strip()) for line in f]

    logging.info("Found {} subjects".format(len(patients)))
    return patients


class GDSData:
    def __init__(self, gds, day, age):
        self.gds = gds
        self.day = day
        self.age = age

    @classmethod
    def load(cls, path):
        try:
            with open(path) as f:
                data = json.load(f)["items"][0]["data_fields"]
                return cls(int(data['GDS']), int(data["visit"]), float(data["age"]))
        except:
            logging.warning('Could not read GDS file {}'.format(path))
            return None
