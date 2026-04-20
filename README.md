# iKPLT Analysis Logs

iOS Crash Report Analyzer System - Comprehensive iOS Kernel Panic Analysis Tool

## Overview

iKPLT Analysis Logs is a professional-grade iOS crash report analyzer designed for technicians, repair specialists, and advanced users. It provides comprehensive analysis of iOS kernel panics, crash logs, and system health diagnostics with support for iPhone 5s through iPhone 17 series.

### Key Features

- **iPhone Information Display**: Comprehensive device info (Name, iOS Version, Serial, IMEI, ECID, Battery Health, etc.)
- **pymobiledevice3 Integration**: Direct iOS device communication without external tools
- **Comprehensive Fault Code Database**: Over 100+ fault codes covering all iPhone generations (5s-17)
- **Bitwise Fault Decoding**: Automatically decodes combinational hardware failures (e.g., 0x1c0000 = 0x40000 + 0x80000 + 0x10000)
- **I2C Bus Analysis**: Identifies I2C bus failures and maps them to specific hardware components
- **Deep Subsystem Panic Detection**: Detects AOP panics, EXBrightComponent failures, and other critical system-level errors
- **Three-Minute Reboot Detection**: Identifies watchdog timeout patterns indicative of sensor failures
- **Hardware Topography Information**: Provides component locations, diagnostic methodologies, and repair guidelines
- **Real-time Syslog Streaming**: Stream device logs in real-time with KeyboardInterrupt support
- **Crash Report Watcher**: Monitor for new crash reports in real-time
- **Device Diagnostics**: Get comprehensive device diagnostics including battery info
- **Sysdiagnose Collection**: Collect complete system diagnostics archives
- **Rich CLI Interface**: Beautiful terminal output with ASCII art banner, tables, panels, and progress indicators
- **Graceful Error Handling**: KeyboardInterrupt support, timeout handling, and fallback mechanisms
- **Database Storage**: SQLite database for crash report history and trend analysis
- **JSON Report Export**: Save failure reports as JSON files in `reports/` directory

## Supported iPhone Models

- **Legacy (iPhone 5s - iPhone 12)**: Alphanumeric fault codes (mic1, mic2, prs0, tg0b, ans2, etc.)
- **iPhone 13 Series**: Hexadecimal fault codes with gyroscope/sandwich separation detection
- **iPhone 14 Series**: Base vs Pro model differentiation with wireless charging coil analysis
- **iPhone 15 Series**: USB-C transition analysis with high-speed port diagnostics
- **iPhone 16 Series**: Air pressure sensor integration and aftermarket part rejection detection
- **iPhone 17 Series**: Secure Enclave pairing requirements and advanced serialization diagnostics

## Installation

### Prerequisites

