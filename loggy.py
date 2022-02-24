import sys
import logging

def setup_logger(verbose: bool, log_file: str='tenpo.log') -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if verbose else logging.WARNING)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))
    logger.addHandler(stdout_handler)
    stdout_handler.setLevel(logging.DEBUG if verbose else logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s"))
    logger.addHandler(file_handler)
#logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="[%(asctime)s] [%(levelname)s] - %(message)s")
