import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

FORMATTER = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s"
)
logger= logging.getLogger("dssat_nitrogen_analysis")
logger.setLevel("INFO")


if not logger.handlers:
    logging_handler= logging.StreamHandler(sys.stdout)
    logging_handler.setLevel("INFO")
    logging_handler.setFormatter(FORMATTER)
    logger.addHandler(logging_handler)

