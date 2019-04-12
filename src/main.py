import data
import coloredlogs, logging

coloredlogs.install(fmt="[%(asctime)s] %(message)s", level=logging.INFO)

subjects = data.load_subjects()

mri_paths = [path for subject in subjects for path in subject.get_mri_paths()]
gds_paths = [path for subject in subjects for path in subject.get_gds_paths()]
