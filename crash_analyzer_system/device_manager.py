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

IPHONE_MODEL_MAP = {
    'iPhone1,1': 'iPhone 2G',
    'iPhone1,2': 'iPhone 3G',
    'iPhone2,1': 'iPhone 3GS',
    'iPhone3,1': 'iPhone 4 (GSM)',
    'iPhone3,2': 'iPhone 4 (GSM Rev A)',
    'iPhone3,3': 'iPhone 4 (CDMA)',
    'iPhone4,1': 'iPhone 4S',
    'iPhone5,1': 'iPhone 5 (GSM)',
    'iPhone5,2': 'iPhone 5 (Global)',
    'iPhone5,3': 'iPhone 5c (GSM)',
    'iPhone5,4': 'iPhone 5c (Global)',
    'iPhone6,1': 'iPhone 5s (GSM)',
    'iPhone6,2': 'iPhone 5s (Global)',
    'iPhone7,1': 'iPhone 6 Plus',
    'iPhone7,2': 'iPhone 6',
    'iPhone8,1': 'iPhone 6s',
    'iPhone8,2': 'iPhone 6s Plus',
    'iPhone8,4': 'iPhone SE (1st Gen)',
    'iPhone9,1': 'iPhone 7 (Global)',
    'iPhone9,2': 'iPhone 7 Plus (Global)',
    'iPhone9,3': 'iPhone 7 (GSM)',
    'iPhone9,4': 'iPhone 7 Plus (GSM)',
    'iPhone10,1': 'iPhone 8 (Global)',
    'iPhone10,2': 'iPhone 8 Plus (Global)',
    'iPhone10,3': 'iPhone X (Global)',
    'iPhone10,4': 'iPhone 8 (GSM)',
    'iPhone10,5': 'iPhone 8 Plus (GSM)',
    'iPhone10,6': 'iPhone X (GSM)',
    'iPhone11,2': 'iPhone XS',
    'iPhone11,4': 'iPhone XS Max (China)',
    'iPhone11,6': 'iPhone XS Max',
    'iPhone11,8': 'iPhone XR',
    'iPhone12,1': 'iPhone 11',
    'iPhone12,3': 'iPhone 11 Pro',
    'iPhone12,5': 'iPhone 11 Pro Max',
    'iPhone12,8': 'iPhone SE (2nd Gen)',
    'iPhone13,1': 'iPhone 12 mini',
    'iPhone13,2': 'iPhone 12',
    'iPhone13,3': 'iPhone 12 Pro',
    'iPhone13,4': 'iPhone 12 Pro Max',
    'iPhone14,2': 'iPhone 13 Pro',
    'iPhone14,3': 'iPhone 13 Pro Max',
    'iPhone14,4': 'iPhone 13 mini',
    'iPhone14,5': 'iPhone 13',
    'iPhone14,6': 'iPhone SE (3rd Gen)',
    'iPhone14,7': 'iPhone 14',
    'iPhone14,8': 'iPhone 14 Plus',
    'iPhone15,2': 'iPhone 14 Pro',
    'iPhone15,3': 'iPhone 14 Pro Max',
    'iPhone15,4': 'iPhone 15',
    'iPhone15,5': 'iPhone 15 Plus',
    'iPhone16,1': 'iPhone 15 Pro',
    'iPhone16,2': 'iPhone 15 Pro Max',
    'iPhone16,3': 'iPhone 16',
    'iPhone16,4': 'iPhone 16 Plus',
    'iPhone16,5': 'iPhone 16 Pro',
    'iPhone16,6': 'iPhone 16 Pro Max',
}

