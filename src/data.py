import json
import logging
import os
import parsing
import sys
import traceback
from math import inf
from bisect import bisect_left

root = "/mnt/data/oasis-3/"

missing_sessions = set()


class Subject:
    def __init__(self, subject_id, experiments, cdr_data):
        self.subject_id = subject_id
        self.experiments = experiments
        self.cdr_data = cdr_data[subject_id]
        self.mri_data = [MRIData.load(mri_path) for mri_path in self.get_mri_paths()]
        self.cdr_days = sorted(cdr.day for cdr in self.cdr_data)
        self.mri_days = sorted(mri.day for mri in self.mri_data)

    def build_path(self, filename): return root + self.subject_id + "/" + filename

    def get_mri_paths(self):
        return [
            self.build_path(experiment)
            for experiment in self.experiments
            if "_MR_" in experiment
        ]

    def get_cdr_paths(self):
        return [
            self.build_path(experiment + ".json")
            for experiment in self.experiments
            if "_USDb6" in experiment
        ]

    def get_mri_cdr_offset_indices(self):
        pre_indices = [
            bisect_left(self.cdr_days, mri_day) - 1 for mri_day in self.mri_days
        ]
        post_indices = [
            bisect_left(self.cdr_days, mri_day) for mri_day in self.mri_days
        ]
        return pre_indices, post_indices

    def get_mri_cdr_offsets(self):
        pre_indices, post_indices = self.get_mri_cdr_offset_indices()
        pre = [
            self.mri_days[mri] - self.cdr_days[i]
            if 0 <= i < len(self.cdr_days)
            else inf
            for mri, i in enumerate(pre_indices)
        ]
        post = [
            self.cdr_days[i] - self.mri_days[mri]
            if 0 <= i < len(self.cdr_days)
            else inf
            for mri, i in enumerate(post_indices)
        ]
        return pre, post

    def get_min_offsets(self):
        pre, post = self.get_mri_cdr_offsets()
        return [min(a, b) for a, b in zip(pre, post)]

    @classmethod
    def load(cls, subject_id, cdr_data):
        path = root + subject_id + "/"
        experiments = parsing.parse_experiments(path + "experiments.json")
        return cls(subject_id, experiments, cdr_data)


def load_subjects():
    logging.info("Loading data...")
    cdr_data = parsing.parse_cdr_ratings(root + 'clinical.csv')
    with open(root + "subjects") as f:
        subjects = [Subject.load(line.strip(), cdr_data) for line in f]

    total_mri_sessions = sum(len(subject.get_mri_paths()) for subject in subjects)
    total_cdr_evaluations = sum(len(subject.get_cdr_paths()) for subject in subjects)
    logging.info(f"Found {len(subjects)} subjects")
    logging.info(f"Found {total_mri_sessions} MRI sessions")
    logging.info(f"Found {total_cdr_evaluations} cdr evaluations")

    if missing_sessions:
        with open("missing_sessions.csv", "w") as f:
            for line in missing_sessions:
                f.write(line + "\n")
        logging.critical(
            f"{len(missing_sessions)} sessions are corrupt/missing, check missing_sessions.csv. Aborting..."
        )
        sys.exit(1)

    return subjects


class CDRData:
    def __init__(self, day, cdr):
        self.day = day
        self.cdr = cdr

    def __repr__(self):
        return f"(day={{self.day}}, cdr={{self.cdr}})"


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
            return cls(filenames, int(day))
        except:
            logging.warning(f"Could not read MRI metadata for {path}")
            return None
