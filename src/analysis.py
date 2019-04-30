from math import inf
from numpy import percentile
from statistics import *
import logging


def print_offset_stats(subjects):
    min_offsets = [
        offset for subject in subjects for offset in subject.get_min_offsets()
    ]
    no_gdr_count = min_offsets.count(inf)
    min_offsets = list(offset for offset in min_offsets if offset != inf)

    if no_gdr_count > 0:
        logging.warning(f"{no_gdr_count} MRI pictures have no possible GDR tag")
    u = round(mean(min_offsets))
    v = round(pvariance(min_offsets))
    med = round(median(min_offsets))
    p90 = round(percentile(min_offsets, 90))
    p99 = round(percentile(min_offsets, 99))
    logging.info(f"GDR tag offset µ: {u}")
    logging.info(f"GDR tag offset variance: {v}")
    logging.info(f"GDR tag offset median: {med}")
    logging.info(f"GDR tag offset 90 percentile: {p90}")
    logging.info(f"GDR tag offset 99 percentile: {p99}")
