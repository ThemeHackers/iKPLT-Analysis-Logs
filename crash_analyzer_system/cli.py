"""
Command Line Interface for Crash Analyzer System
"""

import argparse
import asyncio
import sys
import json
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint
from rich.text import Text

from .analyzer import CrashAnalyzer
from .database import DatabaseManager
from .fault_codes import get_fault_code_info, search_fault_codes
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


class CrashAnalyzerCLI:
    """Command Line Interface for Crash Analyzer"""
    
    def __init__(self):
        self.analyzer = CrashAnalyzer()
        self.db = DatabaseManager()
    
    async def list_devices(self):
        """List connected iOS devices"""
        console.print("\n[bold cyan]=== Connected iOS Devices ===[/bold cyan]\n")
        
        devices = await self.analyzer.list_devices()
        
        if not devices:
            console.print("[red]❌ No iOS devices found.[/red]")
            console.print("\n[yellow]Please ensure:[/yellow]")
            console.print("  1. Device is connected via USB")
            console.print("  2. Device is unlocked")
            console.print("  3. Device trusts this computer")
            console.print("  4. iTunes/Apple Mobile Device Support is installed")
            return
        
        table = Table(title="iOS Devices")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("UDID", style="green")
        table.add_column("Connection Type", style="blue")
        
        for i, device in enumerate(devices, 1):
            table.add_row(str(i), device['udid'], device['connection_type'])
        
        console.print(table)
    
    async def analyze_device(self, udid: Optional[str] = None):
        """Analyze device and extract crash reports"""
        console.print("\n[bold cyan]=== Analyzing Device ===[/bold cyan]")
        if udid:
            console.print(f"[yellow]Target UDID:[/yellow] {udid}")
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Analyzing device...", total=None)
            results = await self.analyzer.analyze_device(udid)
            progress.update(task, completed=True)
        
        console.print("\n[bold green]=== Analysis Results ===[/bold green]")
        
        results_table = Table()
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Success", "[green]✓[/green]" if results['success'] else "[red]✗[/red]")
        results_table.add_row("Device UDID", results['device_udid'] or "N/A")
        results_table.add_row("Crash Reports Found", str(results['crash_reports_extracted']))
        results_table.add_row("Crash Reports Processed", str(results['crash_reports_processed']))
        
        console.print(results_table)
        
        if results['errors']:
            console.print("\n[red]Errors:[/red]")
            for error in results['errors']:
                console.print(f"  [red]•[/red] {error}")
        
        if results['success']:
            console.print("\n[green]✓ Analysis completed successfully![/green]")
        else:
            console.print("\n[red]✗ Analysis failed![/red]")
    
    def list_crash_reports(self, device_udid: Optional[str] = None, limit: int = 100):
        """List crash reports from database"""
        console.print("\n[bold cyan]=== Crash Reports ===[/bold cyan]\n")
        
        reports = self.analyzer.get_crash_reports(device_udid, limit)
        
        if not reports:
            console.print("[yellow]⚠ No crash reports found in database.[/yellow]")
            return
        
        console.print(f"[green]Total: {len(reports)} crash reports[/green]\n")
        
        table = Table(title="Crash Reports")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Device UDID", style="green")
        table.add_column("File", style="blue")
        table.add_column("Type", style="magenta")
        table.add_column("Fault Code", style="red")
        table.add_column("Date", style="yellow")
        table.add_column("Process", style="white")
        
        for report in reports:
            fault_code = report.get('fault_code') or 'N/A'
            # Highlight fault codes in red if present
            if fault_code != 'N/A':
                fault_code = f"[red]{fault_code}[/red]"
            
            table.add_row(
                str(report['id']),
                report['device_udid'][:16] + "...",
                report['file_name'],
                report['exception_type'] or 'N/A',
                fault_code,
                report['crash_date'] or 'N/A',
                report['process_name'] or 'N/A'
            )
        
        console.print(table)
    
    def search_crash_reports(self, query: str, limit: int = 100):
        """Search crash reports"""
        console.print(f"\n[bold cyan]=== Search Results for '{query}' ===[/bold cyan]\n")
        
        reports = self.analyzer.search_crash_reports(query, limit)
        
        if not reports:
            console.print("[yellow]⚠ No matching crash reports found.[/yellow]")
            return
        
        console.print(f"[green]Found {len(reports)} matching crash reports[/green]\n")
        
        table = Table(title="Search Results")
        table.add_column("ID", style="cyan", justify="right")
        table.add_column("Device UDID", style="green")
        table.add_column("File", style="blue")
        table.add_column("Type", style="magenta")
        
        for report in reports:
            table.add_row(
                str(report['id']),
                report['device_udid'][:16] + "...",
                report['file_name'],
                report['exception_type'] or 'N/A'
            )
        
        console.print(table)
    
    def show_statistics(self):
        """Show database statistics"""
        console.print("\n[bold cyan]=== Database Statistics ===[/bold cyan]\n")
        
        stats = self.analyzer.get_statistics()
        
        # Main statistics table
        stats_table = Table(title="Overview")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Crash Reports", str(stats['total_crash_reports']))
        stats_table.add_row("Total Devices", str(stats['total_devices']))
        
        console.print(stats_table)
        
        # Crashes by device table
        if stats['crashes_by_device']:
            console.print("\n[bold yellow]Crashes by Device:[/bold yellow]")
            device_table = Table()
            device_table.add_column("Device UDID", style="green")
            device_table.add_column("Count", style="cyan", justify="right")
            
            for udid, count in stats['crashes_by_device'].items():
                device_table.add_row(udid[:20] + "...", str(count))
            
            console.print(device_table)
        
        # Top exceptions table
        if stats['top_exceptions']:
            console.print("\n[bold magenta]Top Exception Types:[/bold magenta]")
            exc_table = Table()
            exc_table.add_column("Exception Type", style="magenta")
            exc_table.add_column("Count", style="cyan", justify="right")
            
            for exc_type, count in stats['top_exceptions'].items():
                exc_table.add_row(exc_type, str(count))
            
            console.print(exc_table)
        
        console.print()
    
    def export_json(self, output_path: str):
        """Export crash reports to JSON"""
        console.print("\n[bold cyan]=== Exporting to JSON ===[/bold cyan]")
        console.print(f"[yellow]Output:[/yellow] {output_path}\n")
        
        try:
            self.analyzer.export_to_json(output_path)
            console.print("[green]✓ Export completed successfully![/green]")
        except Exception as e:
            console.print(f"[red]✗ Export failed: {e}[/red]")
    
    async def process_local_file(self, file_path: str, device_udid: str = "local"):
        """Process a local crash report file"""
        console.print("\n[bold cyan]=== Processing Local File ===[/bold cyan]")
        console.print(f"[yellow]File:[/yellow] {file_path}\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing file...", total=None)
            results = await self.analyzer.process_local_file(file_path, device_udid)
            progress.update(task, completed=True)
        
        if results['success']:
            console.print("[green]✓ File processed successfully![/green]")
        else:
            console.print("[red]✗ File processing failed![/red]")
            if results['errors']:
                console.print("\n[red]Errors:[/red]")
                for error in results['errors']:
                    console.print(f"  [red]•[/red] {error}")
    
    def fault_code_lookup(self, code: str):
        """Look up a fault code"""
        console.print(f"\n[bold cyan]=== Fault Code Lookup: {code} ===[/bold cyan]\n")
        
        info = get_fault_code_info(code)
        
        table = Table(title="Fault Code Information")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Code", code)
        table.add_row("Description", info.get('description', 'Unknown'))
        table.add_row("Device Series", info.get('device_series', 'Unknown'))
        
        if info.get('note'):
            table.add_row("Note", info.get('note'))
        
        if info.get('decimal_value'):
            table.add_row("Decimal Value", str(info.get('decimal_value')))
        
        console.print(table)


