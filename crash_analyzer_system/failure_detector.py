"""
Device Failure Detection and Pattern Recognition Module
Comprehensive iOS Kernel Panic Analysis
"""

import re
from typing import Dict, List, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import logging

from .fault_codes import (
    get_fault_code_info,
    decode_bitwise_fault_code,
    get_i2c_bus_info,
    get_deep_subsystem_panic_info,
    is_three_minute_reboot,
    DEEP_SUBSYSTEM_PANICS
)

logger = logging.getLogger(__name__)


class FailureDetector:
    """Detect device failures and analyze crash patterns"""
    
    MEMORY_ERROR_PATTERNS = [
        r'out of memory',
        r'memory corruption',
        r'segmentation fault',
        r'memory access',
        r'heap corruption',
        r'buffer overflow',
        r'stack overflow',
        r'null pointer dereference',
        r'invalid memory access',
        r'EXC_BAD_ACCESS',
        r'EXC_BAD_INSTRUCTION',
        r'KERN_INVALID_ADDRESS',
        r'KERN_PROTECTION_FAILURE',
        r'use after free',
        r'double free',
        r'memory leak',
        r'page fault',
        r'access violation',
        r'corrupted memory'
    ]
    
    CRITICAL_EXCEPTIONS = [
        'EXC_BAD_ACCESS',
        'EXC_BAD_INSTRUCTION',
        'SIGSEGV',
        'SIGBUS',
        'SIGABRT',
        'SIGKILL',
        'SIGILL'
    ]
    
    STABILITY_THRESHOLD = 3
    CRITICAL_THRESHOLD = 10
    
    def __init__(self):
        self.crash_history = []
        self.process_crash_counts = Counter()
        self.exception_counts = Counter()
        self.memory_error_counts = Counter()
    
    def analyze_panic_log_advanced(self, crash_report: Dict[str, Any], device_series: str = None) -> Dict[str, Any]:
        """Advanced panic log analysis using comprehensive fault code database"""
        analysis = {
            'is_critical': False,
            'failure_type': 'unknown',
            'memory_errors': [],
            'exception_type': crash_report.get('exception_type', 'unknown'),
            'exception_codes': crash_report.get('exception_codes', 'unknown'),
            'termination_reason': crash_report.get('termination_reason', 'unknown'),
            'triggered_by_thread': crash_report.get('triggered_by_thread', 'unknown'),
            'fault_code': crash_report.get('fault_code', 'unknown'),
            'risk_level': 'low',
            'fault_code_info': None,
            'bitwise_decoded': None,
            'i2c_bus_errors': [],
            'deep_subsystem_panics': [],
            'is_three_minute_reboot': False,
            'three_minute_reboot_indicators': []
        }
        
        if analysis['exception_type'] in self.CRITICAL_EXCEPTIONS:
            analysis['is_critical'] = True
            analysis['failure_type'] = 'critical_exception'
            analysis['risk_level'] = 'critical'
        
        content = str(crash_report)
        memory_errors = self._detect_memory_errors(content)
        analysis['memory_errors'] = memory_errors
        
        if memory_errors:
            analysis['is_critical'] = True
            analysis['failure_type'] = 'memory_error'
            analysis['risk_level'] = 'high'
        
        fault_code = analysis['fault_code']
        if fault_code and fault_code != 'unknown':
            fault_info = get_fault_code_info(fault_code, device_series)
            analysis['fault_code_info'] = fault_info
            
            if fault_code.startswith('0x') or fault_code.isdigit():
                bitwise_decoded = decode_bitwise_fault_code(fault_code, device_series)
                if bitwise_decoded.get('is_combinational'):
                    analysis['bitwise_decoded'] = bitwise_decoded
                    analysis['is_critical'] = True
                    analysis['failure_type'] = 'combinational_hardware_failure'
                    analysis['risk_level'] = 'critical'
        
        i2c_errors = self._detect_i2c_bus_errors(content)
        if i2c_errors:
            analysis['i2c_bus_errors'] = i2c_errors
            analysis['is_critical'] = True
            analysis['failure_type'] = 'i2c_bus_failure'
            analysis['risk_level'] = 'critical'
        
        deep_panics = self._detect_deep_subsystem_panics(content)
        if deep_panics:
            analysis['deep_subsystem_panics'] = deep_panics
            analysis['is_critical'] = True
            analysis['failure_type'] = 'deep_subsystem_panic'
            analysis['risk_level'] = 'critical'
        
        reboot_analysis = is_three_minute_reboot(content)
        analysis['is_three_minute_reboot'] = reboot_analysis['is_three_minute_reboot']
        analysis['three_minute_reboot_indicators'] = reboot_analysis['found_indicators']
        
        if analysis['is_three_minute_reboot']:
            analysis['is_critical'] = True
            if analysis['failure_type'] == 'unknown':
                analysis['failure_type'] = 'watchdog_timeout'
            analysis['risk_level'] = 'high'
        
        fault_analysis = self._analyze_exception_codes(analysis['exception_codes'])
        analysis.update(fault_analysis)
        
        return analysis
    
    def _detect_i2c_bus_errors(self, content: str) -> List[Dict[str, Any]]:
        """Detect I2C bus errors in crash report content"""
        i2c_errors = []
        
        i2c_patterns = [
            r'i2c\d+.*checkInterrupts',
            r'i2c\d+.*_checkInterrupts',
            r'i2c\d+.*error',
            r'i2c\d+.*timeout',
            r'i2c\d+.*failed',
            r'i2c\d+.*nack',
            r'i2c\d+.*ack',
            r'i2cm\d+.*error',
            r'i2cm\d+.*timeout',
            r'i2c.*bus.*error',
            r'i2c.*short',
            r'i2c.*stall',
            r'i2c.*hang',
            r'i2c.*lockup',
            r'SMC.*i2C.*error',
            r'SMC.*i2C.*timeout'
        ]
        
        for pattern in i2c_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                bus_match = re.search(r'(i2c\d+|i2cm\d+)', match, re.IGNORECASE)
                if bus_match:
                    bus_name = bus_match.group(1)
                    bus_info = get_i2c_bus_info(bus_name)
                    i2c_errors.append({
                        'bus_name': bus_name,
                        'error_string': match,
                        'bus_info': bus_info
                    })
        
        return i2c_errors
    
    def _detect_deep_subsystem_panics(self, content: str) -> List[Dict[str, Any]]:
        """Detect deep subsystem panics in crash report content"""
        detected_panics = []
        
        for panic_key in DEEP_SUBSYSTEM_PANICS.keys():
            if panic_key.lower() in content.lower():
                panic_info = get_deep_subsystem_panic_info(panic_key)
                detected_panics.append(panic_info)
        
        additional_patterns = [
            (r'CPU\s+\d+\s+Panic', 'CPU Core Panic'),
            (r'AOP.*PANIC', 'AOP Panic'),
            (r'EXBrightComponent.*panic', 'EXBrightComponent Panic'),
            (r'AppleBCMWLAN.*panic', 'WiFi/WLAN Panic'),
            (r'CP_COM_NORM.*REQUEST', 'CP Communication Panic'),
            (r'Kernel.*data.*abort', 'Kernel Data Abort'),
            (r'NMI.*POWER', 'NMI Power Panic'),
            (r'SMC.*PANIC', 'SMC Panic'),
            (r'AP.*Panic', 'Application Processor Panic'),
            (r'PMU.*Panic', 'Power Management Unit Panic'),
            (r'GPU.*Panic', 'GPU Panic'),
            (r'ISP.*Panic', 'Image Signal Processor Panic'),
            (r'DCP.*Panic', 'Display Controller Panic')
        ]
        
        for pattern, panic_name in additional_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected_panics.append({
                    'panic_type': panic_name,
                    'description': f'Detected {panic_name} in crash log',
                    'severity': 'critical',
                    'causes': ['Hardware failure', 'Subsystem communication failure']
                })
        
        return detected_panics
    
    def analyze_panic_log(self, crash_report: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single panic log for failure indicators"""
        analysis = {
            'is_critical': False,
            'failure_type': 'unknown',
            'memory_errors': [],
            'exception_type': crash_report.get('exception_type', 'unknown'),
            'exception_codes': crash_report.get('exception_codes', 'unknown'),
            'termination_reason': crash_report.get('termination_reason', 'unknown'),
            'triggered_by_thread': crash_report.get('triggered_by_thread', 'unknown'),
            'fault_code': crash_report.get('fault_code', 'unknown'),
            'risk_level': 'low'
        }
        
        if analysis['exception_type'] in self.CRITICAL_EXCEPTIONS:
            analysis['is_critical'] = True
            analysis['failure_type'] = 'critical_exception'
            analysis['risk_level'] = 'critical'
        
        content = str(crash_report)
        memory_errors = self._detect_memory_errors(content)
        analysis['memory_errors'] = memory_errors
        
        if memory_errors:
            analysis['is_critical'] = True
            analysis['failure_type'] = 'memory_error'
            analysis['risk_level'] = 'high'
        
        fault_analysis = self._analyze_exception_codes(analysis['exception_codes'])
        analysis.update(fault_analysis)
        
        return analysis
    
    def _detect_memory_errors(self, content: str) -> List[str]:
        """Detect memory errors in crash report content"""
        errors = []
        for pattern in self.MEMORY_ERROR_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append(pattern)
        return errors
    
    def _analyze_exception_codes(self, exception_codes: str) -> Dict[str, Any]:
        """Analyze exception codes for specific failure patterns"""
        analysis = {
            'is_hardware_related': False,
            'is_software_related': True,
            'code_meaning': 'unknown'
        }
        
        if not exception_codes or exception_codes == 'unknown':
            return analysis
        
        exception_codes_lower = exception_codes.lower() if exception_codes else ''
        
        if '0x00000000' in exception_codes or '0x0' in exception_codes:
            analysis['code_meaning'] = 'null_pointer'
            analysis['is_critical'] = True
        
        elif '0xdead' in exception_codes_lower or '0xbaad' in exception_codes_lower:
            analysis['code_meaning'] = 'memory_corruption'
            analysis['is_critical'] = True
            analysis['is_hardware_related'] = True
        
        elif '0x8badf00d' in exception_codes_lower:
            analysis['code_meaning'] = 'application_watchdog_timeout'
            analysis['is_critical'] = True
        
        elif '0xdead10cc' in exception_codes_lower:
            analysis['code_meaning'] = 'background_task_timeout'
            analysis['is_critical'] = True
        
        elif '0xbad22222' in exception_codes_lower:
            analysis['code_meaning'] = 'invalid_address'
            analysis['is_critical'] = True
        
        elif '0xdeadfa11' in exception_codes_lower:
            analysis['code_meaning'] = 'custom_stack_corruption'
            analysis['is_critical'] = True
        
        elif '0x0000000' in exception_codes:
            analysis['code_meaning'] = 'null_dereference'
            analysis['is_critical'] = True
        
        elif 'KERN_INVALID_ADDRESS' in exception_codes:
            analysis['code_meaning'] = 'invalid_memory_access'
            analysis['is_hardware_related'] = True
            analysis['is_critical'] = True
        
        elif 'KERN_PROTECTION_FAILURE' in exception_codes:
            analysis['code_meaning'] = 'memory_protection_violation'
            analysis['is_critical'] = True
        
        return analysis
    
    def analyze_crash_patterns(self, crash_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across multiple crash reports"""
        if not crash_reports:
            return {
                'total_crashes': 0,
                'most_unstable_processes': [],
                'most_common_exceptions': [],
                'trend': 'no_data',
                'system_health': 'unknown'
            }
        
        pattern_analysis = {
            'total_crashes': len(crash_reports),
            'process_crashes': defaultdict(int),
            'exception_types': defaultdict(int),
            'memory_errors': defaultdict(int),
            'crash_timeline': []
        }
        
        for report in crash_reports:
            if 'processes' in report and report['processes']:
                for process in report['processes']:
                    if isinstance(process, dict):
                        process_name = process.get('name', 'unknown')
                        pattern_analysis['process_crashes'][process_name] += 1
            
            exception_type = report.get('exception_type', 'unknown')
            pattern_analysis['exception_types'][exception_type] += 1
            
            content = str(report)
            for pattern in self.MEMORY_ERROR_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_analysis['memory_errors'][pattern] += 1
            
            timestamp = report.get('timestamp', datetime.now().isoformat())
            pattern_analysis['crash_timeline'].append(timestamp)
        
        unstable_processes = sorted(
            pattern_analysis['process_crashes'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        critical_processes = [
            {'name': name, 'count': count, 'status': 'critical' if count >= self.CRITICAL_THRESHOLD else 'unstable'}
            for name, count in unstable_processes
            if count >= self.STABILITY_THRESHOLD
        ]
        
        common_exceptions = sorted(
            pattern_analysis['exception_types'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        trend = self._determine_crash_trend(pattern_analysis['crash_timeline'])
        
     
        system_health = self._determine_system_health(critical_processes, pattern_analysis['total_crashes'])
        
        return {
            'total_crashes': pattern_analysis['total_crashes'],
            'most_unstable_processes': critical_processes,
            'most_common_exceptions': common_exceptions,
            'memory_error_summary': dict(pattern_analysis['memory_errors']),
            'trend': trend,
            'system_health': system_health
        }
    
    def _determine_crash_trend(self, timeline: List[str]) -> str:
        """Determine crash trend based on timeline"""
        if len(timeline) < 2:
            return 'insufficient_data'
        
     
        mid_point = len(timeline) // 2
        recent_crashes = len(timeline[mid_point:])
        earlier_crashes = len(timeline[:mid_point])
        
        if recent_crashes > earlier_crashes * 1.5:
            return 'increasing'
        elif recent_crashes < earlier_crashes * 0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    def _determine_system_health(self, critical_processes: List[Dict], total_crashes: int) -> str:
        """Determine overall system health"""
        if total_crashes == 0:
            return 'excellent'
        
        critical_count = len([p for p in critical_processes if p['status'] == 'critical'])
        
        if critical_count > 0:
            return 'critical'
        elif len(critical_processes) > 3:
            return 'poor'
        elif len(critical_processes) > 0:
            return 'degraded'
        elif total_crashes > 20:
            return 'needs_attention'
        else:
            return 'good'
    
    def detect_hardware_failure(self, crash_report: Dict[str, Any]) -> Dict[str, Any]:
        """Detect potential hardware failure indicators"""
        hardware_indicators = {
            'is_hardware_related': False,
            'suspected_components': [],
            'confidence': 'low'
        }
        
        exception_type = crash_report.get('exception_type', '')
        exception_codes = crash_report.get('exception_codes', '')
        content = str(crash_report)
        
      
        hardware_patterns = [
            (r'memory.*corruption', 'RAM'),
            (r'bus.*error', 'Motherboard/Bus'),
            (r'cpu.*exception', 'CPU'),
            (r'gpu.*error', 'GPU'),
            (r'storage.*error', 'Storage'),
            (r'nand.*error', 'NAND Flash'),
            (r'flash.*error', 'Flash Storage')
        ]
        
        for pattern, component in hardware_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                hardware_indicators['is_hardware_related'] = True
                hardware_indicators['suspected_components'].append(component)
        

        if exception_codes and ('0xdead' in exception_codes.lower() or '0xbaad' in exception_codes.lower()):
            hardware_indicators['is_hardware_related'] = True
            hardware_indicators['suspected_components'].append('RAM/Memory')
            hardware_indicators['confidence'] = 'high'
        
     
        if len(hardware_indicators['suspected_components']) >= 2:
            hardware_indicators['confidence'] = 'high'
        elif len(hardware_indicators['suspected_components']) == 1:
            hardware_indicators['confidence'] = 'medium'
        
        return hardware_indicators
    
    def generate_failure_report(self, crash_reports: List[Dict[str, Any]]) -> str:
        """Generate comprehensive failure report in Thai"""
        pattern_analysis = self.analyze_crash_patterns(crash_reports)
        
        report = f"""รายงานการวิเคราะห์ความเสียหายของอุปกรณ์
{'='*50}

สถิติโดยรวม:
- Crash Reports ทั้งหมด: {pattern_analysis['total_crashes']}
- สถานะสุขภาพระบบ: {self._translate_health_status(pattern_analysis['system_health'])}
- แนวโน้ม: {self._translate_trend(pattern_analysis['trend'])}

Process ที่ไม่เสถียรที่สุด:
"""
        
        for process in pattern_analysis['most_unstable_processes']:
            report += f"- {process['name']}: {process['count']} crashes ({process['status']})\n"
        
        report += f"\nException Types ที่พบบ่อยที่สุด:\n"
        for exception, count in pattern_analysis['most_common_exceptions']:
            report += f"- {exception}: {count} crashes\n"
        
        if pattern_analysis['memory_error_summary']:
            report += f"\nMemory Errors:\n"
            for error, count in pattern_analysis['memory_error_summary'].items():
                report += f"- {error}: {count} occurrences\n"
        
        return report
    
    def generate_advanced_failure_report(self, crash_report: Dict[str, Any], device_series: str = None) -> str:
        """Generate advanced failure report with comprehensive fault code analysis in Thai"""
        analysis = self.analyze_panic_log_advanced(crash_report, device_series)
        
        report = f"""รายงานการวิเคราะห์ Kernel Panic ขั้นสูง
{'='*60}

ข้อมูลพื้นฐาน:
- Exception Type: {analysis['exception_type']}
- Exception Codes: {analysis['exception_codes']}
- Termination Reason: {analysis['termination_reason']}
- Triggered by Thread: {analysis['triggered_by_thread']}
- Fault Code: {analysis['fault_code']}
- Risk Level: {self._translate_risk_level(analysis['risk_level'])}
- Failure Type: {self._translate_failure_type(analysis['failure_type'])}

"""
        
        if analysis['fault_code_info']:
            fault_info = analysis['fault_code_info']
            report += f"ข้อมูล Fault Code:\n"
            report += f"- คำอธิบาย: {fault_info.get('description', 'N/A')}\n"
            report += f"- รุ่นอุปกรณ์: {fault_info.get('device_series', 'N/A')}\n"
            if fault_info.get('location'):
                report += f"- ตำแหน่ง: {fault_info.get('location', 'N/A')}\n"
            if fault_info.get('severity'):
                report += f"- ความรุนแรง: {fault_info.get('severity', 'N/A')}\n"
            if fault_info.get('solution'):
                report += f"- วิธีแก้ไข: {fault_info.get('solution', 'N/A')}\n"
            report += "\n"
        
        if analysis['bitwise_decoded']:
            decoded = analysis['bitwise_decoded']
            report += f"การวิเคราะห์ Bitwise Fault Code (หลายอุปกรณ์พร้อมกัน):\n"
            report += f"- Original Code: {decoded['original_code']} (Decimal: {decoded['decimal_value']})\n"
            report += f"- จำนวน Component ที่ล้มเหลว: {decoded['component_count']}\n"
            report += f"- Components ที่ตรวจพบ:\n"
            for component in decoded['decoded_components']:
                report += f"  * {component['hex']} ({component['bit_value']}): {component['description']}\n"
            report += "\n"
        
        if analysis['i2c_bus_errors']:
            report += f"I2C Bus Errors ที่ตรวจพบ:\n"
            for i2c_error in analysis['i2c_bus_errors']:
                report += f"- Bus: {i2c_error['bus_name']}\n"
                report += f"  Error: {i2c_error['error_string']}\n"
                bus_info = i2c_error.get('bus_info', {})
                if 'components' in bus_info:
                    report += f"  Components: {', '.join(bus_info['components'])}\n"
                if 'description' in bus_info:
                    report += f"  Description: {bus_info['description']}\n"
            report += "\n"
        
        if analysis['deep_subsystem_panics']:
            report += f"Deep Subsystem Panics ที่ตรวจพบ:\n"
            for panic in analysis['deep_subsystem_panics']:
                report += f"- Type: {panic.get('panic_type', 'N/A')}\n"
                report += f"  Description: {panic.get('description', 'N/A')}\n"
                if panic.get('severity'):
                    report += f"  Severity: {panic.get('severity', 'N/A')}\n"
                if panic.get('causes'):
                    report += f"  Possible Causes:\n"
                    for cause in panic['causes']:
                        report += f"    - {cause}\n"
            report += "\n"
        
        if analysis['is_three_minute_reboot']:
            report += f"ตรวจพบรูปแบบ Three-Minute Reboot Cycle:\n"
            report += f"- Indicators: {', '.join(analysis['three_minute_reboot_indicators'])}\n"
            report += f"- สาเหตุ: Watchdog timer timeout due to failed sensor handshake\n"
            report += f"- ข้อแนะนำ: Logic board ต้องถูก mount ใน test chassis ที่มี OEM parts เต็มรูปแบบ\n"
            report += "\n"
        
        if analysis['memory_errors']:
            report += f"Memory Errors ที่ตรวจพบ:\n"
            for error in analysis['memory_errors']:
                report += f"- {error}\n"
            report += "\n"
        
        return report
    
    def _translate_risk_level(self, risk_level: str) -> str:
        """Translate risk level to Thai"""
        translations = {
            'low': 'ต่ำ',
            'medium': 'ปานกลาง',
            'high': 'สูง',
            'critical': 'วิกฤต'
        }
        return translations.get(risk_level, risk_level)
    
    def _translate_failure_type(self, failure_type: str) -> str:
        """Translate failure type to Thai"""
        translations = {
            'unknown': 'ไม่ทราบ',
            'critical_exception': 'Critical Exception',
            'memory_error': 'Memory Error',
            'combinational_hardware_failure': 'Hardware Failure หลายจุดพร้อมกัน',
            'i2c_bus_failure': 'I2C Bus Failure',
            'deep_subsystem_panic': 'Deep Subsystem Panic',
            'watchdog_timeout': 'Watchdog Timeout'
        }
        return translations.get(failure_type, failure_type)
    
    def _translate_health_status(self, status: str) -> str:
        """Translate health status to Thai"""
        translations = {
            'excellent': 'ดีเยี่ยม',
            'good': 'ดี',
            'needs_attention': 'ต้องติดตาม',
            'degraded': 'ทรุดโทรม',
            'poor': 'แย่',
            'critical': 'วิกฤต',
            'unknown': 'ไม่ทราบ'
        }
        return translations.get(status, status)
    
    def _translate_trend(self, trend: str) -> str:
        """Translate trend to Thai"""
        translations = {
            'increasing': 'เพิ่มขึ้น',
            'decreasing': 'ลดลง',
            'stable': 'คงที่',
            'insufficient_data': 'ข้อมูลไม่เพียงพอ',
            'no_data': 'ไม่มีข้อมูล'
        }
        return translations.get(trend, trend)
