#!/usr/bin/env python3
"""
iOS Crash Analyzer System - Main Entry Point
Complete Python Implementation
Supports: Panic Analysis, System Health Analysis, IPS Extraction, Full Device Analysis
"""
                                                                
import asyncio
import sys
import argparse
import logging
from pathlib import Path
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich import print as rprint
from crash_analyzer_system.device_manager import DeviceManager
from crash_analyzer_system.database import DatabaseManager
from crash_analyzer_system.fault_codes import FAULT_CODES
from crash_analyzer_system.failure_detector import FailureDetector
from crash_analyzer_system.ips_parser import IPSParser, parse_ips_directory

project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

console = Console()
logger = logging.getLogger(__name__)


class iOSCrashAnalyzer:
    """Complete iOS crash analyzer with all analysis modes"""
    
    def __init__(self):
        self.device_manager = DeviceManager()
        self.db = DatabaseManager()
        self.failure_detector = FailureDetector()
        self.ips_parser = IPSParser()
        self.console = Console()
    async def get_latest_panic_report(self) -> dict:
        """Get the latest panic report from database"""
        try:
            crash_reports = self.db.get_crash_reports(limit=1)
            if crash_reports:
                return crash_reports[0]
            return {}
        except Exception as e:
            self.console.print(f"[red]Error getting panic report: {e}[/red]")
            return {}
    
    async def _display_iphone_info(self):
        """Display iPhone device information in a formatted table"""
        try:
            
            devices = await self.device_manager.list_devices()
            if not devices:
                return
            
            if not await self.device_manager.connect_device(devices[0]['udid']):
                return
            
        
            info = await self.device_manager.get_iphone_full_info()
            if not info:
                return
            
        
            from rich.table import Table
            main_table = Table(show_header=True, header_style="bold cyan", border_style="cyan", pad_edge=False, expand=True)
            main_table.add_column("Property", style="white", width=20)
            main_table.add_column("Value", style="cyan")
            
          
            device_name = info.get('device_name', 'Unknown')
            product_type = info.get('product_type', 'Unknown')
            main_table.add_row("📱 Device", f"[bold]{device_name}[/bold] ([white]{product_type}[/white])")
            
         
            ios_version = info.get('product_version', 'Unknown')
            build_version = info.get('build_version', 'Unknown')
            main_table.add_row("📱 iOS Version", f"[cyan]{ios_version}[/cyan] ([white]{build_version}[/white])")
            
      
            hardware_model = info.get('hardware_model', 'Unknown')
            device_class = info.get('device_class', 'Unknown')
            main_table.add_row("🔧 Hardware", f"[cyan]{hardware_model}[/cyan] ([white]{device_class}[/white])")
            
          
            serial = info.get('serial_number', 'Unknown')
            main_table.add_row("🔢 Serial Number", f"[cyan]{serial}[/cyan]")
            
          
            imei = info.get('imei', 'Unknown')
            if imei != 'Unknown':
                main_table.add_row("📞 IMEI", f"[cyan]{imei}[/cyan]")
            
         
            ecid = info.get('ecid', 'Unknown')
            if ecid != 'Unknown':
                main_table.add_row("🆔 ECID", f"[cyan]{ecid}[/cyan]")
            
    
            udid = info.get('udid', 'Unknown')
            if udid != 'Unknown' and len(udid) > 16:
                display_udid = udid[:8] + "..." + udid[-8:]
                main_table.add_row("🆔 UDID", f"[cyan]{display_udid}[/cyan]")
            else:
                main_table.add_row("🆔 UDID", f"[cyan]{udid}[/cyan]")
            
           
            activated = info.get('activated', 'Unknown')
            activated_color = "green" if activated == "Activated" else "yellow"
            main_table.add_row("✅ Activated", f"[{activated_color}]{activated}[/{activated_color}]")
            
        
            battery = info.get('battery')
            if battery:
                try:
                    cycle_count = battery.get('CycleCount', battery.get('CycleCount', 'Unknown'))
                    design_capacity = battery.get('DesignCapacity', battery.get('NominalChargeCapacity', 'Unknown'))
                    full_charge_capacity = battery.get('FullChargeCapacity', battery.get('MaximumChargeCapacity', 'Unknown'))
                    battery_health = battery.get('MaximumFCC', battery.get('MaximumChargeCapacity', 'Unknown'))
                    
                    main_table.add_row("🔋 Battery Cycles", f"[yellow]{cycle_count}[/yellow]")
                    
                   
                    health_displayed = False
                    if battery_health != 'Unknown' and design_capacity != 'Unknown':
                        try:
                            health_pct = (int(battery_health) / int(design_capacity)) * 100
                            main_table.add_row("🔋 Battery Health", f"[green]{health_pct:.1f}%[/green]")
                            health_displayed = True
                        except:
                            pass
                    
                  
                    if not health_displayed and 'BatteryHealth' in battery:
                        try:
                            health_val = battery['BatteryHealth']
                            if isinstance(health_val, (int, float)):
                                main_table.add_row("🔋 Battery Health", f"[green]{health_val}%[/green]")
                        except:
                            pass
                    
                
                    if full_charge_capacity != 'Unknown' and design_capacity != 'Unknown':
                        try:
                            capacity_pct = (int(full_charge_capacity) / int(design_capacity)) * 100
                            main_table.add_row("🔋 Max Capacity", f"[cyan]{capacity_pct:.1f}%[/cyan]")
                        except:
                            pass
                except Exception as e:
                    logger.warning(f"Could not parse battery info: {e}")
            
          
            gestalt = info.get('mobilegestalt')
            if gestalt:
                model_number = gestalt.get('ModelNumber', 'Unknown')
                if model_number != 'Unknown':
                    main_table.add_row("📦 Model Number", f"[cyan]{model_number}[/cyan]")
                
                region = gestalt.get('RegionCode', 'Unknown')
                if region != 'Unknown':
                    main_table.add_row("🌏 Region", f"[cyan]{region}[/cyan]")
                
                color = gestalt.get('DeviceColorString', gestalt.get('DeviceColor', 'Unknown'))
                if color != 'Unknown':
                    main_table.add_row("🎨 Color", f"[cyan]{color}[/cyan]")
            else:
             
                try:
                    region_info = info.get('region_info', 'Unknown')
                    if region_info != 'Unknown':
                        main_table.add_row("🌏 Region", f"[cyan]{region_info}[/cyan]")
                except:
                    pass
                
                try:
                    model_num = info.get('model_number', 'Unknown')
                    if model_num != 'Unknown':
                        main_table.add_row("📦 Model Number", f"[cyan]{model_num}[/cyan]")
                except:
                    pass
            
          
            self.console.print()
            self.console.print(Panel(main_table, title="📱 iPhone Information", border_style="cyan", padding=(1, 2)))
            
        except Exception as e:
            logger.error(f"Failed to display iPhone info: {e}")
    
    def extract_panic_data(self, crash_report: dict) -> dict:
        """Extract relevant panic data from crash report"""
        panic_data = {
            'exception_type': crash_report.get('exception_type', 'Unknown'),
            'exception_codes': crash_report.get('exception_codes', 'Unknown'),
            'termination_reason': crash_report.get('termination_reason', 'Unknown'),
            'triggered_by_thread': crash_report.get('triggered_by_thread', 'Unknown'),
            'fault_code': crash_report.get('fault_code', 'Unknown')
        }
        return panic_data
    
    def extract_memory_errors(self, crash_report: dict) -> dict:
        """Extract memory error information"""
        memory_errors = {
            'total_errors': 0,
            'error_types': []
        }
        
        content = str(crash_report)
        memory_keywords = ['out of memory', 'memory corruption', 'segmentation fault', 'memory access', 'heap corruption']
        
        for keyword in memory_keywords:
            if keyword.lower() in content.lower():
                memory_errors['error_types'].append(keyword)
                memory_errors['total_errors'] += 1
        
        return memory_errors
    
    async def get_all_crash_reports(self) -> list:
        """Get all crash reports from database"""
        try:
            crash_reports = self.db.get_crash_reports(limit=1000)
            return crash_reports
        except Exception as e:
            self.console.print(f"[red]Error getting crash reports: {e}[/red]")
            return []
    
    def analyze_system_activity(self, crash_reports: list) -> dict:
        """Analyze system activity based on crash reports"""
        if not crash_reports:
            return {
                'total_crashes': 0,
                'most_frequent_exception': 'None',
                'most_affected_process': 'None',
                'top_processes': [],
                'exception_distribution': {},
                'crash_trends': 'No crash data available'
            }
        
        exceptions = [crash.get('exception_type', 'Unknown') for crash in crash_reports]
        exception_counter = Counter(exceptions)
        most_frequent_exception = exception_counter.most_common(1)[0][0] if exception_counter else 'None'
        
        processes = []
        for crash in crash_reports:
            if 'processes' in crash and crash['processes']:
                for process in crash['processes']:
                    if isinstance(process, dict):
                        processes.append(process.get('name', 'Unknown'))
        
        process_counter = Counter(processes)
        most_affected_process = process_counter.most_common(1)[0][0] if process_counter else 'None'
        top_processes = process_counter.most_common(5)
        exception_distribution = dict(exception_counter.most_common(10))
        
        total_crashes = len(crash_reports)
        if total_crashes > 10:
            recent_crashes = crash_reports[:10]
            old_crashes = crash_reports[10:20] if len(crash_reports) > 20 else []
            
            recent_exceptions = Counter([crash.get('exception_type', 'Unknown') for crash in recent_crashes])
            old_exceptions = Counter([crash.get('exception_type', 'Unknown') for crash in old_crashes])
            
            if recent_exceptions != old_exceptions:
                crash_trends = "Recent crash patterns differ from historical data - potential new issues"
            else:
                crash_trends = "Crash patterns consistent with historical data"
        else:
            crash_trends = "Insufficient data for trend analysis"
        
        return {
            'total_crashes': total_crashes,
            'most_frequent_exception': most_frequent_exception,
            'most_affected_process': most_affected_process,
            'top_processes': [(name, count) for name, count in top_processes],
            'exception_distribution': exception_distribution,
            'crash_trends': crash_trends
        }
    
    async def extract_and_analyze_ips(self, output_dir: str = "ips_reports") -> bool:
        """Extract .ips files from device and analyze them"""
        self.console.print(Panel(
            Text("iOS IPS File Extractor & Analyzer", style="bold cyan"),
            title="IPS Analyzer",
            border_style="cyan"
        ))
        
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗ No iOS devices found. Please connect your device.[/red]")
            return False
        
        device = devices[0]
        self.console.print(f"[green]✓[/green] Device Found: [cyan]{device['udid']}[/cyan]")
        
        self.console.print("[blue]🔌 Connecting to Device...[/blue]")
        if not await self.device_manager.connect_device(device['udid']):
            self.console.print("[red]✗ Failed to connect to device[/red]")
            return False
        self.console.print("[green]✓ Connected successfully[/green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Extracting .ips Files from Device...[/cyan]", total=None)
            ips_files = await self.device_manager.extract_ips_files(output_dir)
            progress.update(task, completed=True)
        
        if not ips_files:
            self.console.print("[yellow]⚠ No .ips files found on device[/yellow]")
            return False
        
        self.console.print(f"[green]✓ Successfully extracted {len(ips_files)} .ips files[/green]")
        self.console.print(f"   Output directory: [cyan]{output_dir}[/cyan]")
        
        self.console.print("[blue]🔍 Parsing and Analyzing .ips Files...[/blue]")
        ips_reports = parse_ips_directory(output_dir)
        
        if not ips_reports:
            self.console.print("[red]✗ Failed to parse .ips files[/red]")
            return False
        
        self.console.print(f"[green]✓ Successfully parsed {len(ips_reports)} .ips files[/green]")
        
        table = Table(title="IPS Crash Report Summary")
        table.add_column("#", style="cyan", width=4)
        table.add_column("File", style="green")
        table.add_column("App", style="yellow")
        table.add_column("Version", style="blue")
        table.add_column("Exception", style="red")
        
        for i, report in enumerate(ips_reports, 1):
            table.add_row(
                str(i),
                report.get('file_path', 'Unknown')[:30],
                f"{report.get('app_name', 'Unknown')} ({report.get('bundle_id', 'Unknown')})",
                report.get('app_version', 'Unknown'),
                f"{report.get('exception_type', 'Unknown')} - {report.get('exception_codes', 'Unknown')}"
            )
        
        self.console.print(table)
        
        self.console.print("[blue]🔍 Failure Detection Analysis...[/blue]")
        pattern_analysis = self.failure_detector.analyze_crash_patterns(ips_reports)
        
        health_color = "green" if pattern_analysis['system_health'] == 'healthy' else "yellow" if pattern_analysis['system_health'] == 'degraded' else "red"
        self.console.print(f"   System Health: [{health_color}]{pattern_analysis['system_health'].upper()}[/{health_color}]")
        self.console.print(f"   Crash Trend: [cyan]{pattern_analysis['trend'].upper()}[/cyan]")
        
        if pattern_analysis['most_unstable_processes']:
            self.console.print("   Unstable Processes:")
            for process in pattern_analysis['most_unstable_processes'][:3]:
                self.console.print(f"     - [yellow]{process['name']}[/yellow]: {process['count']} crashes")
        
        self.console.print(Panel(
            Text("IPS Analysis Complete", style="bold green"),
            title="Status",
            border_style="green"
        ))
        
        return True
    
    async def run_panic_analysis(self):
        """Run panic log analysis"""
        self.console.print()
        self.console.print(Panel(
            Text("🔴 iOS Panic Log Analyzer", style="bold red"),
            title="Panic Analysis",
            border_style="red",
            padding=(1, 2)
        ))
        

        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold red]▶[/bold red] [bold white]Panic Report Analysis[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[yellow]⚠[/yellow] No iOS devices found. Using local database data.")
            device_info = {
                'udid': 'local',
                'device_name': 'Local Database',
                'os_version': 'Unknown',
                'product_type': 'Unknown',
                'hardware_model': 'Unknown'
            }
        else:
            device = devices[0]
            device_info = {
                'udid': device['udid'],
                'device_name': 'iOS Device',
                'os_version': 'Unknown',
                'product_type': 'Unknown',
                'hardware_model': 'Unknown'
            }
            self.console.print(f"   [green]●[/green] UDID: [cyan]{device['udid']}[/cyan]")
            self.console.print(f"   [green]●[/green] Connection: [cyan]{device['connection_type']}[/cyan]")
            
            if await self.device_manager.connect_device(device['udid']):
                diagnostics = await self.device_manager.get_device_diagnostics()
                if diagnostics:
                    self.console.print(f"   [green]●[/green] Diagnostics collected")
        
        self.console.print()
        self.console.print("[bold red]▶[/bold red] [bold white]Extracting Panic Reports[/bold white]")
        panic_report = await self.get_latest_panic_report()
        
        if not panic_report:
            self.console.print("[yellow]⚠[/yellow] No panic reports found in database.")
            self.console.print("   Use 'python run.py --analyze' to extract crash reports first.")
            return
        
        self.console.print(f"   [green]●[/green] Found panic report")
        
        self.console.print()
        self.console.print("[bold red]▶[/bold red] [bold white]Analyzing Panic Reports[/bold white]")
        self.console.print(f"   [cyan]Analyzing:[/cyan] [white]latest panic report[/white]")
            
        panic_data = self.extract_panic_data(panic_report)
            
        if panic_data:
            self.console.print(f"   [red]●[/red] Panic Detected")
            self.console.print(f"   [white]Exception:[/white] [cyan]{panic_data.get('exception_type', 'Unknown')}[/cyan]")
            self.console.print(f"   [white]Codes:[/white] [yellow]{panic_data.get('exception_codes', 'Unknown')}[/yellow]")
                
            memory_errors = self.extract_memory_errors(panic_report)
            self.console.print(f"   [white]Memory Errors:[/white] [red]{memory_errors['total_errors']}[/red]")
        else:
            self.console.print(f"   [green]●[/green] No panic detected")
        
        self.console.print()
        self.console.print("[bold red]▶[/bold red] [bold white]Failure Detection Analysis...[/bold white]")
        failure_analysis = self.failure_detector.analyze_panic_log(panic_report)
        self.console.print(f"[green]✓ Failure Analysis Complete[/green]")
        
        risk_color = "red" if failure_analysis['risk_level'] == 'critical' else "yellow" if failure_analysis['risk_level'] == 'high' else "green"
        self.console.print(f"   Risk Level: [{risk_color}]{failure_analysis['risk_level'].upper()}[/{risk_color}]")
        self.console.print(f"   Failure Type: [cyan]{failure_analysis['failure_type']}[/cyan]")
        self.console.print(f"   Is Critical: [red]{'YES' if failure_analysis['is_critical'] else 'NO'}[/red]")
        if failure_analysis['memory_errors']:
            self.console.print(f"   Memory Errors: [yellow]{', '.join(failure_analysis['memory_errors'])}[/yellow]")
        
        self.console.print("[blue]⚙ Step 4: Hardware Failure Detection...[/blue]")
        hardware_analysis = self.failure_detector.detect_hardware_failure(panic_report)
        self.console.print(f"[green]✓ Hardware Analysis Complete[/green]")
        self.console.print(f"   Hardware Related: [red]{'YES' if hardware_analysis['is_hardware_related'] else 'NO'}[/red]")
        if hardware_analysis['suspected_components']:
            self.console.print(f"   Suspected Components: [yellow]{', '.join(hardware_analysis['suspected_components'])}[/yellow]")
        self.console.print(f"   Confidence: [cyan]{hardware_analysis['confidence'].upper()}[/cyan]")
        
        self.console.print("[blue]💾 Step 5: Analyzing Memory Errors...[/blue]")
        memory_errors = self.extract_memory_errors(panic_report)
        self.console.print(f"[green]✓ Memory Analysis Complete[/green]")
        self.console.print(f"   Total Errors: [cyan]{memory_errors['total_errors']}[/cyan]")
        self.console.print(f"   Error Types: [yellow]{', '.join(memory_errors['error_types']) if memory_errors['error_types'] else 'None'}[/yellow]")
        
        self.console.print(Panel(
            Text("Analysis Complete", style="bold green"),
            title="Status",
            border_style="green"
        ))
    
    async def run_system_health_analysis(self):
        """Run system health analysis"""
        self.console.print()
        self.console.print(Panel(
            Text("📊 iOS System Health Analysis", style="bold magenta"),
            title="Analysis",
            border_style="magenta",
            padding=(1, 2)
        ))
        
        
        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Crash Report Statistics[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[yellow]⚠[/yellow] No iOS devices found. Using local database data.")
            device_info = {
                'udid': 'local',
                'device_name': 'Local Database',
                'os_version': 'Unknown',
                'product_type': 'Unknown',
                'hardware_model': 'Unknown'
            }
        else:
            device = devices[0]
            device_info = {
                'udid': device['udid'],
                'device_name': 'iOS Device',
                'os_version': 'Unknown',
                'product_type': 'Unknown',
                'hardware_model': 'Unknown'
            }
            self.console.print(f"   [green]●[/green] UDID: [cyan]{device['udid']}[/cyan]")
            self.console.print(f"   [green]●[/green] Connection: [cyan]{device['connection_type']}[/cyan]")
            
            if await self.device_manager.connect_device(device['udid']):
                diagnostics = await self.device_manager.get_device_diagnostics()
                if diagnostics:
                    self.console.print(f"   [green]●[/green] Diagnostics collected")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Crash Report Statistics[/bold white]")
        crash_reports = await self.get_all_crash_reports()
        
        if not crash_reports:
            self.console.print("[yellow]⚠[/yellow] No crash reports found in database.")
            return
        
        panic_reports = [r for r in crash_reports if r.get('is_panic', 0) == 1]
        other_reports = [r for r in crash_reports if r.get('is_panic', 0) == 0]
        
        self.console.print(f"   [bold white]Total:[/bold white] [cyan]{len(crash_reports)}[/cyan]")
        self.console.print(f"   [bold white]Panic Logs:[/bold white] [red]{len(panic_reports)}[/red]")
        self.console.print(f"   [bold white]Other Logs:[/bold white] [cyan]{len(other_reports)}[/cyan]")
        
        if len(other_reports) > 0:
            self.console.print(f"   [bold white]Types:[/bold white] [yellow]{', '.join(set([r.get('file_type', 'unknown') for r in other_reports]))}[/yellow]")
        
        pattern_analysis = self.failure_detector.analyze_crash_patterns(panic_reports if panic_reports else crash_reports)
        
        health_color = "green" if pattern_analysis['system_health'] == 'healthy' else "yellow" if pattern_analysis['system_health'] == 'degraded' else "red"
        self.console.print(f"   [bold white]Health Status:[/bold white] [{health_color}]{pattern_analysis['system_health'].upper()}[/{health_color}]")
        self.console.print(f"   [bold white]Trend:[/bold white] [cyan]{pattern_analysis['trend'].upper()}[/cyan]")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Process Stability[/bold white]")
        
        table = Table(show_header=True, header_style="bold magenta", border_style="magenta", pad_edge=False)
        table.add_column("Status", width=10, style="bold")
        table.add_column("Process", style="cyan")
        table.add_column("Crashes", justify="right", style="yellow")
        table.add_column("State", style="green")
        
        for process in pattern_analysis['most_unstable_processes'][:5]:
            status_icon = "🔴" if process['status'] == 'critical' else "🟡" if process['status'] == 'unstable' else "🟢"
            table.add_row(f"{status_icon} {process['status']}", process['name'], str(process['count']), process['status'])
        
        self.console.print(table)
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Exception Distribution[/bold white]")
        
        exception_table = Table(show_header=True, header_style="bold magenta", border_style="magenta", pad_edge=False)
        exception_table.add_column("Exception", style="cyan")
        exception_table.add_column("Count", justify="right", style="yellow")
        
        for exception, count in pattern_analysis['most_common_exceptions'][:5]:
            exception_table.add_row(exception, str(count))
        
        self.console.print(exception_table)
        
        if pattern_analysis['memory_error_summary']:
            self.console.print()
            self.console.print("[bold magenta]▶[/bold magenta] [bold white]Memory Error Summary[/bold white]")
            for error, count in pattern_analysis['memory_error_summary'].items():
                self.console.print(f"   [yellow]•[/yellow] [cyan]{error}[/cyan]: [white]{count}[/white] occurrences")
        
       
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Generating Failure Report[/bold white]")
        failure_report = self.failure_detector.generate_failure_report(crash_reports)
        
      
        import json
        from datetime import datetime
        from pathlib import Path
        
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"failure_report_{timestamp}.json"
        
        report_data = {
            "timestamp": timestamp,
            "device_udid": device_info.get('udid', 'Unknown'),
            "device_name": device_info.get('device_name', 'Unknown'),
            "total_crashes": pattern_analysis.get('total_crashes', 0),
            "panic_logs": pattern_analysis.get('panic_count', 0),
            "other_logs": pattern_analysis.get('other_count', 0),
            "system_health": pattern_analysis.get('health_status', 'Unknown'),
            "crash_trend": pattern_analysis.get('trend', 'Unknown'),
            "failure_report_text": failure_report
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        self.console.print(f"   [green]●[/green] Report saved: [cyan]{report_file}[/cyan]")
        
        self.console.print()
        self.console.print(Panel(
            Text("✓ Analysis Complete", style="bold green"),
            title="Status",
            border_style="green",
            padding=(1, 2)
        ))
    
    async def run_full_analysis(self, udid: str = None):
        """Run full device analysis - extract and analyze crash reports"""
        self.console.print()
        self.console.print(Panel(
            Text("🔬 iOS Full Device Analysis", style="bold magenta"),
            title="Full Analysis",
            border_style="magenta",
            padding=(1, 2)
        ))
        
 
        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Device Information[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗[/red] No iOS devices found")
            return
        
        target_udid = udid if udid else devices[0]['udid']
        device = next((d for d in devices if d['udid'] == target_udid), devices[0])
        
        self.console.print(f"   [green]●[/green] UDID: [cyan]{device['udid']}[/cyan]")
        self.console.print(f"   [green]●[/green] Connection: [cyan]{device['connection_type']}[/cyan]")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Establishing Connection[/bold white]")
        if not await self.device_manager.connect_device(target_udid):
            self.console.print("[red]✗[/red] Connection failed")
            return
        self.console.print(f"   [green]●[/green] Connected")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Collecting Diagnostics[/bold white]")
        try:
            diagnostics = await self.device_manager.get_diagnostics()
            if diagnostics:
                self.console.print(f"   [green]●[/green] Collected [cyan]{len(diagnostics)}[/cyan] entries")
            else:
                self.console.print("[yellow]⚠[/yellow] No diagnostics available")
        except Exception as e:
            self.console.print(f"[yellow]⚠[/yellow] Diagnostics failed: {e}")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Listing Crash Reports[/bold white]")
        crash_reports = await self.device_manager.get_crash_reports()
        
        if not crash_reports:
            self.console.print("[yellow]⚠[/yellow] No crash reports found")
            try:
                await self.device_manager.disconnect()
            except:
                pass
            return
        
        self.console.print(f"   [green]●[/green] Found [cyan]{len(crash_reports)}[/cyan] reports")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Downloading Crash Reports[/bold white]")
        downloaded = 0
        
        if not await self.device_manager.connect_device(target_udid):
            self.console.print("[yellow]⚠[/yellow] Re-establishing connection...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Downloading...[/cyan]", total=len(crash_reports[:10]))
            
            for report in crash_reports[:10]:
                report_name = report if isinstance(report, str) else report.get('name', str(report))
                try:
                    success = await self.device_manager.download_crash_report(report_name, f"data/{report_name}")
                    if success:
                        downloaded += 1
                        self.console.print(f"   [green]●[/green] [cyan]{report_name}[/cyan]")
                    else:
                        self.console.print(f"   [red]✗[/red] [yellow]{report_name}[/yellow]")
                except Exception as e:
                    self.console.print(f"   [red]✗[/red] [yellow]{report_name}[/yellow]: {e}")
                
                progress.update(task, advance=1)
        
        self.console.print(f"   [green]●[/green] Downloaded [cyan]{downloaded}/{len(crash_reports[:10])}[/cyan]")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Processing Crash Reports[/bold white]")
        from crash_analyzer_system.parser import CrashReportParser
        parser = CrashReportParser()
        processed = 0
        
        data_dir = Path("data")
        if data_dir.exists():
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            ) as progress:
                files = list(data_dir.rglob("*"))
                files = [f for f in files if f.is_file() and not f.name.startswith('.') and f.suffix != '.db']
                task = progress.add_task("[cyan]Processing...[/cyan]", total=len(files))
                
                for file_path in files:
                    try:
                        parsed_data = parser.parse_file(str(file_path))
                        if parsed_data:
                            if 'device_udid' not in parsed_data:
                                parsed_data['device_udid'] = 'local'
                            self.db.insert_crash_report(parsed_data)
                            processed += 1
                            self.console.print(f"   [green]●[/green] [cyan]{file_path.name}[/cyan]")
                    except Exception as e:
                        self.console.print(f"   [red]✗[/red] [yellow]{file_path.name}[/yellow]: {e}")
                    
                    progress.update(task, advance=1)
        
        self.console.print(f"   [green]●[/green] Processed [cyan]{processed}[/cyan] reports")
        
        self.console.print()
        self.console.print("[bold magenta]▶[/bold magenta] [bold white]Running System Health Analysis[/bold white]")
        await self.run_system_health_analysis()
        
        try:
            await self.device_manager.disconnect()
        except Exception as e:
            self.console.print(f"[yellow]⚠[/yellow] Disconnect warning: {e}")
    
    async def run_syslog_streaming(self):
        """Stream syslog from device in real-time"""
        self.console.print()
        self.console.print(Panel(
            Text("📡 iOS Syslog Streaming", style="bold blue"),
            title="Syslog",
            border_style="blue",
            padding=(1, 2)
        ))

        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold blue]▶[/bold blue] [bold white]Connecting to Device[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗[/red] No iOS devices found")
            return
        
        device = devices[0]
        self.console.print(f"   [green]●[/green] Device: [cyan]{device['udid']}[/cyan]")
        
        self.console.print()
        self.console.print("[bold blue]▶[/bold blue] [bold white]Establishing Connection[/bold white]")
        if not await self.device_manager.connect_device(device['udid']):
            self.console.print("[red]✗[/red] Connection failed")
            return
        self.console.print(f"   [green]●[/green] Connected")
        
        self.console.print()
        self.console.print("[bold blue]▶[/bold blue] [bold white]Streaming Syslog[/bold white]")
        self.console.print("[yellow]   Press Ctrl+C to stop[/yellow]")
        
        try:
            async for syslog_line in self.device_manager.stream_syslog():
                self.console.print(syslog_line)
        except KeyboardInterrupt:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Stopped by user")
        except asyncio.CancelledError:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Cancelled")
        except Exception as e:
            self.console.print(f"[red]✗[/red] Error: {e}")
        finally:
            try:
                await self.device_manager.disconnect()
            except:
                pass
    
    async def run_diagnostics_analysis(self):
        """Get device diagnostics information"""
        self.console.print()
        self.console.print(Panel(
            Text("🔧 iOS Device Diagnostics", style="bold yellow"),
            title="Diagnostics",
            border_style="yellow",
            padding=(1, 2)
        ))
        
     
        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold yellow]▶[/bold yellow] [bold white]Additional Diagnostics[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗[/red] No iOS devices found")
            return
        
        device = devices[0]
        self.console.print(f"   [green]●[/green] Device: [cyan]{device['udid']}[/cyan]")
        
        self.console.print()
        self.console.print("[bold yellow]▶[/bold yellow] [bold white]Establishing Connection[/bold white]")
        if not await self.device_manager.connect_device(device['udid']):
            self.console.print("[red]✗[/red] Connection failed")
            return
        self.console.print(f"   [green]●[/green] Connected")
        
        self.console.print()
        self.console.print("[bold yellow]▶[/bold yellow] [bold white]Collecting Diagnostics[/bold white]")
        try:
            diagnostics = await self.device_manager.get_diagnostics()
            
            if diagnostics:
                self.console.print(f"   [green]●[/green] Collected [cyan]{len(diagnostics)}[/cyan] entries")
                
                from rich.table import Table
                diag_table = Table(title="Device Diagnostics", show_header=True, header_style="bold yellow", border_style="yellow", pad_edge=False)
                diag_table.add_column("Key", style="cyan")
                diag_table.add_column("Value", style="green")
                
                for key, value in list(diagnostics.items())[:20]:
                    diag_table.add_row(str(key), str(value))
                
                self.console.print(diag_table)
            else:
                self.console.print("[yellow]⚠[/yellow] No diagnostics data available")
        except Exception as e:
            self.console.print(f"[red]✗[/red] Failed: {e}")
        finally:
            try:
                await self.device_manager.disconnect()
            except:
                pass
    
    async def run_crash_watch(self, process_name: str = None):
        """Watch for new crash reports in real-time"""
        self.console.print()
        self.console.print(Panel(
            Text("👁️ iOS Crash Report Watcher", style="bold cyan"),
            title="Crash Watch",
            border_style="cyan",
            padding=(1, 2)
        ))
        
       
        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold cyan]▶[/bold cyan] [bold white]Crash Monitoring[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗[/red] No iOS devices found")
            return
        
        device = devices[0]
        self.console.print(f"   [green]●[/green] Device: [cyan]{device['udid']}[/cyan]")
        
        self.console.print()
        self.console.print("[bold cyan]▶[/bold cyan] [bold white]Establishing Connection[/bold white]")
        if not await self.device_manager.connect_device(device['udid']):
            self.console.print("[red]✗[/red] Connection failed")
            return
        self.console.print(f"   [green]●[/green] Connected")
        
        if process_name:
            self.console.print()
            self.console.print(f"[bold cyan]▶[/bold cyan] [bold white]Watching process: [cyan]{process_name}[/cyan][/bold white]")
        else:
            self.console.print()
            self.console.print("[bold cyan]▶[/bold cyan] [bold white]Watching all crash reports[/bold white]")
        self.console.print("[yellow]   Press Ctrl+C to stop[/yellow]")
        
        try:
            async for crash_report in self.device_manager.watch_crash_reports(process_name=process_name, raw=False):
                self.console.print()
                self.console.print(f"[red]🔴 New crash:[/red] [cyan]{crash_report.name}[/cyan]")
                self.console.print(f"   [white]Exception:[/white] [yellow]{crash_report.exception_type}[/yellow]")
                self.console.print(f"   [white]Process:[/white] [cyan]{crash_report.process_name}[/cyan]")
        except KeyboardInterrupt:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Stopped by user")
        except asyncio.CancelledError:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Cancelled")
        except Exception as e:
            self.console.print(f"[red]✗[/red] Error: {e}")
        finally:
            try:
                await self.device_manager.disconnect()
            except:
                pass
    
    async def run_sysdiagnose_collection(self, output_path: str):
        """Collect sysdiagnose archive from device"""
        self.console.print()
        self.console.print(Panel(
            Text("📦 iOS Sysdiagnose Collection", style="bold green"),
            title="Sysdiagnose",
            border_style="green",
            padding=(1, 2)
        ))
        
      
        await self._display_iphone_info()
        
        self.console.print()
        self.console.print("[bold green]▶[/bold green] [bold white]Connecting to Device[/bold white]")
        devices = await self.device_manager.list_devices()
        
        if not devices:
            self.console.print("[red]✗[/red] No iOS devices found")
            return
        
        device = devices[0]
        self.console.print(f"   [green]●[/green] Device: [cyan]{device['udid']}[/cyan]")
        
        self.console.print()
        self.console.print("[bold green]▶[/bold green] [bold white]Establishing Connection[/bold white]")
        if not await self.device_manager.connect_device(device['udid']):
            self.console.print("[red]✗[/red] Connection failed")
            return
        self.console.print(f"   [green]●[/green] Connected")
        
        self.console.print()
        self.console.print(f"[bold green]▶[/bold green] [bold white]Collecting to {output_path}[/bold white]")
        self.console.print("[yellow]   This may take several minutes...[/yellow]")
        
        try:
            success = await self.device_manager.get_sysdiagnose(output_path, erase=False, timeout=600)
            
            if success:
                self.console.print(f"   [green]●[/green] Saved to: [cyan]{output_path}[/cyan]")
            else:
                self.console.print("[red]✗[/red] Collection failed")
        except KeyboardInterrupt:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Cancelled by user")
        except asyncio.TimeoutError:
            self.console.print("[red]✗[/red] Timeout (>10 minutes)")
        except asyncio.CancelledError:
            self.console.print()
            self.console.print("[yellow]⚠[/yellow] Cancelled")
        except Exception as e:
            self.console.print(f"[red]✗[/red] Error: {e}")
            import traceback
            self.console.print(f"[red]Details: {traceback.format_exc()}[/red]")
        finally:
            try:
                await self.device_manager.disconnect()
            except:
                pass


def print_usage():
    """Print usage information"""
    console = Console()
    

    console.print()
    console.print(r"[bold magenta]         .-. .-')    _ (`-.            .-') _    [/bold magenta]")
    console.print(r"[bold magenta]         \  ( OO )  ( (OO  )          (  OO) )   [/bold magenta]")
    console.print(r"[bold magenta]  ,-.-') ,--. ,--. _.`     \ ,--.     /     '._  [/bold magenta]")
    console.print(r"[bold magenta]  |  |OO)|  .'   /(__...--'' |  |.-') |'--...__) [/bold magenta]")
    console.print(r"[bold magenta]  |  |  \|      /, |  /  | | |  | OO )'--.  .--' [/bold magenta]")
    console.print(r"[bold magenta]  |  |(_/|     ' _)|  |_.' | |  |`-' |   |  |    [/bold magenta]")
    console.print(r"[bold magenta] ,|  |_.'|  .   \  |  .___.'(|  '---.'   |  |    [/bold magenta]")
    console.print(r"[bold magenta](_|  |   |  |\   \ |  |      |      |    |  |    [/bold magenta]")
    console.print(r"[bold magenta]  `--'   `--' '--' `--'      `------'    `--'     [/bold magenta]")
    console.print(r"[bold magenta]              iOS Crash Analyzer System[/bold magenta]")
    console.print()
    
    console.print()
    table = Table(title="Commands", show_header=True, header_style="bold magenta", border_style="magenta", pad_edge=False)
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    
    table.add_row("python run.py", "System health analysis - Analyze crash reports from database")
    table.add_row("python run.py --panic", "Panic log analysis - Analyze latest panic reports from device")
    table.add_row("python run.py --check", "Panic log analysis (alias for --panic)")
    table.add_row("python run.py --ips [output_dir]", "Extract and analyze .ips crash files from device")
    table.add_row("python run.py --analyze [udid]", "Full device analysis - Extract and analyze all crash reports")
    table.add_row("python run.py --udid [UDID]", "Specify device UDID for analysis")
    table.add_row("python run.py --syslog", "Stream syslog from device in real-time")
    table.add_row("python run.py --diagnostics", "Get device diagnostics information")
    table.add_row("python run.py --sysdiagnose [output]", "Collect sysdiagnose archive from device")
    table.add_row("python run.py --watch [process]", "Watch for new crash reports in real-time")
    
    console.print(table)


async def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(add_help=False)
    
    parser.add_argument('--panic', action='store_true', help='Run panic log analysis')
    parser.add_argument('--ips', nargs='?', const='ips_reports', help='Extract and analyze .ips files')
    parser.add_argument('--analyze', nargs='?', const=True, help='Run full device analysis (optional UDID)')
    parser.add_argument('--udid', metavar='UDID', help='Device UDID for analysis')
    parser.add_argument('--syslog', action='store_true', help='Stream syslog from device')
    parser.add_argument('--diagnostics', action='store_true', help='Get device diagnostics')
    parser.add_argument('--sysdiagnose', nargs='?', const='sysdiagnose.tar.gz', help='Collect sysdiagnose archive')
    parser.add_argument('--watch', nargs='?', const=True, help='Watch for new crash reports')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message')
    
    args = parser.parse_args()
    
    if args.help:
        print_usage()
        sys.exit(0)
    
    analyzer = iOSCrashAnalyzer()
    
    if args.syslog:
        await analyzer.run_syslog_streaming()
    elif args.diagnostics:
        await analyzer.run_diagnostics_analysis()
    elif args.sysdiagnose:
        await analyzer.run_sysdiagnose_collection(args.sysdiagnose)
    elif args.watch:
        await analyzer.run_crash_watch(args.watch if isinstance(args.watch, str) else None)
    elif args.ips:
        success = await analyzer.extract_and_analyze_ips(args.ips)
        if not success:
            sys.exit(1)
    elif args.panic:
        await analyzer.run_panic_analysis()
    elif args.analyze:
        udid = args.analyze if isinstance(args.analyze, str) else args.udid
        await analyzer.run_full_analysis(udid)
    else:
        await analyzer.run_system_health_analysis()


if __name__ == '__main__':
    asyncio.run(main())
