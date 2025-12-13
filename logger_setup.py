
import logging
import json
import time
import os
from logging.handlers import RotatingFileHandler

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Basic fields
        log_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage()
        }

        meta = getattr(record, "meta", None)
        if isinstance(meta, dict):
            log_record.update(meta)

        if record.exc_info:
            exc_type = record.exc_info[0].__name__ if record.exc_info[0] else None
            exc_msg = str(record.exc_info[1]) if record.exc_info[1] else None
            log_record["exception"] = {"type": exc_type, "message": exc_msg}

        return json.dumps(log_record, ensure_ascii=False)

def get_logger(name="openapi_parser", logfile="logs/app.log", level=logging.INFO):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    try:
        os.makedirs(os.path.dirname(logfile) or ".", exist_ok=True)
    except Exception:
        pass

    sh = logging.StreamHandler()
    sh.setFormatter(JsonFormatter())
    logger.addHandler(sh)

    fh = RotatingFileHandler(logfile, maxBytes=3 * 1024 * 1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(JsonFormatter())
    logger.addHandler(fh)

    return logger

