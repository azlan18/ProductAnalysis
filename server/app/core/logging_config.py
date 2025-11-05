"""
Logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Configure application-wide logging."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler - for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # File handler - for all logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    root_logger.addHandler(file_handler)
    
    # Separate file handler for pipeline logs
    pipeline_handler = logging.FileHandler(log_dir / "pipeline.log")
    pipeline_handler.setLevel(logging.DEBUG)
    pipeline_format = logging.Formatter(
        '%(asctime)s - PIPELINE - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    pipeline_handler.setFormatter(pipeline_format)
    
    # Create pipeline logger
    pipeline_logger = logging.getLogger("pipeline")
    pipeline_logger.addHandler(pipeline_handler)
    pipeline_logger.setLevel(logging.DEBUG)
    
    # Create API logger
    api_logger = logging.getLogger("api")
    api_logger.addHandler(file_handler)
    api_logger.setLevel(logging.INFO)
    
    logging.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)

