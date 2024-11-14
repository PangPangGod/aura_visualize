import os
from datetime import datetime
from pydantic import BaseModel
from loguru import logger
import sys

class BaseLogger():
    def get_logger(self):
        logger.remove()
        logger.configure(**self.LOGURU_SETTINGS)
        return logger
    
    @staticmethod
    def _get_session_log_file_name(base_path : str = "logs") -> str:
        time = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(base_path, f"session_{time}.log")

    LOGURU_SETTINGS = {
        "handlers" : [
            dict(sink=sys.stderr, format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}"),
            dict(sink=_get_session_log_file_name(), format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}", enqueue=True),
        ]
    }

systemlogger = BaseLogger().get_logger()