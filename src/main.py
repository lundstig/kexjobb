import data
import logging

logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.DEBUG)

subjects = data.load_subjects()

mri_paths = [path for subject in subjects for path in subject.get_mri_paths()]
logging.info("Found {} MRI images".format(len(mri_paths)))

