"""
IPS File Parser
Parse iOS .ips crash report files
"""

import re
import plistlib
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class IPSParser:
    """Parser for iOS .ips crash report files"""
    
    def __init__(self):
        self.ips_data = None
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse an .ips file and extract crash information"""
        try:
            ips_path = Path(file_path)
            if not ips_path.exists():
                logger.error(f"File not found: {file_path}")
                return {}
            
            try:
                with open(ips_path, 'rb') as f:
                    self.ips_data = plistlib.load(f)
            except:
             
                try:
                    with open(ips_path, 'r', encoding='utf-8') as f:
                        self.ips_data = json.load(f)
                except json.JSONDecodeError:
                  
                    try:
                        self.ips_data = {}
                        with open(ips_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and line.startswith('{'):
                                    try:
                                        obj = json.loads(line)
                                        self.ips_data.update(obj)
                                    except json.JSONDecodeError:
                                        pass 
                    except Exception as e:
                        logger.error(f"Failed to parse as JSON Lines: {e}")
                        raise
                except Exception as e:
                    logger.error(f"Failed to parse as JSON: {e}")
                    raise
            
            crash_info = self._extract_crash_info()
            
            logger.info(f"Successfully parsed .ips file: {file_path}")
            return crash_info
            
        except Exception as e:
            logger.error(f"Failed to parse .ips file {file_path}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    def _extract_crash_info(self) -> Dict[str, Any]:
        """Extract crash information from parsed IPS data"""
        if not self.ips_data:
            return {}
        
        crash_info = {
            'file_type': 'ips',
            'timestamp': self.ips_data.get('timestamp', datetime.now().isoformat()),
            'app_name': self._get_app_name(),
            'bundle_id': self._get_bundle_id(),
            'app_version': self._get_app_version(),
            'os_version': self._get_os_version(),
            'device_model': self._get_device_model(),
            'exception_type': self._get_exception_type(),
            'exception_codes': self._get_exception_codes(),
            'termination_reason': self._get_termination_reason(),
            'triggered_by_thread': self._get_triggered_thread(),
            'fault_code': self._get_fault_code(),
            'processes': self._get_processes(),
            'threads': self._get_threads(),
            'images': self._get_images(),
            'system_info': self._get_system_info(),
            'memory_info': self._get_memory_info()
        }
        
        return crash_info
    
    def _get_app_name(self) -> str:
        """Get application name from IPS data"""
        for key in ['app_name', 'appName', 'name', 'ProcessName']:
            if key in self.ips_data:
                return self.ips_data[key]
        return 'unknown'
    
    def _get_bundle_id(self) -> str:
        """Get bundle ID from IPS data"""
    
        if 'agent' in self.ips_data:
            agent = self.ips_data['agent']
            if isinstance(agent, str) and '(' in agent:
             
                return agent.split('(')[0].strip()
        for key in ['bundleID', 'bundle_id', 'BundleIdentifier']:
            if key in self.ips_data:
                return self.ips_data[key]
      
        app_name = self._get_app_name()
        if app_name != 'unknown':
            return app_name
        return 'unknown'
    
    def _get_app_version(self) -> str:
        """Get application version from IPS data"""
      
        if 'agent' in self.ips_data:
            agent = self.ips_data['agent']
            if isinstance(agent, str) and 'iPhone OS' in agent:
             
                parts = agent.split('iPhone OS')
                if len(parts) > 1:
                    version_part = parts[1].split(')')[0].strip()
                    return version_part
       
        os_ver = self._get_os_version()
        if os_ver != 'unknown' and 'iPhone OS' in os_ver:
            parts = os_ver.split('iPhone OS')
            if len(parts) > 1:
                return parts[1].strip()
        if 'appVersion' in self.ips_data:
            return self.ips_data['appVersion']
        elif 'version' in self.ips_data:
            return self.ips_data['version']
        return 'unknown'
    
    def _get_os_version(self) -> str:
        """Get OS version from IPS data"""
        if 'os_version' in self.ips_data:
            return self.ips_data['os_version']
        elif 'OSVersion' in self.ips_data:
            return self.ips_data['OSVersion']
        return 'unknown'
    
    def _get_device_model(self) -> str:
        """Get device model from IPS data"""
       
        if 'agent' in self.ips_data:
            agent = self.ips_data['agent']
            if isinstance(agent, str) and 'iPhone' in agent:
             
                parts = agent.split(';')
                for part in parts:
                    if 'iPhone' in part:
                        return part.strip().split(')')[0]
        if 'device_model' in self.ips_data:
            return self.ips_data['device_model']
        elif 'Model' in self.ips_data:
            return self.ips_data['Model']
        elif 'HardwareModel' in self.ips_data:
            return self.ips_data['HardwareModel']
        return 'unknown'
    
    def _get_exception_type(self) -> str:
        """Get exception type from IPS data"""
        if 'bug_type' in self.ips_data:
            return self.ips_data['bug_type']
        if 'exception' in self.ips_data:
            exception = self.ips_data['exception']
            if isinstance(exception, dict):
                return exception.get('type', 'unknown')
            return str(exception)
        elif 'ExceptionType' in self.ips_data:
            return self.ips_data['ExceptionType']
        return 'unknown'
    
    def _get_exception_codes(self) -> str:
        """Get exception codes from IPS data"""
        if 'bug_type' in self.ips_data:
            return self.ips_data['bug_type']
        if 'exception' in self.ips_data:
            exception = self.ips_data['exception']
            if isinstance(exception, dict):
                codes = exception.get('codes', [])
                if isinstance(codes, list):
                    return ', '.join(str(c) for c in codes)
                return str(codes)
        elif 'ExceptionCodes' in self.ips_data:
            return self.ips_data['ExceptionCodes']
        return 'unknown'
    
    def _get_termination_reason(self) -> str:
        """Get termination reason from IPS data"""
        if 'terminationReason' in self.ips_data:
            return self.ips_data['terminationReason']
        elif 'TerminationReason' in self.ips_data:
            return self.ips_data['TerminationReason']
        return 'unknown'
    
    def _get_triggered_thread(self) -> str:
        """Get triggered thread from IPS data"""
        if 'crashedThread' in self.ips_data:
            return str(self.ips_data['crashedThread'])
        elif 'triggeredThread' in self.ips_data:
            return str(self.ips_data['triggeredThread'])
        return 'unknown'
    
    def _get_fault_code(self) -> str:
        """Get fault code from IPS data"""
        if 'fault' in self.ips_data:
            fault = self.ips_data['fault']
            if isinstance(fault, dict):
                return fault.get('code', 'unknown')
            return str(fault)
        return 'unknown'
    
    def _get_processes(self) -> List[Dict[str, Any]]:
        """Get process information from IPS data"""
        processes = []
        
        if 'processes' in self.ips_data:
            for process in self.ips_data['processes']:
                if isinstance(process, dict):
                    process_info = {
                        'name': process.get('name', 'unknown'),
                        'pid': process.get('pid', 0),
                        'cpu_type': process.get('cpuType', 'unknown'),
                        'state': process.get('state', 'unknown')
                    }
                    processes.append(process_info)
        
        return processes
    
    def _get_threads(self) -> List[Dict[str, Any]]:
        """Get thread information from IPS data"""
        threads = []
        
        if 'threads' in self.ips_data:
            for thread in self.ips_data['threads']:
                if isinstance(thread, dict):
                    thread_info = {
                        'id': thread.get('threadId', 0),
                        'name': thread.get('name', 'unknown'),
                        'state': thread.get('state', 'unknown'),
                        'frames': self._get_thread_frames(thread)
                    }
                    threads.append(thread_info)
        
        return threads
    
    def _get_thread_frames(self, thread: Dict) -> List[Dict[str, Any]]:
        """Get stack frames from thread data"""
        frames = []
        
        if 'frames' in thread:
            for frame in thread['frames']:
                if isinstance(frame, dict):
                    frame_info = {
                        'image': frame.get('image', 'unknown'),
                        'symbol': frame.get('symbol', 'unknown'),
                        'offset': frame.get('offset', 0)
                    }
                    frames.append(frame_info)
        
        return frames
    
    def _get_images(self) -> List[Dict[str, Any]]:
        """Get loaded images/libraries from IPS data"""
        images = []
        
        if 'images' in self.ips_data:
            for image in self.ips_data['images']:
                if isinstance(image, dict):
                    image_info = {
                        'name': image.get('name', 'unknown'),
                        'uuid': image.get('uuid', 'unknown'),
                        'base': image.get('base', 0),
                        'size': image.get('size', 0)
                    }
                    images.append(image_info)
        
        return images
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information from IPS data"""
        system_info = {}
        
        system_keys = ['system', 'System', 'os_version', 'OSVersion', 'device_model', 'Model']
        
        for key in system_keys:
            if key in self.ips_data:
                system_info[key] = self.ips_data[key]
        
        return system_info
    
    def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information from IPS data"""
        memory_info = {}
        
        if 'memory' in self.ips_data:
            memory = self.ips_data['memory']
            if isinstance(memory, dict):
                memory_info = {
                    'used': memory.get('used', 0),
                    'free': memory.get('free', 0),
                    'total': memory.get('total', 0)
                }
        
        return memory_info
    
    def get_summary(self) -> str:
        """Get a summary of the IPS crash report in Thai"""
        if not self.ips_data:
            return "ไม่มีข้อมูล IPS"
        
        crash_info = self._extract_crash_info()
        
        summary = f"""สรุป IPS Crash Report
{'='*50}

