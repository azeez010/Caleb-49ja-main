import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os

# Set up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Create a console handler and set the level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create a timed rotating file handler based on the day
if not os.path.exists("logs"):
    os.mkdir("logs")

log_file_name = f"logs/log_{datetime.datetime.now().strftime('%Y-%m-%d')}.log"
fh = TimedRotatingFileHandler(log_file_name, when="midnight", interval=1, backupCount=7)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
