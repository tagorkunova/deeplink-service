import sys
import json
import socket
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


class LogstashHandler(logging.Handler):
    def __init__(self, host: str = "logstash", port: int = 5044):
        super().__init__()
        self.host = host
        self.port = port

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            with socket.create_connection((self.host, self.port), timeout=2) as sock:
                sock.sendall((msg + "\n").encode("utf-8"))
        except Exception:
            pass


def setup_logger(service_name: str) -> logging.Logger:
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # stdout handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(JSONFormatter(service_name))
        logger.addHandler(stdout_handler)

        # logstash handler
        logstash_handler = LogstashHandler(host="logstash", port=5044)
        logstash_handler.setFormatter(JSONFormatter(service_name))
        logger.addHandler(logstash_handler)

    return logger