ข้อมูลแอปพลิเคชัน:
- ชื่อแอป: {crash_info['app_name']}
- Bundle ID: {crash_info['bundle_id']}
- เวอร์ชัน: {crash_info['app_version']}

ข้อมูลอุปกรณ์:
- ระบบปฏิบัติ: {crash_info['os_version']}
- รุ่นอุปกรณ์: {crash_info['device_model']}

ข้อมูล Crash:
- เวลาเกิด: {crash_info['timestamp']}
- ประเภท Exception: {crash_info['exception_type']}
- รหัส Exception: {crash_info['exception_codes']}
- สาเหตุการสิ้นสุด: {crash_info['termination_reason']}
- Thread ที่เกิด: {crash_info['triggered_by_thread']}
- Fault Code: {crash_info['fault_code']}

Process ที่เกี่ยวข้อง:
"""
        
        for process in crash_info['processes'][:5]:
            summary += f"- {process['name']} (PID: {process['pid']})\n"
        
        return summary


def parse_ips_directory(directory: str) -> List[Dict[str, Any]]:
    """Parse all .ips files in a directory"""
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return []
        
        ips_files = list(dir_path.glob('*.ips'))
        if not ips_files:
            logger.info(f"No .ips files found in {directory}")
            return []
        
        parser = IPSParser()
        crash_reports = []
        
        for ips_file in ips_files:
            crash_info = parser.parse_file(str(ips_file))
            if crash_info:
                crash_info['file_path'] = str(ips_file)
                crash_reports.append(crash_info)
        
        logger.info(f"Parsed {len(crash_reports)} .ips files from {directory}")
        return crash_reports
        
    except Exception as e:
        logger.error(f"Failed to parse IPS directory {directory}: {e}")
        return []
