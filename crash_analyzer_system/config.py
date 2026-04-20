"""
Configuration settings for the Crash Analyzer System
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CRASH_REPORTS_DIR = BASE_DIR / "crash_reports"
DATABASE_PATH = DATA_DIR / "crash_analyzer.db"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
CRASH_REPORTS_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_CONFIG = {
    "path": str(DATABASE_PATH),
    "timeout": 30,
}

# Device connection settings
DEVICE_CONFIG = {
    "connection_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 2,
}

# Crash report settings
CRASH_REPORT_CONFIG = {
    "supported_extensions": [".ips", ".panic", ".crash", ".txt"],
    "extract_raw": True,
    "keep_on_device": False,
}

# Logging configuration
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": str(DATA_DIR / "crash_analyzer.log"),
}
