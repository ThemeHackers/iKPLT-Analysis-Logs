#!/usr/bin/env python3
"""
iOS Crash Report Analyzer System - Main Entry Point
Complete Python Implementation
"""

import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from crash_analyzer_system.cli import main

if __name__ == '__main__':
    main()
