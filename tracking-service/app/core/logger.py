import sys
import json
import logging
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.msg, dict):
            log_data = record.msg
        else:
            log_data = {"message": record.getMessage()}

        log_data.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        log_data.setdefault("level", record.levelname)
        log_data.setdefault("service", self.service_name)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(service_name: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter(service_name))
        logger.addHandler(handler)

    return logger