- Python 3.8 or higher
- iOS device with crash logs
- USB connection to device (for device analysis)
- USB cable (original Apple cable recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/iKPLT-Analysis-Logs.git
cd iKPLT-Analysis-Logs

# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install pymobiledevice3>=3.0.0 rich>=13.0.0
```

### Dependencies

**Required:**
- `pymobiledevice3>=3.0.0` - iOS device communication
- `rich>=13.0.0` - Terminal formatting and UI

**Optional:**
- `requests>=2.28.0` - For future HTTP features

**No External Tools Required:**
- No iTunes installation needed
- No libimobiledevice required
- Pure Python implementation

## Usage

### Command Line Interface

```bash
# Main entry point
python main.py [command] [options]

# Alternative entry point
python run.py [command] [options]
```

### Available Commands

#### 1. Help

```bash
python run.py -h
```

Displays ASCII art banner and all available commands.

#### 2. System Health Analysis (Default)

```bash
python run.py
```

Analyzes crash reports from local database with iPhone Information display.

#### 3. Full Device Analysis

```bash
python run.py --analyze
```

Performs comprehensive device analysis:
- Displays iPhone Information (Device Name, iOS Version, Serial, IMEI, ECID, Battery, etc.)
- Connects to device using pymobiledevice3
- Collects device diagnostics
- Lists and downloads crash reports
- Parses and analyzes crash logs
- Runs system health analysis
- Stores results in database

With specific device:
```bash
python run.py --analyze <device-udid>
```

#### 4. Panic Analysis

```bash
python run.py --panic
```

Analyzes kernel panic logs with:
- iPhone Information display
- Fault code detection
- Hardware failure analysis
- Memory error detection
- Risk level assessment

#### 5. IPS File Analysis

```bash
python run.py --ips [output_dir]
```

Extracts and analyzes .ips crash files from device. Default output directory: `ips_reports`

#### 6. Syslog Streaming

```bash
python run.py --syslog
```

Streams syslog from device in real-time with iPhone Information display.

Features:
- Real-time log streaming
- KeyboardInterrupt handling (Ctrl+C to stop)
- Automatic device connection/disconnection

#### 7. Device Diagnostics

```bash
python run.py --diagnostics
```

Gets comprehensive device diagnostics information:
- iPhone Information display
- MobileGestalt data (if available)
- Battery information (Cycle Count, Health, Capacity)
- IORegistry data (fallback)
- Diagnostics info (fallback)

#### 8. Sysdiagnose Collection

```bash
python run.py --sysdiagnose [output_path]
```

Collects sysdiagnose archive from device.

Features:
- iPhone Information display
- Default output: `sysdiagnose.tar.gz`
- Timeout: 10 minutes
- KeyboardInterrupt support
- Automatic device connection/disconnection

Example:
```bash
python run.py --sysdiagnose my_sysdiagnose.tar.gz
```

#### 9. Crash Report Watcher

```bash
python run.py --watch [process_name]
```

Watches for new crash reports in real-time.

Features:
- iPhone Information display
- Monitor all crash reports or specific process
- Real-time crash detection
- KeyboardInterrupt support

Examples:
```bash
# Watch all crash reports
python run.py --watch

# Watch specific process
python run.py --watch SpringBoard
```

#### 10. Specify Device UDID

```bash
python run.py --udid <device-udid>
```

Use with other commands to specify which device to analyze.

Example:
```bash
python run.py --analyze --udid 00008020-001C4D200104002E
```

### iPhone Information Display

All commands now display comprehensive iPhone information before analysis:

**Displayed Information:**
- 📱 Device Name and Product Type (e.g., iPhone 11 Pro)
- 📱 iOS Version and Build Version
- 🔧 Hardware Model and Device Class
- 🔢 Serial Number
- 📞 IMEI
- 🆔 ECID (UniqueChipID)
- 🆔 UDID (truncated for display)
- ✅ Activation Status
- 🔋 Battery Cycles
- 🔋 Battery Health (%)
- 🔋 Max Capacity (%)
- 📦 Model Number
- 🌏 Region Code
- 🎨 Device Color

### pymobiledevice3 Integration

This system uses `pymobiledevice3` for direct iOS device communication:

**Features:**
- Pure Python implementation (no external tools required)
- USBmux device discovery
- Lockdown service communication
- CrashReportsManager for crash report collection
- SyslogService for real-time log streaming
- DiagnosticsService for device diagnostics
- AFC (Apple File Conduit) for file operations

**Benefits:**
- No dependency on `libimobiledevice` or `iTunes`
- Cross-platform support (Windows, macOS, Linux)
- Direct API access instead of subprocess calls
- Better error handling and reliability

### CLI Module Usage

```bash
python -m crash_analyzer_system.cli list-devices
python -m crash_analyzer_system.cli analyze --udid <udid>
python -m crash_analyzer_system.cli list-crashes
python -m crash_analyzer_system.cli search "SIGABRT"
python -m crash_analyzer_system.cli stats
python -m crash_analyzer_system.cli export output.json
python -m crash_analyzer_system.cli process-file crash.ips
python -m crash_analyzer_system.cli fault-code 0x400
```

## Architecture

### Core Modules

- **`crash_analyzer_system/device_manager.py`**: iOS device communication using pymobiledevice3
  - `list_devices()`: USBmux device discovery
  - `connect_device()`: Lockdown service initialization
  - `get_iphone_full_info()`: Comprehensive device information collection
  - `get_crash_reports()`: Crash report listing via CrashReportsManager
  - `download_crash_report()`: Pull reports from device
  - `stream_syslog()`: Real-time syslog streaming via SyslogService
  - `get_diagnostics()`: Device diagnostics via DiagnosticsService
  - `get_sysdiagnose()`: Sysdiagnose archive collection
  - `watch_crash_reports()`: Real-time crash monitoring

- **`crash_analyzer_system/parser.py`**: Crash report parsing (.ips, .panic, .crash formats)
- **`crash_analyzer_system/fault_codes.py`**: Comprehensive fault code database and decoding logic
- **`crash_analyzer_system/failure_detector.py`**: Advanced panic analysis with I2C and deep subsystem detection
- **`crash_analyzer_system/database.py`**: SQLite database for crash report storage
- **`crash_analyzer_system/ips_parser.py`**: Binary plist parsing for .ips files
- **`crash_analyzer_system/cli.py`**: Rich CLI interface with command parsing
- **`run.py`**: Main entry point with all command implementations

### Data Flow

```
Device → DeviceManager (pymobiledevice3) → Parser → FailureDetector → Database → Reports
                    ↓
            iPhone Info Display
                    ↓
                Fault Codes Database
```

### Visual Interface

**Color-coded Sections:**
- 🔴 **Red**: Panic Analysis
- 🟣 **Magenta**: System Health Analysis, Full Device Analysis
- 🟡 **Yellow**: Device Diagnostics
- 🔵 **Blue**: Syslog Streaming
- 🟢 **Green**: Sysdiagnose Collection
- 🔵 **Cyan**: Crash Report Watcher

**Console Output Features:**
- Rich Panels with borders and titles
- ASCII art banner on startup
- Progress bars with spinners for long operations
- Tables with color-coded headers
- Bullet points (●) for completed tasks
- Section indicators (▶) for active processes
- Emoji icons for information types
- Automatic terminal width adaptation

## Fault Code Examples

### Legacy Codes (iPhone 5s-12)

| Code | Description | Component |
|------|-------------|-----------|
| mic1 | Charging port flex microphone | Charging Port |
| mic2 | Power button flex microphone | Power Button |
| prs0 | Barometer telemetry failure | Charging Port |
| tg0b | Battery data line failure | Battery FPC |
| ans2 | NAND flash memory failure | Logic Board |

### iPhone 13 Series

| Code | Description | Component |
|------|-------------|-----------|
| 0x800 | Charging port flex failure | Charging Port |
| 0x1000 | Proximity flex failure | Proximity Sensor |
| 0x400 | Gyroscope failure (sandwich separation) | Logic Board |

### iPhone 14 Pro Series

| Code | Description | Component |
|------|-------------|-----------|
| 0x40000 | Charging port flex failure | Charging Port |
| 0x80000 | Proximity flex failure | Proximity Sensor |
| 0x10000 | Power button flex failure | Power Button |
| 0x1c0000 | Combined failure (all three) | Multiple |

### iPhone 15 Pro Series

| Code | Description | Component |
|------|-------------|-----------|
| 0x300000 | USB-C charging port failure | USB-C Port |
| 0x400000 | Wireless charging coil failure | Back Glass |
| 0xa1 | Battery data line (BMS) | Battery |

### iPhone 16-17 Series

| Code | Description | Component |
|------|-------------|-----------|
| 169 | Battery data line (logic board level) | Logic Board ICs |
| 0x800000 | Wireless charging with Secure Enclave | Back Glass |
| 0xE00000 | Widespread peripheral desynchronization | Multiple |

## Advanced Features

### Bitwise Fault Decoding

The system automatically decodes combinational fault codes:

```
Input: 0x1c0000
Decoded:
  - 0x40000 (262144): Charging port flex failure
  - 0x80000 (524288): Proximity flex failure
  - 0x10000 (1048576): Power button flex failure
```

### I2C Bus Analysis

Detects and maps I2C bus errors to specific components:

```
Detected: i2c0::_checkInterrupts
Bus: i2c0
Architecture: iPhone 12 Series
Components: Earpiece speaker flex assembly
```

### Three-Minute Reboot Detection

Identifies watchdog timeout patterns:

```
Indicators: thermalmonitord, watchdog, SMC PANIC
Diagnosis: Three-minute reboot cycle (sensor handshake failure)
Recommendation: Logic board must be mounted in test chassis with OEM parts
```

### Hardware Topography

Provides component locations and diagnostic methodologies:

- Logic board types (single-layer, dual-layer sandwich, triple-layer)
- Component locations and vulnerabilities
- Diagnostic methods (diode mode testing, voltage injection, microsoldering)
- Repair guidelines (OEM parts requirements, Secure Enclave pairing)

## Database

Crash reports are stored in `data/crash_analyzer.db` (SQLite) with the following tables:

- **crash_reports**: Main crash report data
- **processes**: Process information
- **threads**: Thread information
- **binary_images**: Binary image information
- **devices**: Device information

### Export Data

```bash
python -m crash_analyzer_system.cli export output.json
```

## Error Handling

### KeyboardInterrupt Support

All long-running operations support graceful interruption:

```bash
# Streaming commands (Ctrl+C to stop)
python run.py --syslog       # Press Ctrl+C to stop streaming
python run.py --watch        # Press Ctrl+C to stop watching

# Collection commands
python run.py --sysdiagnose  # Press Ctrl+C to cancel collection
```

### Timeout Handling

- **Sysdiagnose Collection**: 10-minute timeout
- **Device Connection**: Automatic retry with delay
- **Crash Report Download**: 60-second timeout per file

### Error Types

| Error | Cause | Solution |
|-------|-------|----------|
| `No iOS devices found` | Device not connected or not trusted | Connect device and trust computer |
| `LockdownClient error` | Communication failure | Restart device, check USB cable |
| `MobileGestalt deprecated` | iOS version doesn't support full diagnostics | System will use fallback methods |
| `Timeout` | Operation took too long | Retry operation or check device status |
| `Connection failed` | USB connection issue | Try different USB port or cable |

### Fallback Mechanisms

**Diagnostics Collection:**
1. Try MobileGestalt (full data)
2. Fallback to `info("All")` method
3. Fallback to IORegistry data
4. Return empty if all methods fail

**Device Connection:**
1. Try direct USB connection
2. Retry with delay if failed
3. Log error if all attempts fail

## Troubleshooting

### Device Connection Issues

If you encounter connection issues:
1. Ensure device is connected via USB
2. Trust the computer on the iOS device (tap "Trust" when prompted)
3. Check USB cable connection (use original Apple cable if possible)
4. Try a different USB port
5. Restart the iOS device
6. Check that `pymobiledevice3` is installed: `pip install pymobiledevice3`

### pymobiledevice3 Issues

```bash
# Reinstall pymobiledevice3
pip uninstall pymobiledevice3
pip install pymobiledevice3>=3.0.0

# Test device connection
python -c "from pymobiledevice3 import usbmux; print(usbmux.list_devices())"
```

### Permission Errors

On Linux/macOS, you may need to run with sudo:
```bash
sudo python run.py --analyze
```

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## Disclaimer

This tool is designed for professional use by trained technicians and repair specialists. Always verify diagnosis with additional testing methods before performing repairs. The authors are not responsible for any damage caused by improper use of this tool.

