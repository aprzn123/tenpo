import sys
import logging

def create_logger(verbose: bool, log_file: str='tenpo.log') -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if verbose else logging.WARNING)
    logger.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    file_handler = logging.FileHandler(log_file)
#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s")
