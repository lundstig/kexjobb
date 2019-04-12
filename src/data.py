import json
import logging
import os
import parsing
import sys
import traceback

root = "/mnt/data/oasis-3/"

missing_sessions = set()


class Subject:
    def __init__(self, subject_id, experiments=[]):
        self.subject_id = subject_id
        self.experiments = experiments
        self.gds_data = [GDSData.load(gds_path) for gds_path in self.get_gds_paths()]
        self.mri_data = [MRIData.load(mri_path) for mri_path in self.get_mri_paths()]

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
            self.build_path(experiment + ".json")
            for experiment in self.experiments
            if "_USDb6" in experiment
        ]

    def get_mri_gds_delays():
        return None

    @classmethod
    def load(cls, subject_id):
        path = root + subject_id + "/"
        experiments = parsing.parse_experiments(path + "experiments.json")
        return cls(subject_id, experiments)


def load_subjects():
    logging.info("Loading data...")
    with open(root + "subjects") as f:
        subjects = [Subject.load(line.strip()) for line in f]

    total_mri_sessions = sum(len(subject.get_mri_paths()) for subject in subjects)
    total_gds_evaluations = sum(len(subject.get_gds_paths()) for subject in subjects)
    logging.info(f"Found {len(subjects)} subjects")
    logging.info(f"Found {total_mri_sessions} MRI sessions")
    logging.info(f"Found {total_gds_evaluations} GDS evaluations")

    if len(missing_sessions) > 0:
        with open("missing_sessions.csv", "w") as f:
            for line in missing_sessions:
                f.write(line + "\n")
        logging.critical(
            f"{len(missing_sessions)} sessions are corrupt/missing, check missing_sessions.csv. Aborting..."
        )
        sys.exit(1)

    return subjects


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
                if not "GDS" in data:
                    logging.debug(f"GDS entry missing, skipping {path}")
                    return None
                return cls(int(data["GDS"]), int(data["visit"]), float(data["age"]))
        except:
            logging.warning(f"Could not read GDS file {path}")
            return None


class MRIData:
    def __init__(self, filenames, day):
        self.filenames = filenames
        self.day = day

    @classmethod
    def load(cls, path):
        try:
            day = path[-4:]
            filenames = []
            with open(path + ".json") as f:
                data = json.load(f)["ResultSet"]["Result"]
                if len(data) % 2 != 0:
                    logging.error(
                        "MRI metadata doesn't seem to contain both BIDS and NIFTI files in {}".format(
                            path
                        )
                    )
                for file in data:
                    if file["file_content"] == "BIDS":
                        bids_file = path + "/" + file["Name"]
                        file_without_extension = bids_file[:-5]
                        filenames.append(file_without_extension)
                    if file["file_content"] == "NIFTI_RAW":
                        # Verify data file is there
                        session_id = "{},{}".format(
                            path.split("/")[-1], path.split("/")[-2]
                        )
                        try:
                            nifti_file = path + "/" + file["Name"]
                            correct_size = int(file["Size"])
                            actual_size = os.path.getsize(nifti_file)
                            if actual_size < correct_size * 0.9:
                                logging.error(f"Found corrupted file! {nifti_file}")
                                missing_sessions.add(session_id)
                        except OSError as e:
                            logging.error(f"Missing file {nifti_file}")
                            missing_sessions.add(session_id)

            return cls(filenames, day)
        except:
            logging.warning(f"Could not read MRI metadata for {path}")
            traceback.print_exception()
            return None
