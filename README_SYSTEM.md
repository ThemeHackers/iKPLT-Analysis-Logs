# iOS Crash Report Analyzer System

Complete Python implementation for iOS crash report extraction and analysis.

## Features

- **Device Connection**: Connect to iOS devices via USB using pymobiledevice3
- **Crash Report Extraction**: Download crash reports from iOS devices
- **File Parsing**: Parse .ips, .panic, .crash, and .txt files
- **Database Storage**: Store crash reports in SQLite database
- **Search & Query**: Search crash reports by content
- **Statistics**: View database statistics and analytics
- **Export**: Export crash reports to JSON format
- **Local File Processing**: Process local crash report files

## Installation

```bash
pip install pymobiledevice3 pycrashreport
```

## Usage

### List connected devices
```bash
python main.py list-devices
```

### Analyze device and extract crash reports
```bash
python main.py analyze
```

### Analyze specific device
```bash
python main.py analyze --udid XXXX
```

### List crash reports from database
```bash
python main.py list-crashes
```

### Search crash reports
```bash
python main.py search "SIGABRT"
```

### Show statistics
```bash
python main.py stats
```

### Export to JSON
```bash
python main.py export output.json
```

### Process local file
```bash
python main.py process-file crash.ips
```

## System Architecture

```
┌─────────────────────────────────────────┐
│         CLI Interface (cli.py)           │
└──────────────┬──────────────────────────┘
                  │
   ┌────────────▼──────────────────────────┐
   │      Main Analyzer (analyzer.py)      │
   │  - Orchestrates workflow              │
   │  - Coordinates components             │
   └────────────┬──────────────────────────┘
                  │
   ┌────────────┴──────────────────────────┐
   │              Components                │
   ├───────────────────────────────────────┤
   │ Device Manager (device_manager.py)    │
   │ - Device connection                   │
   │ - Lockdown authentication             │
   │ - File operations                    │
   ├───────────────────────────────────────┤
   │ Parser (parser.py)                    │
   │ - Parse .ips files                    │
   │ - Parse .panic files                  │
   │ - Parse .crash files                  │
   ├───────────────────────────────────────┤
   │ Database Manager (database.py)        │
   │ - SQLite storage                      │
   │ - Query operations                   │
   │ - Export functionality                │
   └───────────────────────────────────────┘
```

## Database Schema

### crash_reports
- Main table for crash reports
- Stores metadata and parsed content

### devices
- Device information
- Tracking device history

### processes
- Process information from crash reports

### threads
- Thread information and stack traces

### binary_images
- Binary image information

## Configuration

Configuration is in `crash_analyzer_system/config.py`:

- `DATABASE_CONFIG`: Database settings
- `DEVICE_CONFIG`: Device connection settings
- `CRASH_REPORT_CONFIG`: Crash report processing settings
- `LOG_CONFIG`: Logging configuration

## Requirements

- Python 3.7+
- pymobiledevice3
- pycrashreport
- iOS device with iTunes/Apple Mobile Device Support installed
- USB cable for device connection

## Troubleshooting

### Device not found
1. Ensure device is connected via USB
2. Unlock the device
3. Trust this computer on the device
4. Install iTunes or Apple Mobile Device Support
5. Check if usbmuxd service is running

### Connection failed
1. Check device is unlocked
2. Verify device trusts this computer
3. Try different USB port
4. Try different USB cable
5. Restart the device

## License

MIT License
