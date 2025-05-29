import logging

class CustomLogger(logging.Logger):
    def __init__(self, name: str = "main", level: int = logging.INFO):
        super().__init__(name, level)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
        self.addHandler(handler)

logging.setLoggerClass(CustomLogger)

def get_logger(name: str = "main") -> logging.Logger:
    return logging.getLogger(name)