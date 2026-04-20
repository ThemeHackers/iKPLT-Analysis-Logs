"""
Device Connection Manager - Handle iOS device connections
"""

import asyncio
from typing import Optional, List, Dict, Any
from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.crash_reports import CrashReportsManager
from .config import DEVICE_CONFIG
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manage iOS device connections"""
    
    def __init__(self):
        self.device = None
        self.lockdown = None
        self.crash_manager = None
        self.connection_timeout = DEVICE_CONFIG["connection_timeout"]
        self.retry_attempts = DEVICE_CONFIG["retry_attempts"]
        self.retry_delay = DEVICE_CONFIG["retry_delay"]
    
    async def list_devices(self) -> List[Dict[str, Any]]:
        """List all connected iOS devices"""
        try:
            devices = await usbmux.list_devices()
            
            device_list = []
            for device in devices:
                device_info = {
                    'udid': device.serial,
                    'connection_type': device.connection_type,
                }
                device_list.append(device_info)
            
            return device_list
            
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            return []
    
    async def connect_device(self, udid: str = None) -> bool:
        """Connect to an iOS device"""
        for attempt in range(self.retry_attempts):
            try:
                # List devices
                devices = await usbmux.list_devices()
                
                if not devices:
                    logger.warning("No iOS devices found")
                    return False
                
                # Select device
                if udid:
                    selected_device = None
                    for device in devices:
                        if device.serial == udid:
                            selected_device = device
                            break
                    
                    if not selected_device:
                        logger.error(f"Device with UDID {udid} not found")
                        return False
                else:
                    selected_device = devices[0]
                
                # Connect to lockdown
                self.lockdown = LockdownClient(selected_device)
                logger.info(f"Connected to device: {selected_device.serial}")
                
                # Get device information
                device_info = await self.get_device_info()
                
                # Initialize crash reports manager
                self.crash_manager = CrashReportsManager(self.lockdown)
                
                self.device = selected_device
                return True
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("All connection attempts failed")
                    return False
        
        return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        try:
            if not self.lockdown:
                return {}
            
            # Get device name
            device_name = self.lockdown.get_value("", "DeviceName")
            
            # Get product type
            product_type = self.lockdown.get_value("", "ProductType")
            
            # Get iOS version
            ios_version = self.lockdown.get_value("", "ProductVersion")
            
            # Get hardware model
            hardware_model = self.lockdown.get_value("", "HardwareModel")
            
            # Get device class
            device_class = self.lockdown.get_value("", "DeviceClass")
            
            device_info = {
                'udid': self.device.serial,
                'device_name': device_name,
                'product_type': product_type,
                'os_version': ios_version,
                'hardware_model': hardware_model,
                'device_class': device_class,
            }
            
            logger.info(f"Device info: {device_info}")
            return device_info
            
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    async def get_crash_reports(self) -> List[str]:
        """Get list of crash reports from device"""
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return []
            
            reports = self.crash_manager.list_crash_reports()
            logger.info(f"Found {len(reports)} crash reports")
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get crash reports: {e}")
            return []
    
    async def download_crash_report(self, report_name: str, output_path: str) -> bool:
        """Download a crash report from device"""
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return False
            
            self.crash_manager.retrieve(report_name, output_path)
            logger.info(f"Downloaded crash report: {report_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download crash report {report_name}: {e}")
            return False
    
    async def delete_crash_report(self, report_name: str) -> bool:
        """Delete a crash report from device"""
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return False
            
            self.crash_manager.remove(report_name)
            logger.info(f"Deleted crash report: {report_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete crash report {report_name}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from device"""
        try:
            if self.crash_manager:
                self.crash_manager = None
            
            if self.lockdown:
                self.lockdown = None
            
            if self.device:
                self.device = None
            
            logger.info("Disconnected from device")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
