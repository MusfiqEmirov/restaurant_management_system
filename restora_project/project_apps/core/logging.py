import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Log qovluğunu yarat
LOG_DIR = Path(__file__).resolve().parent.parent.parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)

def get_logger(name):
    """
    Modul üçün log qaytarır.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Konsol handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Fayl handler
        log_file = LOG_DIR / f'{name}.log'
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        logger.setLevel(logging.INFO)
    
    return logger