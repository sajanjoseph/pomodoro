import logging,logging.handlers
from settings import LOGFILE_NAME as LOG_OUTPUTFILE
def init_logging():
    filehandler =logging.handlers.RotatingFileHandler(LOG_OUTPUTFILE, maxBytes=9000, backupCount=5)
    fmtr = logging.Formatter("%(asctime)s - %(funcName)s - %(lineno)d - %(levelname)s - %(message)s")
    filehandler.setFormatter(fmtr)
    logger = logging.getLogger("pomodoro")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(filehandler)

init_logging()