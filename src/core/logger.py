import logging
import sys

# Define the log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str = "ai_agent_logger", level: str = "debug") -> logging.Logger:
    """
    Sets up a stream logger that outputs to stdout.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())
    logger.propagate = False 
    if not logger.handlers:
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
    return logger

# Global instance for use across modules
logger = setup_logger(level="Debug")