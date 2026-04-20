"""
Crash Report Parser - Parse iOS crash report files
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CrashReportParser:
    """Parse iOS crash report files (.ips, .panic, .crash)"""
    
    def __init__(self):
        self.supported_extensions = ['.ips', '.panic', '.crash', '.txt']
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse a crash report file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_extensions:
            logger.warning(f"Unsupported file type: {file_ext}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return None
        
        # Parse based on file type
        if file_ext == '.ips':
            return self._parse_ips(content, file_path)
        elif file_ext == '.panic':
            return self._parse_panic(content, file_path)
        elif file_ext == '.crash':
            return self._parse_crash(content, file_path)
        else:
            return self._parse_generic(content, file_path)
    
    def _parse_ips(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse .ips file (iOS crash report format)"""
        crash_data = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_type': '.ips',
            'file_size': file_path.stat().st_size,
            'parsed_metadata': {}
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Parse key-value pairs
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'Incident Identifier':
                    crash_data['incident_id'] = value
                elif key == 'CrashReporter Key':
                    crash_data['crash_reporter_key'] = value
                elif key == 'Build Version':
                    crash_data['build_version'] = value
                elif key == 'Product Type':
                    crash_data['product_type'] = value
                elif key == 'OS Version':
                    crash_data['os_version'] = value
                elif key == 'Date/Time':
                    crash_data['crash_date'] = value.split(' ')[0] if ' ' in value else value
                    crash_data['crash_time'] = value.split(' ')[1] if ' ' in value else ''
                elif key == 'Exception Type':
                    crash_data['exception_type'] = value
                elif key == 'Exception Message':
                    crash_data['exception_message'] = value
                elif key == 'Process':
                    crash_data['process_name'] = value.split(' ')[0] if ' ' in value else value
                    if '[' in value:
                        crash_data['process_id'] = int(re.search(r'\[(\d+)\]', value).group(1))
                elif key == 'Parent Process':
                    crash_data['parent_process'] = value.split(' ')[0] if ' ' in value else value
                elif key == 'Hardware Model':
                    crash_data['hardware_model'] = value
        
        crash_data['raw_content'] = content
        crash_data['parsed_metadata'] = self._extract_ips_metadata(content)
        
        return crash_data
    
    def _parse_panic(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse .panic file (kernel panic)"""
        crash_data = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_type': '.panic',
            'file_size': file_path.stat().st_size,
            'exception_type': 'Kernel Panic',
            'parsed_metadata': {}
        }
        
        # Extract panic information
        lines = content.split('\n')
        
        for line in lines:
            if 'Panic Version' in line:
                crash_data['build_version'] = line.split(':')[1].strip()
            elif 'Process' in line:
                crash_data['process_name'] = line.split(':')[1].strip()
            elif 'PID' in line:
                crash_data['process_id'] = int(line.split(':')[1].strip())
            elif 'Timestamp' in line or 'Date' in line:
                crash_data['crash_date'] = line.split(':')[1].strip()
        
        crash_data['raw_content'] = content
        crash_data['exception_message'] = 'Kernel panic occurred'
        crash_data['parsed_metadata'] = self._extract_panic_metadata(content)
        
        return crash_data
    
    def _parse_crash(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse .crash file (generic crash format)"""
        crash_data = {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_type': '.crash',
            'file_size': file_path.stat().st_size,
            'parsed_metadata': {}
        }
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('Process:'):
                crash_data['process_name'] = line.split(':')[1].strip()
                if '[' in line:
                    match = re.search(r'\[(\d+)\]', line)
                    if match:
                        crash_data['process_id'] = int(match.group(1))
            elif line.startswith('Exception Type:'):
                crash_data['exception_type'] = line.split(':')[1].strip()
            elif line.startswith('Date/Time:'):
                crash_data['crash_date'] = line.split(':')[1].strip()
            elif line.startswith('OS Version:'):
                crash_data['os_version'] = line.split(':')[1].strip()
        
        crash_data['raw_content'] = content
        crash_data['parsed_metadata'] = self._extract_crash_metadata(content)
        
        return crash_data
    
    def _parse_generic(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Parse generic text file"""
        return {
            'file_name': file_path.name,
            'file_path': str(file_path),
            'file_type': file_path.suffix,
            'file_size': file_path.stat().st_size,
            'raw_content': content,
            'parsed_metadata': {}
        }
    
    def _extract_ips_metadata(self, content: str) -> Dict[str, Any]:
        """Extract additional metadata from .ips file"""
        metadata = {}
        
        # Extract thread that crashed
        if 'Thread' in content:
            thread_match = re.search(r'Thread (\d+)', content)
            if thread_match:
                metadata['crashed_thread'] = thread_match.group(1)
        
        # Extract binary images
        images = re.findall(r'Binary Images:.*?\n\n', content, re.DOTALL)
        if images:
            metadata['binary_images_count'] = len(images)
        
        # Extract stack traces
        stack_traces = re.findall(r'Thread \d+.*?Stack:', content, re.DOTALL)
        metadata['stack_traces_count'] = len(stack_traces)
        
        return metadata
    
    def _extract_panic_metadata(self, content: str) -> Dict[str, Any]:
        """Extract additional metadata from .panic file"""
        metadata = {}
        
        # Extract panic string
        panic_match = re.search(r'Panic String: (.+)', content)
        if panic_match:
            metadata['panic_string'] = panic_match.group(1).strip()
        
        # Extract backtrace
        if 'Backtrace' in content:
            metadata['has_backtrace'] = True
        
        return metadata
    
    def _extract_crash_metadata(self, content: str) -> Dict[str, Any]:
        """Extract additional metadata from .crash file"""
        metadata = {}
        
        # Extract error codes
        error_codes = re.findall(r'Error: (0x[0-9a-fA-F]+)', content)
        if error_codes:
            metadata['error_codes'] = error_codes
        
        return metadata