def get_iphone_model_name(product_type: str) -> str:
    """Get iPhone model name from product type identifier"""
    return IPHONE_MODEL_MAP.get(product_type, product_type)


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
            info['model_name'] = get_iphone_model_name(info['product_type'])
            
            info['hardware_model'] = await self.lockdown.get_value("", "HardwareModel")
            
            try:
                info['device_class'] = await self.lockdown.get_value("", "DeviceClass")
            except:
                info['device_class'] = 'Unknown'

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
                    if gestalt and isinstance(gestalt, dict) and 'Status' not in gestalt:
                        info['mobilegestalt'] = gestalt
                except Exception as e:
                    error_msg = str(e)
                    if 'MobileGestaltDeprecated' in error_msg or 'deprecated' in error_msg.lower():
                        logger.info("MobileGestalt is deprecated on this iOS version (>= 17.4)")
                    else:
                        logger.warning(f"Could not get mobilegestalt info: {e}")

            try:
                storage_info = await self.get_storage_info()
                if storage_info:
                    info['storage'] = storage_info
            except Exception as e:
                logger.warning(f"Could not get storage info: {e}")

            try:
                storage_categories = await self.get_storage_categories()
                if storage_categories:
                    info['storage_categories'] = storage_categories
            except Exception as e:
                logger.warning(f"Could not get storage categories: {e}")

            try:
                jailbreak_info = await self.detect_jailbreak()
                info['jailbreak'] = jailbreak_info
            except Exception as e:
                logger.warning(f"Could not detect jailbreak: {e}")

            try:
                serial = info.get('serial_number', '')
                production_date_info = self.decode_production_date(serial)
                info['production_date'] = production_date_info.get('production_date', 'Unknown')
                
                if production_date_info.get('production_date') != 'Unknown':
                    warranty_info = self.calculate_warranty_date(production_date_info['production_date'])
                    info['warranty_date'] = warranty_info.get('warranty_date', 'Unknown')
                    info['warranty_status'] = warranty_info.get('warranty_status', 'Unknown')
            except Exception as e:
                logger.warning(f"Could not decode production date: {e}")

            try:
                product_type = info.get('product_type', '')
                cpu_info = self.get_cpu_info(product_type)
                info['cpu'] = cpu_info
            except Exception as e:
                logger.warning(f"Could not get CPU info: {e}")

            try:
                charging_status = await self.get_charging_status()
                if charging_status:
                    info['charging'] = charging_status
            except Exception as e:
                logger.warning(f"Could not get charging status: {e}")

            try:
                charge_times = await self.get_charge_times()
                if charge_times:
                    info['charge_times'] = charge_times.get('charge_times', 0)
            except Exception as e:
                logger.warning(f"Could not get charge times: {e}")

            try:
                icloud_status = await self.get_icloud_status()
                if icloud_status:
                    info['icloud_status'] = icloud_status
            except Exception as e:
                logger.warning(f"Could not get iCloud status: {e}")

            try:
                region_code = info.get('model_number', '')
                if not region_code and info.get('mobilegestalt'):
                    region_code = info['mobilegestalt'].get('RegionCode', '')
                sales_region = self.get_sales_region(region_code)
                info['sales_region'] = sales_region
            except Exception as e:
                logger.warning(f"Could not get sales region: {e}")

            try:
                product_type = info.get('product_type', '')
                hard_disk_type = self.get_hard_disk_type(product_type)
                info['hard_disk_type'] = hard_disk_type
            except Exception as e:
                logger.warning(f"Could not get hard disk type: {e}")

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
            from pathlib import Path
            
            if not self.crash_manager:
                logger.error("Not connected to device")
                return []
            
      
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
           
            reports = await self.crash_manager.ls()
            logger.info(f"Crash reports from device: {reports}")
            
            if not reports:
                logger.info("No crash reports found on device")
                return []
            
            ips_files = [r for r in reports if r.endswith('.ips')]
            logger.info(f"Filtered .ips files: {ips_files}")
            
            if not ips_files:
                logger.info("No .ips files found on device")
                return []
            
            logger.info(f"Found {len(ips_files)} .ips files on device")
            
           
            downloaded_files = []
            for ips_file in ips_files:
                try:
                  
                    file_name = ips_file.lstrip('/')
                    
                
                    await self.crash_manager.pull(str(output_dir), entry=file_name, erase=False, progress_bar=False)
                    downloaded_path = Path(output_dir) / file_name
                    if downloaded_path.exists():
                        downloaded_files.append(str(downloaded_path))
                        logger.info(f"Downloaded: {file_name}")
                except Exception as e:
                    logger.warning(f"Failed to download {ips_file}: {e}")
            
            logger.info(f"Successfully downloaded {len(downloaded_files)} .ips files")
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Failed to extract .ips files: {e}")
            return []
    
    async def download_crash_report(self, report_name: str, output_path: str = None) -> bool:
        """Download a crash report from device using pymobiledevice3 API"""
        try:
            from pathlib import Path
            
            if not self.crash_manager:
                logger.error("Not connected to device")
                return False
            
            if output_path:
                output_dir = Path(output_path)
                output_dir.mkdir(parents=True, exist_ok=True)
                await self.crash_manager.pull(str(output_dir), entry=report_name, erase=False, progress_bar=True)
                logger.info(f"Downloaded crash report to {output_dir}")
                return True
            else:
                return False
            
        except Exception as e:
            logger.error(f"Failed to download crash report {report_name}: {e}")
            return False
    
    async def read_crash_report(self, report_name: str) -> str:
        """Read crash report content directly from device"""
        try:
            if not self.crash_manager:
                logger.error("Not connected to device")
                return ""
            
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                await self.crash_manager.pull(temp_dir, entry=report_name, erase=False, progress_bar=False)
                
                report_path = os.path.join(temp_dir, report_name.lstrip('/'))
                if os.path.exists(report_path):
                    with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    logger.info(f"Read crash report: {report_name}")
                    return content
                else:
                    logger.warning(f"Report file not found: {report_path}")
                    return ""
            
        except Exception as e:
            logger.error(f"Failed to read crash report {report_name}: {e}")
            return ""
    
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
    
    async def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information including total and used capacity"""
        try:
            try:
                from pymobiledevice3.services.afc import AFC2Service
                afc_service = AFC2Service(self.lockdown)
            except ImportError:
                try:
                    from pymobiledevice3.services.afc import AFCService
                    afc_service = AFCService(self.lockdown)
                except ImportError:
                    return {}
            
            if not self.lockdown:
                logger.error("Not connected to device")
                return {}
            
            try:
                device_info = await afc_service.get_device_info()
                if device_info:
                    total_bytes = int(device_info.get('TotalDiskCapacity', 0))
                    free_bytes = int(device_info.get('TotalFreeSpace', 0))
                    used_bytes = total_bytes - free_bytes
                    
                    storage_info = {
                        'total_capacity_gb': round(total_bytes / (1024**3), 2),
                        'used_capacity_gb': round(used_bytes / (1024**3), 2),
                        'free_capacity_gb': round(free_bytes / (1024**3), 2),
                        'total_capacity_bytes': total_bytes,
                        'used_capacity_bytes': used_bytes,
                        'free_capacity_bytes': free_bytes
                    }
                    
                    logger.info(f"Storage info collected: {storage_info}")
                    return storage_info
            except Exception as e:
                logger.warning(f"Could not get storage info via AFC: {e}")
            
            await afc_service.close()
            
            
            if self.diagnostics_service:
                try:
                    diagnostics = await self.diagnostics_service.mobilegestalt(['TotalDiskCapacity', 'TotalFreeSpace'])
                    if diagnostics and isinstance(diagnostics, dict) and 'Status' not in diagnostics:
                        total_bytes = diagnostics.get('TotalDiskCapacity', 0)
                        free_bytes = diagnostics.get('TotalFreeSpace', 0)
                        used_bytes = total_bytes - free_bytes
                        
                        storage_info = {
                            'total_capacity_gb': round(total_bytes / (1024**3), 2),
                            'used_capacity_gb': round(used_bytes / (1024**3), 2),
                            'free_capacity_gb': round(free_bytes / (1024**3), 2),
                            'total_capacity_bytes': total_bytes,
                            'used_capacity_bytes': used_bytes,
                            'free_capacity_bytes': free_bytes
                        }
                        return storage_info
                except Exception as e:
                    error_msg = str(e)
                    if 'MobileGestaltDeprecated' in error_msg or 'deprecated' in error_msg.lower():
                        logger.info("MobileGestalt is deprecated on this iOS version (>= 17.4)")
                    else:
                        logger.warning(f"Could not get storage info via diagnostics: {e}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get storage info: {e}")
            return {}
    
    async def get_storage_categories(self) -> Dict[str, Any]:
        """Get storage categories breakdown (System, Apps, Photos, Media, UDisk, Others, Free)"""
        try:
            if not self.diagnostics_service:
                logger.error("Diagnostics service not initialized")
                return {}
            
            try:
               
                storage_data = await self.diagnostics_service.mobilegestalt([
                    'SystemUsage',
                    'UserUsage',
                    'MediaUsage',
                    'PhotoUsage',
                    'AppUsage'
                ])
                
                if storage_data and isinstance(storage_data, dict) and 'Status' not in storage_data:
                    categories = {
                        'System': round(storage_data.get('SystemUsage', 0) / (1024**3), 2),
                        'Apps': round(storage_data.get('AppUsage', 0) / (1024**3), 2),
                        'Photos': round(storage_data.get('PhotoUsage', 0) / (1024**3), 2),
                        'Media': round(storage_data.get('MediaUsage', 0) / (1024**3), 2),
                        'UDisk': 0.0,
                        'Others': round(storage_data.get('UserUsage', 0) / (1024**3), 2),
                        'Free': 0.0
                    }
                    return categories
            except Exception as e:
                error_msg = str(e)
                if 'MobileGestaltDeprecated' in error_msg or 'deprecated' in error_msg.lower():
                    logger.info("MobileGestalt is deprecated on this iOS version (>= 17.4)")
                else:
                    logger.warning(f"Could not get storage categories: {e}")
            
         
            storage_info = await self.get_storage_info()
            if storage_info:
                total = storage_info.get('total_capacity_gb', 0)
                used = storage_info.get('used_capacity_gb', 0)
                free = storage_info.get('free_capacity_gb', 0)
                
                
                categories = {
                    'System': round(total * 0.15, 2), 
                    'Apps': round(used * 0.4, 2),
                    'Photos': round(used * 0.2, 2),
                    'Media': round(used * 0.2, 2),
                    'UDisk': 0.0,
                    'Others': round(used * 0.2, 2),
                    'Free': free
                }
                return categories
            
            return {}
            
        except Exception as e:
            logger.error(f"Failed to get storage categories: {e}")
            return {}
    
    async def detect_jailbreak(self) -> Dict[str, Any]:
        """Detect if device is jailbroken"""
        try:
            try:
                from pymobiledevice3.services.afc import AFC2Service
                afc_service = AFC2Service(self.lockdown)
            except ImportError:
                try:
                    from pymobiledevice3.services.afc import AFCService
                    afc_service = AFCService(self.lockdown)
                except ImportError:
                    return {'jailbroken': False, 'method': 'Unknown'}
            
            if not self.lockdown:
                logger.error("Not connected to device")
                return {'jailbroken': False, 'method': 'Unknown'}
            jailbreak_indicators = {
                'jailbroken': False,
                'indicators': []
            }
            
          
            jailbreak_paths = [
                '/Applications/Cydia.app',
                '/Applications/blackra1n.app',
                '/Applications/FakeCarrier.app',
                '/Applications/Icy.app',
                '/Applications/IntelliScreen.app',
                '/Applications/MxTube.app',
                '/Applications/RockApp.app',
                '/Applications/SBSettings.app',
                '/Applications/WinterBoard.app',
                '/Library/MobileSubstrate',
                '/private/var/lib/apt',
                '/private/var/stash',
                '/private/var/tmp/cydia.log',
                '/System/Library/LaunchDaemons/com.ikey.bbot.plist',
                '/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist',
                '/bin/bash',
                '/bin/sh',
                '/etc/apt',
                '/usr/bin/sshd',
                '/usr/libexec/sftp-server',
                '/usr/sbin/sshd',
                '/var/cache/apt',
                '/var/lib/cydia',
                '/var/tmp/cydia.log'
            ]
            
            for path in jailbreak_paths:
                try:
                    await afc_service.file_exists(path)
                    jailbreak_indicators['indicators'].append(path)
                    jailbreak_indicators['jailbroken'] = True
                except:
                    pass
            
            await afc_service.close()
            
            jailbreak_indicators['method'] = 'Path Detection'
            logger.info(f"Jailbreak detection: {jailbreak_indicators}")
            return jailbreak_indicators
            
        except Exception as e:
            logger.error(f"Failed to detect jailbreak: {e}")
            return {'jailbroken': False, 'method': 'Error', 'indicators': []}
    
    def decode_production_date(self, serial_number: str) -> Dict[str, Any]:
        """Decode production date from Apple serial number"""
        try:
            if not serial_number or len(serial_number) < 10:
                return {'production_date': 'Unknown', 'year': 0, 'week': 0}
            
          
            year_map = {
                'C': 2010, 'D': 2011, 'F': 2012, 'G': 2013, 'H': 2014,
                'J': 2015, 'K': 2016, 'L': 2017, 'M': 2018, 'N': 2019,
                'P': 2020, 'Q': 2021, 'R': 2022, 'S': 2023, 'T': 2024,
                'V': 2025, 'W': 2026, 'X': 2027, 'Y': 2028, 'Z': 2029,
                'D': 2011, 'F': 2012, 'G': 2013, 'H': 2014, 'J': 2015,
                'K': 2016, 'L': 2017, 'M': 2018, 'N': 2019, 'P': 2020,
                'Q': 2021, 'R': 2022, 'S': 2023, 'T': 2024, 'V': 2025,
                'W': 2026, 'X': 2027, 'Y': 2028, 'Z': 2029
            }
            
            year = 0
            week = 0
            
        
            if len(serial_number) >= 12:
                year_char = serial_number[2].upper()
                year = year_map.get(year_char, 0)
                try:
                    week = int(serial_number[3:5])
                except:
                    week = 0
            
       
            if year == 0 and len(serial_number) >= 4:
                year_char = serial_number[3].upper()
                year = year_map.get(year_char, 0)
                try:
                    week = int(serial_number[4:6]) if len(serial_number) >= 6 else 0
                except:
                    week = 0
            
            if year > 0 and week > 0:
                from datetime import datetime, timedelta
                production_date = datetime(year, 1, 1) + timedelta(weeks=week-1)
                date_str = production_date.strftime("%m/%d/%Y")
            else:
                date_str = 'Unknown'
            
            return {
                'production_date': date_str,
                'year': year,
                'week': week
            }
            
        except Exception as e:
            logger.error(f"Failed to decode production date: {e}")
            return {'production_date': 'Unknown', 'year': 0, 'week': 0}
    
    def calculate_warranty_date(self, production_date_str: str) -> Dict[str, Any]:
        """Calculate warranty expiration date from production date"""
        try:
            if production_date_str == 'Unknown':
                return {'warranty_date': 'Unknown', 'warranty_status': 'Unknown'}
            
            from datetime import datetime, timedelta
            
            production_date = datetime.strptime(production_date_str, "%m/%d/%Y")
            warranty_date = production_date + timedelta(days=365)  
            
            today = datetime.now()
            warranty_expired = today > warranty_date
            
            warranty_status = 'Warranty Expired' if warranty_expired else 'Under Warranty'
            warranty_date_str = warranty_date.strftime("%m/%d/%Y")
            
            return {
                'warranty_date': warranty_date_str,
                'warranty_status': warranty_status
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate warranty date: {e}")
            return {'warranty_date': 'Unknown', 'warranty_status': 'Unknown'}
    
    def get_cpu_info(self, product_type: str) -> Dict[str, Any]:
        """Get CPU information based on device model"""
        try:
            cpu_map = {
             
                'iPhone8,1': {'cpu': 'Apple A9 Dual', 'cores': 2, 'architecture': 'ARMv8-A'},
                'iPhone8,2': {'cpu': 'Apple A9 Dual', 'cores': 2, 'architecture': 'ARMv8-A'},
                'iPhone8,4': {'cpu': 'Apple A9 Dual', 'cores': 2, 'architecture': 'ARMv8-A'},
                
          
                'iPhone9,1': {'cpu': 'Apple A10 Fusion', 'cores': 4, 'architecture': 'ARMv8-A'},
                'iPhone9,2': {'cpu': 'Apple A10 Fusion', 'cores': 4, 'architecture': 'ARMv8-A'},
                'iPhone9,3': {'cpu': 'Apple A10 Fusion', 'cores': 4, 'architecture': 'ARMv8-A'},
                'iPhone9,4': {'cpu': 'Apple A10 Fusion', 'cores': 4, 'architecture': 'ARMv8-A'},
                
               
                'iPhone10,1': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,2': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,3': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,4': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,5': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,6': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                
             
                'iPhone10,7': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                'iPhone10,8': {'cpu': 'Apple A11 Bionic', 'cores': 6, 'architecture': 'ARMv8-A'},
                
              
                'iPhone11,2': {'cpu': 'Apple A12 Bionic', 'cores': 6, 'architecture': 'ARMv8.2-A'},
                'iPhone11,4': {'cpu': 'Apple A12 Bionic', 'cores': 6, 'architecture': 'ARMv8.2-A'},
                'iPhone11,6': {'cpu': 'Apple A12 Bionic', 'cores': 6, 'architecture': 'ARMv8.2-A'},
                'iPhone11,8': {'cpu': 'Apple A12 Bionic', 'cores': 6, 'architecture': 'ARMv8.2-A'},
                
               
                'iPhone12,1': {'cpu': 'Apple A13 Bionic', 'cores': 6, 'architecture': 'ARMv8.3-A'},
                'iPhone12,3': {'cpu': 'Apple A13 Bionic', 'cores': 6, 'architecture': 'ARMv8.3-A'},
                'iPhone12,5': {'cpu': 'Apple A13 Bionic', 'cores': 6, 'architecture': 'ARMv8.3-A'},
                'iPhone12,8': {'cpu': 'Apple A13 Bionic', 'cores': 6, 'architecture': 'ARMv8.3-A'},
                
            
                'iPhone13,1': {'cpu': 'Apple A14 Bionic', 'cores': 6, 'architecture': 'ARMv8.4-A'},
                'iPhone13,2': {'cpu': 'Apple A14 Bionic', 'cores': 6, 'architecture': 'ARMv8.4-A'},
                'iPhone13,3': {'cpu': 'Apple A14 Bionic', 'cores': 6, 'architecture': 'ARMv8.4-A'},
                'iPhone13,4': {'cpu': 'Apple A14 Bionic', 'cores': 6, 'architecture': 'ARMv8.4-A'},
                
               
                'iPhone14,1': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,2': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,3': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,4': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,5': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,6': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,7': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                'iPhone14,8': {'cpu': 'Apple A15 Bionic', 'cores': 6, 'architecture': 'ARMv8.5-A'},
                
               
                'iPhone15,2': {'cpu': 'Apple A16 Bionic', 'cores': 6, 'architecture': 'ARMv8.6-A'},
                'iPhone15,3': {'cpu': 'Apple A16 Bionic', 'cores': 6, 'architecture': 'ARMv8.6-A'},
                'iPhone15,4': {'cpu': 'Apple A16 Bionic', 'cores': 6, 'architecture': 'ARMv8.6-A'},
                'iPhone15,5': {'cpu': 'Apple A16 Bionic', 'cores': 6, 'architecture': 'ARMv8.6-A'},
                
              
                'iPhone16,1': {'cpu': 'Apple A16 Bionic', 'cores': 6, 'architecture': 'ARMv8.6-A'},
                'iPhone16,2': {'cpu': 'Apple A17 Pro', 'cores': 6, 'architecture': 'ARMv9.2-A'},
                
              
                'iPhone17,1': {'cpu': 'Apple A18', 'cores': 6, 'architecture': 'ARMv9.3-A'},
                'iPhone17,2': {'cpu': 'Apple A18 Pro', 'cores': 6, 'architecture': 'ARMv9.3-A'},
                'iPhone17,3': {'cpu': 'Apple A18', 'cores': 6, 'architecture': 'ARMv9.3-A'},
                'iPhone17,4': {'cpu': 'Apple A18 Pro', 'cores': 6, 'architecture': 'ARMv9.3-A'},
            }
            
            return cpu_map.get(product_type, {'cpu': 'Unknown', 'cores': 0, 'architecture': 'Unknown'})
            
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {'cpu': 'Unknown', 'cores': 0, 'architecture': 'Unknown'}
    
    async def get_charging_status(self) -> Dict[str, Any]:
        """Get charging status including power source, wattage, and percentage"""
        try:
            if not self.diagnostics_service:
                logger.error("Diagnostics service not initialized")
                return {}
            
            charging_info = {}
            
            try:
                battery = await self.diagnostics_service.get_battery()
                if battery:
                 
                    battery_level = battery.get('BatteryCurrentCapacity', battery.get('CurrentCapacity', 0))
                    charging_info['battery_percentage'] = battery_level
                    
                   
                    is_charging = battery.get('BatteryIsCharging', False)
                    external_connected = battery.get('ExternalConnected', None)
                    
                   
                    if external_connected is not None and external_connected != 0:
                        is_charging = True
                    
                    charging_info['is_charging'] = is_charging
                    

                    if is_charging:
                        if external_connected == 1:
                            charging_info['power_source'] = 'AC Adapter'
                            charging_info['charging_type'] = 'Wall Charging'
                            charging_info['wattage'] = '10W+'
                        elif external_connected == 2:
                            charging_info['power_source'] = 'USB/PC'
                            charging_info['charging_type'] = 'PC Charging'
                            charging_info['wattage'] = '5W'
                        else:
                            charging_info['power_source'] = 'Unknown'
                            charging_info['charging_type'] = 'Charging'
                            charging_info['wattage'] = 'Unknown'
                    else:
                        charging_info['power_source'] = 'Battery'
                        charging_info['charging_type'] = 'Not Charging'
                        charging_info['wattage'] = '0W'
                    
            except Exception as e:
                logger.warning(f"Could not get battery info: {e}")
            
          
            try:
                diagnostics = await self.diagnostics_service.mobilegestalt([
                    'ChargerType',
                    'ExternalChargeCapability'
                ])
                if diagnostics and isinstance(diagnostics, dict) and 'Status' not in diagnostics:
                    charger_type = diagnostics.get('ChargerType', 'Unknown')
                    if charger_type:
                        charging_info['charger_type'] = charger_type
            except Exception as e:
                error_msg = str(e)
                if 'MobileGestaltDeprecated' in error_msg or 'deprecated' in error_msg.lower():
                    logger.info("MobileGestalt is deprecated on this iOS version (>= 17.4)")
                else:
                    logger.warning(f"Could not get charger type: {e}")
            
            logger.info(f"Charging status: {charging_info}")
            return charging_info
            
        except Exception as e:
            logger.error(f"Failed to get charging status: {e}")
            return {}
    
    async def get_charge_times(self) -> Dict[str, Any]:
        """Get charge times (cycle count is available from battery info)"""
        try:
            if not self.diagnostics_service:
                logger.error("Diagnostics service not initialized")
                return {'charge_times': 0}
            
            try:
                battery = await self.diagnostics_service.get_battery()
                if battery:
                    cycle_count = battery.get('CycleCount', battery.get('BatteryCycleCount', 0))
                    return {'charge_times': cycle_count}
            except Exception as e:
                logger.warning(f"Could not get charge times: {e}")
            
            return {'charge_times': 0}
            
        except Exception as e:
            logger.error(f"Failed to get charge times: {e}")
            return {'charge_times': 0}
    
    async def get_icloud_status(self) -> Dict[str, Any]:
        """Get iCloud and Apple ID Lock status"""
        try:
            if not self.lockdown:
                logger.error("Not connected to device")
                return {'icloud': 'Unknown', 'apple_id_lock': 'Unknown'}
            
            icloud_info = {
                'icloud': 'Unknown',
                'apple_id_lock': 'Unknown'
            }
            
        
            try:
         
                has_account = await self.lockdown.get_value("", "HasAccount")
                if has_account is not None:
                    icloud_info['icloud'] = 'On' if has_account else 'Off'
            except:
                pass
            
          
            if icloud_info['icloud'] == 'Unknown':
                try:
                  
                    activation_state = await self.lockdown.get_value("", "ActivationState")
                    if activation_state == 'Activated':
                        icloud_info['icloud'] = 'On'
                    elif activation_state == 'Unactivated':
                        icloud_info['icloud'] = 'Off'
                except:
                    pass
            
            try:
          
                activation_lock = await self.lockdown.get_value("", "ActivationLockEnabled")
                if activation_lock is not None:
                    icloud_info['apple_id_lock'] = 'On' if activation_lock else 'Off'
            except:
                pass
            
         
            if icloud_info['apple_id_lock'] == 'Unknown':
                try:
                    activation_state = await self.lockdown.get_value("", "ActivationState")
                    if activation_state == 'Unactivated':
                        icloud_info['apple_id_lock'] = 'On'
                    else:
                        icloud_info['apple_id_lock'] = 'Off'
                except:
                    pass
            
            logger.info(f"iCloud status: {icloud_info}")
            return icloud_info
            
        except Exception as e:
            logger.error(f"Failed to get iCloud status: {e}")
            return {'icloud': 'Unknown', 'apple_id_lock': 'Unknown'}
    
    def get_sales_region(self, region_code: str) -> str:
        """Get sales region from region code"""
        try:
            region_map = {
                'LL/A': 'USA',
                'ZA/A': 'USA',
                'B/A': 'UK/Ireland',
                'C/A': 'Canada',
                'DN/A': 'Germany',
                'TA/A': 'Italy',
                'FD/A': 'France',
                'J/A': 'Japan',
                'KH/A': 'Korea',
                'CH/A': 'China',
                'X/A': 'Australia/New Zealand',
                'B/A': 'Europe',
                'GR/A': 'Greece',
                'HB/A': 'Hungary',
                'PO/A': 'Portugal',
                'RO/A': 'Romania',
                'S/A': 'Spain',
                'TH/A': 'Thailand',
                'VN/A': 'Vietnam',
                'MY/A': 'Malaysia',
                'SG/A': 'Singapore',
                'PH/A': 'Philippines',
                'ID/A': 'Indonesia',
                'IN/A': 'India',
                'AE/A': 'Middle East',
                'BR/A': 'Brazil',
                'MX/A': 'Mexico',
                'CL/A': 'Chile',
                'CO/A': 'Colombia',
                'PE/A': 'Peru',
                'AR/A': 'Argentina',
                'ZA/A': 'South Africa',
                'NG/A': 'Nigeria',
                'EG/A': 'Egypt',
                'SA/A': 'Saudi Arabia',
                'RU/A': 'Russia',
                'TR/A': 'Turkey',
                'IL/A': 'Israel',
                'SE/A': 'Sweden',
                'NO/A': 'Norway',
                'DK/A': 'Denmark',
                'FI/A': 'Finland',
                'PL/A': 'Poland',
                'CZ/A': 'Czech Republic',
                'SK/A': 'Slovakia',
                'AT/A': 'Austria',
                'BE/A': 'Belgium',
                'NL/A': 'Netherlands',
                'LU/A': 'Luxembourg',
                'IE/A': 'Ireland',
                'CH/A': 'Switzerland',
                'HR/A': 'Croatia',
                'SI/A': 'Slovenia',
                'BG/A': 'Bulgaria',
                'RS/A': 'Serbia',
                'UA/A': 'Ukraine',
                'BY/A': 'Belarus',
                'KZ/A': 'Kazakhstan',
                'UZ/A': 'Uzbekistan',
                'AU/A': 'Azerbaijan',
                'GE/A': 'Georgia',
                'AM/A': 'Armenia',
                'AZ/A': 'Azerbaijan',
                'KG/A': 'Kyrgyzstan',
                'TJ/A': 'Tajikistan',
                'TM/A': 'Turkmenistan',
                'MN/A': 'Mongolia',
                'NP/A': 'Nepal',
                'LK/A': 'Sri Lanka',
                'MM/A': 'Myanmar',
                'KH/A': 'Cambodia',
                'LA/A': 'Laos',
                'BD/A': 'Bangladesh',
                'PK/A': 'Pakistan',
                'LK/A': 'Sri Lanka',
                'MV/A': 'Maldives',
                'BT/A': 'Bhutan',
                'NP/A': 'Nepal',
            }
            
            return region_map.get(region_code, 'Unknown')
            
        except Exception as e:
            logger.error(f"Failed to get sales region: {e}")
            return 'Unknown'
    
    def get_hard_disk_type(self, product_type: str) -> str:
        """Get hard disk type based on device model"""
        try:
        
            legacy_devices = [
                'iPhone8,1', 'iPhone8,2', 'iPhone8,4', 
                'iPhone7,1', 'iPhone7,2',  
                'iPhone6,1', 'iPhone6,2',  
            ]
            
            if product_type in legacy_devices:
                return 'MLC/TLC NAND'
            
            return 'NVMe SSD'
            
        except Exception as e:
            logger.error(f"Failed to get hard disk type: {e}")
            return 'Unknown'
    
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
