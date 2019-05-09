import analysis
import coloredlogs, logging
import data
import export

coloredlogs.install(fmt="[%(asctime)s] %(message)s", level=logging.INFO)
fh = logging.FileHandler('log')
fh.setLevel(logging.DEBUG)
logging.getLogger().addHandler(fh)

subjects = data.load_subjects()
analysis.print_offset_stats(subjects)
export.export_all(subjects, "/mnt/data/oasis_out/")