def main():
    """Main entry point"""
    # Display banner
    banner = Panel(
        "[bold cyan]iOS Crash Report Analyzer System[/bold cyan]\n"
        "[green]Complete Python Implementation[/green]\n"
        "[dim]Version 1.0.0[/dim]",
        title="[bold white]📱 Crash Analyzer[/bold white]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(banner)
    console.print()
    
    parser = argparse.ArgumentParser(
        description='iOS Crash Report Analyzer System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list-devices              List connected iOS devices
  %(prog)s analyze                   Analyze device and extract crash reports
  %(prog)s analyze --udid XXXX       Analyze specific device
  %(prog)s list-crashes              List crash reports from database
  %(prog)s search "SIGABRT"          Search crash reports
  %(prog)s stats                     Show database statistics
  %(prog)s export output.json        Export crash reports to JSON
  %(prog)s process-file crash.ips    Process local crash report file
  %(prog)s fault-code 0x400          Look up fault code information
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List devices command
    subparsers.add_parser('list-devices', help='List connected iOS devices')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze device and extract crash reports')
    analyze_parser.add_argument('--udid', help='Specific device UDID')
    
    # List crashes command
    list_parser = subparsers.add_parser('list-crashes', help='List crash reports from database')
    list_parser.add_argument('--device', help='Filter by device UDID')
    list_parser.add_argument('--limit', type=int, default=100, help='Limit results')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search crash reports')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=100, help='Limit results')
    
    # Statistics command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export crash reports to JSON')
    export_parser.add_argument('output', help='Output JSON file path')
    
    # Process file command
    process_parser = subparsers.add_parser('process-file', help='Process local crash report file')
    process_parser.add_argument('file', help='Crash report file path')
    process_parser.add_argument('--device-udid', default='local', help='Device UDID to assign')
    
    # Fault code lookup command
    fault_parser = subparsers.add_parser('fault-code', help='Look up fault code information')
    fault_parser.add_argument('code', help='Fault code to look up')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = CrashAnalyzerCLI()
    
    # Execute command
    if args.command == 'list-devices':
        asyncio.run(cli.list_devices())
    elif args.command == 'analyze':
        asyncio.run(cli.analyze_device(args.udid))
    elif args.command == 'list-crashes':
        cli.list_crash_reports(args.device, args.limit)
    elif args.command == 'search':
        cli.search_crash_reports(args.query, args.limit)
    elif args.command == 'stats':
        cli.show_statistics()
    elif args.command == 'export':
        cli.export_json(args.output)
    elif args.command == 'process-file':
        asyncio.run(cli.process_local_file(args.file, args.device_udid))
    elif args.command == 'fault-code':
        cli.fault_code_lookup(args.code)


if __name__ == '__main__':
    main()
