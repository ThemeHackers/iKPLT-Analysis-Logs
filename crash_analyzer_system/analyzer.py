"""
Main Crash Analyzer - Orchestrates the entire crash report analysis workflow
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .device_manager import DeviceManager
from .parser import CrashReportParser
from .database import DatabaseManager
from .config import CRASH_REPORTS_DIR, CRASH_REPORT_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrashAnalyzer:
    """Main crash analyzer orchestrator"""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.parser = CrashReportParser()
        self.db = DatabaseManager()
        self.crash_reports_dir = CRASH_REPORTS_DIR
        self.extract_raw = CRASH_REPORT_CONFIG["extract_raw"]
        self.keep_on_device = CRASH_REPORT_CONFIG["keep_on_device"]
    
    async def analyze_device(self, udid: str = None) -> Dict[str, Any]:
        """Analyze a device and extract all crash reports"""
        results = {
            'success': False,
            'device_udid': None,
            'crash_reports_extracted': 0,
            'crash_reports_processed': 0,
            'errors': []
        }
        
        try:
            # Connect to device
            logger.info("Connecting to device...")
            if not await self.device_manager.connect_device(udid):
                results['errors'].append("Failed to connect to device")
                return results
            
            device_udid = self.device_manager.device.serial
            results['device_udid'] = device_udid
            logger.info(f"Connected to device: {device_udid}")
            
            # Get device information
            device_info = await self.device_manager.get_device_info()
            self.db.insert_device(device_udid, device_info)
            
            # List crash reports
            logger.info("Listing crash reports...")
            crash_reports = await self.device_manager.get_crash_reports()
            
            if not crash_reports:
                logger.info("No crash reports found on device")
                results['success'] = True
                return results
            
            logger.info(f"Found {len(crash_reports)} crash reports")
            results['crash_reports_extracted'] = len(crash_reports)
            
            # Download and process each crash report
            processed_count = 0
            for report_name in crash_reports:
                try:
                    # Download crash report
                    output_path = self.crash_reports_dir / report_name
                    logger.info(f"Downloading: {report_name}")
                    
                    if await self.device_manager.download_crash_report(report_name, str(output_path)):
                        # Parse crash report
                        logger.info(f"Parsing: {report_name}")
                        parsed_data = self.parser.parse_file(str(output_path))
                        
                        if parsed_data:
                            # Add device UDID
                            parsed_data['device_udid'] = device_udid
                            
                            # Store in database
                            self.db.insert_crash_report(parsed_data)
                            processed_count += 1
                            logger.info(f"Processed: {report_name}")
                        
                        # Optionally delete from device
                        if not self.keep_on_device:
                            await self.device_manager.delete_crash_report(report_name)
                            logger.info(f"Deleted from device: {report_name}")
                    
                except Exception as e:
                    logger.error(f"Error processing {report_name}: {e}")
                    results['errors'].append(f"Error processing {report_name}: {str(e)}")
            
            results['crash_reports_processed'] = processed_count
            results['success'] = True
            
            # Disconnect
            self.device_manager.disconnect()
            
            logger.info(f"Analysis complete. Processed {processed_count}/{len(crash_reports)} crash reports")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            results['errors'].append(str(e))
        
        return results
    
    async def list_devices(self) -> List[Dict[str, Any]]:
        """List all connected devices"""
        return await self.device_manager.list_devices()
    
    def get_crash_reports(self, device_udid: str = None, limit: int = 100) -> List[Dict]:
        """Get crash reports from database"""
        return self.db.get_crash_reports(device_udid, limit)
    
    def search_crash_reports(self, query: str, limit: int = 100) -> List[Dict]:
        """Search crash reports"""
        return self.db.search_crash_reports(query, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self.db.get_statistics()
    
    def export_to_json(self, output_path: str):
        """Export crash reports to JSON"""
        self.db.export_to_json(output_path)
        logger.info(f"Exported crash reports to {output_path}")
    
    async def process_local_file(self, file_path: str, device_udid: str = "local") -> Dict[str, Any]:
        """Process a local crash report file"""
        results = {
            'success': False,
            'errors': []
        }
        
        try:
            # Parse file
            parsed_data = self.parser.parse_file(file_path)
            
            if parsed_data:
                # Add device UDID
                parsed_data['device_udid'] = device_udid
                
                # Store in database
                self.db.insert_crash_report(parsed_data)
                results['success'] = True
                logger.info(f"Processed local file: {file_path}")
            else:
                results['errors'].append("Failed to parse file")
        
        except Exception as e:
            logger.error(f"Error processing local file {file_path}: {e}")
            results['errors'].append(str(e))
        
        return results
