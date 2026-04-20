"""
Device Connection Manager - Handle iOS device connections
"""

import asyncio
from typing import Optional, List, Dict, Any
from collections.abc import AsyncGenerator
from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.crash_reports import CrashReportsManager
from pymobiledevice3.services.syslog import SyslogService
from pymobiledevice3.services.diagnostics import DiagnosticsService
from .config import DEVICE_CONFIG
import logging

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manage iOS device connections"""

    def __init__(self):
        self.device = None
        self.lockdown = None
        self.crash_manager = None
        self.syslog_service = None
        self.diagnostics_service = None
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

    async def get_iphone_full_info(self) -> Dict[str, Any]:
        """Get comprehensive iPhone device information"""
        try:
            if not self.lockdown:
                logger.error("Not connected to device")
                return {}


            info = {}

            info['device_name'] = await self.lockdown.get_value("", "DeviceName")
            info['product_type'] = await self.lockdown.get_value("", "ProductType")
            info['product_version'] = await self.lockdown.get_value("", "ProductVersion")
            info['build_version'] = await self.lockdown.get_value("", "BuildVersion")
            info['device_class'] = await self.lockdown.get_value("", "DeviceClass")
            info['hardware_model'] = await self.lockdown.get_value("", "HardwareModel")
            

            try:
                info['region_info'] = await self.lockdown.get_value("", "RegionInfo")
            except:
                info['region_info'] = 'Unknown'
            
            try:
                info['model_number'] = await self.lockdown.get_value("", "ModelNumber")
            except:
                info['model_number'] = 'Unknown'

            info['serial_number'] = await self.lockdown.get_value("", "SerialNumber")
            info['udid'] = self.device.serial if self.device else 'Unknown'

        
            try:
                info['imei'] = await self.lockdown.get_value("", "InternationalMobileEquipmentIdentity")
            except:
                info['imei'] = 'Unknown'

          
            try:
                info['ecid'] = await self.lockdown.get_value("", "UniqueChipID")
            except:
                info['ecid'] = 'Unknown'

           
            try:
                info['meid'] = await self.lockdown.get_value("", "MobileEquipmentIdentifier")
            except:
                info['meid'] = 'Unknown'

            try:
                info['activated'] = await self.lockdown.get_value("", "ActivationState")
            except:
                info['activated'] = 'Unknown'

        
            if self.diagnostics_service:
                try:
                    battery = await self.diagnostics_service.get_battery()
                    if battery:
                        info['battery'] = battery
                except Exception as e:
                    logger.warning(f"Could not get battery info: {e}")

         
            if self.diagnostics_service:
                try:
                    gestalt = await self.diagnostics_service.mobilegestalt([
                        'ModelNumber',
                        'RegionCode',
                        'DeviceColor',
                        'DeviceColorString',
                        'HasBaseband',
                        'SupportedDeviceFamilies',
                    ])
                    if gestalt:
                        info['mobilegestalt'] = gestalt
                except Exception as e:
                    logger.warning(f"Could not get mobilegestalt info: {e}")

            logger.info("Full iPhone info collected")
            return info

        except Exception as e:
            logger.error(f"Failed to get iPhone full info: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}

    async def connect_device(self, udid: str = None) -> bool:
        """Connect to an iOS device"""
        try:
            devices = await usbmux.list_devices()
            if not devices:
                logger.warning("No iOS devices found")
                return False

          
            target_device = None
            if udid:
                for device in devices:
                    if device.serial == udid:
                        target_device = device
                        break
                if not target_device:
                    logger.error(f"Device with UDID {udid} not found")
                    return False
            else:
                target_device = devices[0]

            self.device = target_device
            logger.info(f"Device selected: {target_device.serial}")

           
            from pymobiledevice3.lockdown import create_using_usbmux
            self.lockdown = await create_using_usbmux(serial=target_device.serial)

         
            self.crash_manager = CrashReportsManager(self.lockdown)
            await self.crash_manager.__aenter__()

         
            self.syslog_service = SyslogService(self.lockdown)

          
            self.diagnostics_service = DiagnosticsService(self.lockdown)

            logger.info("Successfully connected to device")
            return True

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        try:
            if not self.lockdown:
                return {}

         
            device_info = await self.lockdown.get_value("", "DeviceName")
            product_type = await self.lockdown.get_value("", "ProductType")
            ios_version = await self.lockdown.get_value("", "ProductVersion")
            hardware_model = await self.lockdown.get_value("", "HardwareModel")
            device_class = await self.lockdown.get_value("", "DeviceClass")

            info = {
                'udid': self.device.serial,
                'device_name': device_info,
                'product_type': product_type,
                'os_version': ios_version,
                'hardware_model': hardware_model,
                'device_class': device_class,
            }

            logger.info(f"Device info: {info}")
            return info

        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return {}
    
    async def get_crash_reports(self) -> List[str]:
        """Get list of crash reports from device using pymobiledevice3 API"""
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return []

           
            reports = await self.crash_manager.ls("/")
            logger.info(f"Found {len(reports)} crash reports")
            return reports

        except Exception as e:
            logger.error(f"Failed to get crash reports: {e}")
            return []
    
    async def extract_panic_reports(self, output_dir: str) -> bool:
        """Extract panic reports using idevicecrashreport.exe (panic-full analysis)"""
        try:
            import subprocess
            from pathlib import Path
            
            if not self.device:
                logger.error("Not connected to device")
                return False
            
           
            idevicecrashreport_path = Path(__file__).parent.parent / "iDevicePanicLogAnalyzer-1.7.4-full" / "lib" / "net45" / "win-x64" / "idevicecrashreport.exe"
            
            if not idevicecrashreport_path.exists():
                logger.warning(f"idevicecrashreport.exe not found at {idevicecrashreport_path}")
                return False
            
           
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
           
            cmd = [
                str(idevicecrashreport_path),
                '-u', self.device.serial,
                '-e',  
                '-k', 
                str(output_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"idevicecrashreport.exe failed: {result.stderr}")
                return False
            
            logger.info(f"Successfully extracted panic reports to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract panic reports: {e}")
            return False
    
    async def get_device_diagnostics(self) -> Dict[str, Any]:
        """Get comprehensive device diagnostics using idevice tools"""
        try:
            import subprocess
            from pathlib import Path
            
            if not self.device:
                logger.error("Not connected to device")
                return {}
            
            diagnostics = {}
            
          
            tools_dir = Path(__file__).parent.parent / "iDevicePanicLogAnalyzer-1.7.4-full" / "lib" / "net45" / "win-x64"
            
           
            ideviceinfo_path = tools_dir / "ideviceinfo.exe"
            if ideviceinfo_path.exists():
                cmd = [str(ideviceinfo_path), '-u', self.device.serial]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    diagnostics['device_info'] = result.stdout
            
         
            idevicediagnostics_path = tools_dir / "idevicediagnostics.exe"
            if idevicediagnostics_path.exists():
                cmd = [str(idevicediagnostics_path), '-u', self.device.serial]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    diagnostics['diagnostics'] = result.stdout
            
            logger.info("Device diagnostics collected")
            return diagnostics
            
        except Exception as e:
            logger.error(f"Failed to get device diagnostics: {e}")
            return {}
    
    async def extract_ips_files(self, output_dir: str) -> List[str]:
        """Extract .ips crash files from device"""
        try:
            import subprocess
            from pathlib import Path
            
            if not self.device:
                logger.error("Not connected to device")
                return []
            
      
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
           
            cmd_list = ['pymobiledevice3', 'crash', 'ls', '--udid', self.device.serial]
            result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"Failed to list crash reports: {result.stderr}")
                return []
            
           
            reports = result.stdout.strip().split('\n') if result.stdout.strip() else []
            ips_files = [r for r in reports if r.endswith('.ips')]
            
            if not ips_files:
                logger.info("No .ips files found on device")
                return []
            
            logger.info(f"Found {len(ips_files)} .ips files on device")
            
           
            downloaded_files = []
            for ips_file in ips_files:
                cmd_download = ['pymobiledevice3', 'crash', 'pull', '--udid', self.device.serial, ips_file, output_dir]
                result = subprocess.run(cmd_download, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    downloaded_path = Path(output_dir) / ips_file
                    if downloaded_path.exists():
                        downloaded_files.append(str(downloaded_path))
                        logger.info(f"Downloaded: {ips_file}")
                else:
                    logger.warning(f"Failed to download {ips_file}: {result.stderr}")
            
            logger.info(f"Successfully downloaded {len(downloaded_files)} .ips files")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Failed to extract .ips files: {e}")
            return []
    
    async def download_crash_report(self, report_name: str, output_path: str) -> bool:
        """Download a crash report from device using pymobiledevice3 API"""
        try:
            from pathlib import Path
            
            if not self.crash_manager:
                logger.error("Not connected to device")
                return False
            
          
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
         
            await self.crash_manager.pull(str(output_dir), entry=report_name, erase=False, progress_bar=True)
            
            logger.info(f"Downloaded crash report to {output_dir}")
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
            
            await self.crash_manager.clear(report_name)
            logger.info(f"Deleted crash report: {report_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete crash report {report_name}: {e}")
            return False
    
    async def watch_crash_reports(self, process_name: Optional[str] = None, raw: bool = False):
        """
        Monitor creation of new crash reports for a given process name.
        Returns an async generator that yields crash reports as they are created.
        """
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return
            
            async for crash_report in self.crash_manager.watch(name=process_name, raw=raw):
                yield crash_report
                
        except Exception as e:
            logger.error(f"Error watching crash reports: {e}")
            raise
    
    async def get_sysdiagnose(self, output_path: str, erase: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Collect sysdiagnose archive from device.
        :param output_path: Path to save the sysdiagnose archive
        :param erase: Whether to erase the sysdiagnose from device after collection
        :param timeout: Maximum time to wait for sysdiagnose completion
        """
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return False
            
            await self.crash_manager.get_new_sysdiagnose(output_path, erase=erase, timeout=timeout)
            logger.info(f"Sysdiagnose collected to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect sysdiagnose: {e}")
            return False
    
    async def stream_syslog(self) -> AsyncGenerator[str, None]:
        """
        Stream syslog messages from device in real-time.
        Returns an async generator that yields syslog lines.
        """
        try:
            if not self.syslog_service:
                logger.error("Syslog service not initialized")
                return
            
            async for syslog_line in self.syslog_service.watch():
                yield syslog_line
                
        except Exception as e:
            logger.error(f"Error streaming syslog: {e}")
            raise
    
    async def get_diagnostics(self) -> Dict[str, Any]:
        """
        Get device diagnostics using MobileGestalt keys.
        Returns diagnostic information about the device.
        """
        try:
            if not self.diagnostics_service:
                logger.error("Diagnostics service not initialized")
                return {}
            
            from pymobiledevice3.exceptions import DeprecationError
            
            try:
            
                diagnostics = await self.diagnostics_service.mobilegestalt()
                
                if not diagnostics or not isinstance(diagnostics, dict):
                    logger.warning("Diagnostics returned empty or invalid data")
                else:
                    logger.info(f"Device diagnostics collected: {len(diagnostics)} entries")
                    return diagnostics
            except DeprecationError:
                logger.warning("MobileGestalt is deprecated on this device, trying alternative methods")
            
          
            try:
                info = await self.diagnostics_service.info("All")
                if info:
                    logger.info("Collected diagnostics using info() method")
                    return info
            except Exception as e:
                logger.warning(f"Failed to get diagnostics via info(): {e}")
            
       
            try:
                ioregistry = await self.diagnostics_service.ioregistry()
                if ioregistry:
                    logger.info("Collected diagnostics via ioregistry()")
                    return {"ioregistry": ioregistry}
            except Exception as e:
                logger.warning(f"Failed to get diagnostics via ioregistry(): {e}")
            
            logger.warning("All diagnostics methods failed")
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get diagnostics: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {}
    
    async def disconnect(self):
        """Disconnect from device"""
        try:
            if self.crash_manager:
                await self.crash_manager.aclose()
                self.crash_manager = None
            
            if self.syslog_service:
                await self.syslog_service.close()
                self.syslog_service = None
            
            if self.diagnostics_service:
                await self.diagnostics_service.close()
                self.diagnostics_service = None
            
            if self.lockdown:
                await self.lockdown.close()
                self.lockdown = None
            
            self.device = None
            
            logger.info("Disconnected from device")
            
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")
