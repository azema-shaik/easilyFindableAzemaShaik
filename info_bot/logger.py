from enum import Enum
import logging


class LogColors(Enum):
    DEBUG = 13
    INFO = 11
    ERROR = 9

class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        rec = super().format(record)
        color = LogColors[record.levelname].value
        return f'\33[38;5;{color}m{rec}\033[0m'
    
log_fmt = '[%(asctime)s] : [%(levelname)s]: [%(filename)s] :[%(lineno)d] : [%(funcName)s] : [%(msg)s]'
datefmt = '%b %m %Y %I:%M:%S %p'    
formatter = logging.Formatter(log_fmt, datefmt= datefmt)
logger = logging.getLogger("agent")
logger.setLevel(logging.DEBUG)
hdlr = logging.FileHandler("info.log", mode = 'w')
hdlr.setLevel(logging.INFO)
hdlr.setFormatter(formatter)

hdlr2 = logging.FileHandler("debug.log", mode = 'w')
hdlr2.setLevel(logging.DEBUG)
hdlr2.setFormatter(formatter)


hdlr3 = logging.StreamHandler()
hdlr3.setLevel(logging.ERROR)
hdlr3.setFormatter(Formatter(log_fmt, datefmt= datefmt))
logger.addHandler(hdlr)
logger.addHandler(hdlr2)
logger.addHandler(hdlr3)


search_results_logger = logging.getLogger('search_results')
search_results_logger.setLevel(logging.INFO)
shdlr = logging.FileHandler('search_results.txt',encoding="utf-8")
shdlr.setLevel(logging.INFO)
shdlr.setFormatter(logging.Formatter('[%(asctime)s]: [%(msg)s]', datefmt = datefmt))
search_results_logger.addHandler(shdlr)