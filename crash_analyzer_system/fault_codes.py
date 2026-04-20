"""
Fault Code Reference Database
Comprehensive iOS panic log faults for iPhone devices
Supports: iPhone 5s through iPhone 17 series
"""

LEGACY_FAULT_CODES = {
    "mic1": {
        "description": "Primary charging port flex microphone. Highly susceptible to liquid damage and mechanical stress from charging port insertion.",
        "note": "On the iPhone SE 2020, this can occasionally indicate a severe logic board failure rather than just the flex.",
        "device_series": "iPhone 12 series and older",
        "vulnerability": "Charging port assembly - primary environmental ingress point"
    },
    "mic2": {
        "description": "Microphone situated adjacent to the rear camera flash. This sensor routes through the power button flex assembly.",
        "device_series": "iPhone 12 series and older",
        "location": "Power button flex"
    },
    "mic3": {
        "description": "Microphone positioned on the front-facing camera and earpiece flex assembly.",
        "device_series": "iPhone 12 series and older",
        "location": "Front camera flex"
    },
    "mic4": {
        "description": "Bottom-right microphone integrated into the charging port assembly.",
        "device_series": "iPhone 12 series and older",
        "location": "Charging port assembly"
    },
    "prs0": {
        "description": "Barometer telemetry failure. The barometer is historically located on the charging port flex assembly and requires access to ambient air pressure.",
        "device_series": "iPhone 12 series and older",
        "vulnerability": "Frequent point of failure following minor liquid exposure due to air pressure access"
    },
    "tg0b": {
        "description": "Critical failure in the battery data line. Indicates the logic board cannot read the battery's Gas Gauge chip due to a warped connector or damaged FPC pins.",
        "device_series": "iPhone 12 series and older",
        "protocol": "SWI or HDQ communication protocols used by Apple's gas gauge ICs (Tigris or Tristar)"
    },
    "ans2": {
        "description": "NAND flash memory communication failure. Points to PCIe storage errors, often resulting from separated board layers or failing BGA solder joints beneath the NAND IC.",
        "device_series": "iPhone 12 series and older",
        "severity": "Logic board substrate failure",
        "cause": "Severe kinetic impacts causing inter-board solder joint fractures"
    },
    "Ememory": {
        "description": "NAND flash memory communication failure. Points to PCIe storage errors, often resulting from separated board layers or failing BGA solder joints beneath the NAND IC.",
        "device_series": "iPhone 12 series and older",
        "severity": "Logic board substrate failure",
        "cause": "Severe kinetic impacts causing inter-board solder joint fractures"
    },
    "AppleSocHot": {
        "description": "Thermal runaway condition or false thermal report originating from the CPU.",
        "device_series": "Primarily iPhone 7 series",
        "severity": "Critical",
        "solution": "Frequently necessitates board-level reflowing or CPU reballing due to extreme physical stress"
    }
}

IPHONE_13_CODES = {
    "0x800": {
        "description": "Charging port flex failure",
        "device_series": "iPhone 13 base series",
        "location": "Charging port assembly"
    },
    "0x1000": {
        "description": "Proximity flex cable failure",
        "device_series": "iPhone 13 series",
        "location": "Top earpiece sensor array"
    },
    "0x1800": {
        "description": "Charging port flex & proximity flex cable combined failure",
        "device_series": "iPhone 13 series",
        "combination": "0x800 + 0x1000",
        "cause": "Total liquid immersion or careless disassembly"
    },
    "0x400": {
        "description": "Gyroscope communication failure. Strongly indicative of logic board sandwich separation.",
        "device_series": "iPhone 13 Mini (highly prevalent)",
        "severity": "Critical",
        "solution": "Requires complete logic board separation, reballing of interposer, and thermal bonding"
    }
}

IPHONE_14_BASE_CODES = {
    "0x100000": {
        "description": "Primary charging port flex failure",
        "device_series": "iPhone 14 and 14 Plus",
        "location": "Charging port assembly"
    },
    "0x200000": {
        "description": "Proximity flex cable failure",
        "device_series": "iPhone 14 and 14 Plus",
        "location": "Top earpiece sensor array"
    },
    "0x400000": {
        "description": "Wireless charging flex failure attached to removable back glass",
        "device_series": "iPhone 14 and 14 Plus",
        "vulnerability": "Leading cause of three-minute reboots due to back glass removal during repairs"
    },
    "0x500000": {
        "description": "Taptic engine interconnected failure or severe battery communication breakdown",
        "device_series": "iPhone 14 and 14 Plus",
        "severity": "Complex electrical failure"
    }
}

IPHONE_14_PRO_CODES = {
    "0x10000": {
        "description": "Isolated power button flex failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "location": "Power button flex"
    },
    "0x40000": {
        "description": "Charging port flex failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "location": "Charging port assembly"
    },
    "0x80000": {
        "description": "Proximity flex failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "location": "Top earpiece sensor array"
    },
    "0xc0000": {
        "description": "Combined charge port and proximity flex failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "combination": "0x40000 + 0x80000",
        "cause": "Liquid damage at top and bottom of chassis"
    },
    "0x140000": {
        "description": "Combined power button and charging port failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "combination": "0x10000 + 0x40000"
    },
    "0x180000": {
        "description": "Combined proximity flex and power button failure",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "combination": "0x80000 + 0x10000"
    },
    "0x1c0000": {
        "description": "Peripheral cascade failure - charge port, power button, and proximity flex",
        "device_series": "iPhone 14 Pro and 14 Pro Max",
        "severity": "Critical",
        "combination": "0x40000 + 0x80000 + 0x10000",
        "description": "Logic board entirely blind to all three flex cables"
    }
}

IPHONE_15_BASE_CODES = {
    "0x80000": {
        "description": "Charging port flex failure",
        "device_series": "iPhone 15 and 15 Plus",
        "location": "Charging port assembly"
    },
    "0x100000": {
        "description": "Proximity flex cable failure",
        "device_series": "iPhone 15 and 15 Plus",
        "location": "Top earpiece sensor array"
    },
    "0x200000": {
        "description": "Back glass wireless charging flex failure",
        "device_series": "iPhone 15 and 15 Plus",
        "location": "Wireless charging coil on back glass"
    }
}

IPHONE_15_PRO_CODES = {
    "0xa1": {
        "description": "Battery data line issue - Battery Management System (BMS) gas gauge not communicating with logic board",
        "device_series": "iPhone 15 Pro and 15 Pro Max",
        "severity": "Distinct from legacy connector faults",
        "protocol": "Battery Management System communication"
    },
    "0x300000": {
        "description": "High-speed USB-C charging port flex telemetry fault",
        "device_series": "iPhone 15 Pro and 15 Pro Max",
        "location": "USB-C charging port assembly",
        "architecture": "USB-C controller"
    },
    "0x100000": {
        "description": "Proximity flex cable fault",
        "device_series": "iPhone 15 Pro and 15 Pro Max",
        "location": "Top earpiece sensor array"
    },
    "0x400000": {
        "description": "Wireless charging flex fault",
        "device_series": "iPhone 15 Pro and 15 Pro Max",
        "location": "Wireless charging coil"
    },
    "0x700000": {
        "description": "Massive combinatorial fault - USB-C port and wireless charging flex",
        "device_series": "iPhone 15 Pro and 15 Pro Max",
        "combination": "0x300000 + 0x400000",
        "severity": "Critical"
    }
}

IPHONE_16_CODES = {
    "0x80000": {
        "description": "Charging port flex failure with integrated air pressure sensor",
        "device_series": "iPhone 16 base models",
        "location": "Charging port assembly with air pressure sensor",
        "feature": "Independent Air Pressure Sensor module"
    },
    "0x180000": {
        "description": "Charging port flex and air pressure sensor failure",
        "device_series": "iPhone 16 base models",
        "decimal": 1572864,
        "feature": "Bottom microphone or air pressure sensor module unplugged"
    },
    "0x300000": {
        "description": "Critical charging port flex failure",
        "device_series": "iPhone 16 Pro and 16 Pro Max",
        "decimal": 3145728,
        "location": "Charging port with air pressure sensor",
        "vulnerability": "Physical damage from back glass breakage or liquid exposure near Taptic Engine"
    },
    "0x200000": {
        "description": "Critical charging port flex failure",
        "device_series": "iPhone 16 Pro and 16 Pro Max",
        "decimal": 2097152,
        "location": "Charging port with air pressure sensor",
        "note": "Aftermarket parts have high defect rates - kernel rejects uncalibrated sensors"
    },
    "169": {
        "description": "Severe Battery Data Line fault on logic board",
        "device_series": "iPhone 16 series",
        "severity": "Logic board level failure",
        "solution": "Inspect battery FPC connector for warping, use diode mode to map data pins, potentially replace ICs U4000/U4200"
    }
}

IPHONE_17_CODES = {
    "0x800000": {
        "description": "Fatal Wireless Charging Flex failure with calibrated sensor",
        "device_series": "iPhone 17 series",
        "decimal": 8388608,
        "location": "Wireless charge coil in back glass assembly",
        "security": "Cryptographically paired to Secure Enclave",
        "solution": "Must be digitally paired using Apple's proprietary System Configuration tool"
    },
    "0x600000": {
        "description": "Charging Port Flex or Air Pressure Sensor failure",
        "device_series": "iPhone 17 series",
        "decimal": 6291456,
        "location": "Charging port assembly"
    },
    "0xE00000": {
        "description": "Widespread peripheral desynchronization - multiple serialized components simultaneously",
        "device_series": "iPhone 17 series",
        "decimal": 14680064,
        "severity": "Critical",
        "description": "Logic board entirely unable to interface with multiple serialized components"
    },
    "0x10000": {
        "description": "Power button flex failure",
        "device_series": "iPhone 17 base models",
        "location": "Power button flex"
    },
    "0x1c0000": {
        "description": "Peripheral cascade failure - Charge port + Power Button + Prox Flex",
        "device_series": "iPhone 17 base models",
        "combination": "0x80000 + 0x10000 + 0x40000",
        "severity": "Critical"
    }
}

UNIVERSAL_CODES = {
    32: {
        "hex": "0x20",
        "description": "Charging circuit failure. Indicates a breakdown in the primary voltage regulation pathways."
    },
    64: {
        "hex": "0x40",
        "description": "Gas gauge failure. The logic board is unable to read battery capacity metrics."
    },
    65: {
        "hex": "0x41",
        "description": "Battery data line failure. Similar to the legacy tg0b code, indicating severed SWI communication."
    },
    161: {
        "hex": "0xa1",
        "description": "Battery sensor failure. Heavily prevalent in the iPhone 15 Pro series when the battery BMS fails."
    },
    169: {
        "hex": "0xa9",
        "description": "Battery data variant. Common on iPhone 16 series, requiring FPC replacement or board-level IC repair (U4000/U4200)."
    },
    1024: {
        "hex": "0x400",
        "description": "Gyroscope communication failure. Strongly indicative of logic board sandwich separation, particularly on dual-layer boards like the iPhone 13 Mini."
    },
    2048: {
        "hex": "0x800",
        "description": "Charging port flex failure. Specifically assigned to the early architectures of the iPhone 13 base series."
    },
    4096: {
        "hex": "0x1000",
        "description": "Proximity flex cable failure. Assigned to the top earpiece sensor array on the iPhone 13 series."
    },
    16384: {
        "hex": "0x4000",
        "description": "Battery sensor total loss. Seen when the battery is completely undetected by the system."
    },
    131072: {
        "hex": "0x20000",
        "description": "Gyroscope failure for iPhone 14 Pro and newer. Confirms catastrophic board separation after physical kinetic trauma."
    },
    262144: {
        "hex": "0x40000",
        "description": "Charging port flex failure exclusively mapped to the iPhone 14 Pro and 14 Pro Max."
    },
    524288: {
        "hex": "0x80000",
        "description": "Proximity flex failure mapped across iPhone 14 to iPhone 17 base models."
    },
    1048576: {
        "hex": "0x100000",
        "description": "Power button flex failure. Found primarily on Pro model architectures where the power flex houses secondary thermistors."
    },
    2097152: {
        "hex": "0x200000",
        "description": "Front sensor or Wireless charging coil fault, depending on the specific model tier (Base vs. Pro)."
    },
    3145728: {
        "hex": "0x300000",
        "description": "USB-C charging port assembly failure. Exclusively mapped to the Pro models beginning with the iPhone 15 Pro transition to USB-C."
    },
    4194304: {
        "hex": "0x400000",
        "description": "Wireless charging coil flex failure."
    },
    5242880: {
        "hex": "0x500000",
        "description": "Taptic engine interconnected failure or severe battery communication breakdown."
    },
    8388608: {
        "hex": "0x800000",
        "description": "Wireless charging coil with Secure Enclave pairing (iPhone 17+)."
    }
}

I2C_BUS_MAPPINGS = {
    "i2c0": {
        "iPhone 6 / 6P": {
            "components": ["U1202", "U1501", "U1502", "U1700"],
            "description": "Primary I2C bus for early iPhone 6 series"
        },
        "iPhone 6s / 6sP": {
            "components": ["U2000", "U4000", "U4020"],
            "description": "Primary I2C bus for iPhone 6s series"
        },
        "iPhone 7 / 7P": {
            "components": ["U1801", "U3703", "U3701", "U4001", "U2301"],
            "description": "Primary I2C bus for iPhone 7 series"
        },
        "iPhone 8 / 8P / X": {
            "components": ["U2700", "U5600", "U5660", "U6110", "J6400"],
            "description": "Primary I2C bus for iPhone 8 and X series"
        },
        "iPhone 12 Series": {
            "components": ["Earpiece speaker flex assembly"],
            "description": "Highly indicative of earpiece speaker flex assembly failure",
            "symptom": "Short on upper ear speaker array pulls entire I2C0 bus to ground, causing aggressive boot loops"
        }
    },
    "i2c1": {
        "iPhone 6 / 6P": {
            "components": ["U1580", "U1400", "U1401", "U1601", "J2118"],
            "description": "Secondary I2C bus for iPhone 6 series"
        },
        "iPhone 6s / 6sP": {
            "components": ["U3800", "U2300", "U3700", "U4500"],
            "description": "Secondary I2C bus for iPhone 6s series"
        },
        "iPhone 7 / 7P": {
            "components": ["U1801", "U2101", "U4601"],
            "description": "Secondary I2C bus for iPhone 7 series"
        },
        "iPhone 8 / 8P / X": {
            "components": ["J4300", "J6400"],
            "description": "Secondary I2C bus for iPhone 8 and X series"
        },
        "iPhone XR / Xs / Xs Max": {
            "components": ["J4300", "U2700", "U6110", "J6400"],
            "description": "Secondary I2C bus for iPhone X series"
        }
    },
    "i2c2": {
        "General Architecture": {
            "components": ["Front camera flex cable"],
            "description": "Primarily associated with the front camera flex cable, encompassing the vibrator signal, ambient light sensor, earpiece, and infrared cameras"
        },
        "iPhone 6 / 6P": {
            "components": ["J1111", "J2019"],
            "description": "Front camera I2C bus for iPhone 6 series"
        },
        "iPhone 6s / 6sP": {
            "components": ["J3100", "J4200", "U4050"],
            "description": "Front camera I2C bus for iPhone 6s series"
        },
        "iPhone 7 / 7P": {
            "components": ["U3301", "J4503"],
            "description": "Front camera I2C bus for iPhone 7 series"
        },
        "iPhone 8 / 8P / X": {
            "components": ["U3301", "J4200", "U5000"],
            "description": "Front camera I2C bus for iPhone 8 and X series"
        }
    },
    "i2c3": {
        "iPhone 7 / 7P": {
            "components": ["Charging port", "Screen", "Rear microphones"],
            "description": "Charging and display I2C bus for iPhone 7 series"
        },
        "iPhone 8 / 8P / X": {
            "components": ["Charging port", "Display connector", "Screen backlight chip"],
            "description": "Charging and display I2C bus for iPhone 8 and X series"
        },
        "iPhone XR / Xs / Xs Max": {
            "components": ["Display power driver IC", "Touch interface", "Touch connector"],
            "description": "Display I2C bus for iPhone X series"
        }
    },
    "SMC i2Cm0": {
        "A11 Bionic Series": {
            "components": ["U3100", "U3300", "U3400", "U6200", "J3200"],
            "description": "Interfaces with power management and logic EEPROM"
        },
        "A12 Bionic Series": {
            "components": ["U3300", "U3400", "U6200", "J3200", "USB IC", "PMU"],
            "description": "Interfaces with power management, USB IC, and PMU"
        }
    },
    "SMC i2Cm1": {
        "A11 Bionic Series": {
            "components": ["Primary USB IC controller"],
            "description": "Dedicated mapping to the primary USB IC controller"
        }
    }
}

DEEP_SUBSYSTEM_PANICS = {
    "AOP NMI POWER": {
        "description": "Non-Maskable Interrupt forcefully directed at the AOP. A hardware event that the CPU cannot ignore under any circumstances.",
        "causes": [
            "Physical short in the front-facing camera assembly",
            "Failure in the primary power button cable",
            "Damaged main crystal oscillator",
            "Severed communication rails between CPU and logic EEPROM"
        ],
        "severity": "Critical"
    },
    "AOP PANIC No pulse on": {
        "description": "Failure by the AOP to receive an expected electrical heartbeat pulse from a peripheral.",
        "causes": [
            "Dead ambient light sensor",
            "Failed rear denoise microphone",
            "Inability to route signals to vibrator/Taptic motor"
        ]
    },
    "AOP PREFETCH ABORT": {
        "description": "Fatal instruction abort from a lower exception level within the processor. The AOP attempted to fetch an execution instruction from a memory address that was invalid, corrupted, or structurally inaccessible.",
        "causes": [
            "Firmware corruption",
            "Deep vulnerabilities in kernel memory allocation handling"
        ],
        "severity": "Critical"
    },
    "EXBrightComponent": {
        "description": "Low-level module responsible for regulating display brightness, running within a secure kernel enclave. Panic occurs during initialization due to invalid temporal input (start time > end time).",
        "architecture": "SecureRTBuddyProxy kernel extension",
        "symptom": "Logical inversion violates fundamental operating parameters",
        "solution": "Complete Device Firmware Update (DFU) restoration or logic board replacement",
        "affected": "iPhone 16 and 17 series running iOS 18.x and 19.x",
        "severity": "Critical"
    },
    "AppleBCMWLAN": {
        "description": "Loss of communication with the Broadcom Wi-Fi and Bluetooth module.",
        "causes": [
            "Module crack",
            "Pseudo-soldering (microscopic stress fractures in BGA solder balls beneath main Application Processor)",
            "PCIe high-speed communication line between CPU and Wi-Fi module physically drops"
        ],
        "severity": "Critical"
    },
    "CP_COM_NORM REQUEST": {
        "description": "Severe disruption in normal high-speed communication flows.",
        "causes": [
            "CPU failing to reach NAND storage memory",
            "Primary camera circuits",
            "Logic board that has been flexed or bent, severing internal copper traces"
        ],
        "severity": "Critical"
    },
    "Ememory apcie": {
        "description": "NAND flash storage chip failure. PCIe bus cannot enumerate the storage drive.",
        "causes": [
            "Dropped or ripped copper pads under NAND BGA chip following catastrophic physical drop"
        ],
        "severity": "Critical"
    },
    "ans2": {
        "description": "NAND flash storage chip failure.",
        "causes": [
            "Dropped or ripped copper pads under NAND BGA chip",
            "Memory queues irreparably corrupted"
        ],
        "severity": "Critical"
    },
    "Invalid queue element linkage": {
        "description": "NAND flash storage chip failure. Memory queues are irreparably corrupted.",
        "causes": [
            "Dropped or ripped copper pads under NAND BGA chip"
        ],
        "severity": "Critical"
    },
    "Kernel data abort": {
        "description": "Direct failure of the CPU execution core itself. Abrupt termination of the CPU process.",
        "causes": [
            "Extreme power instability on processor blade",
            "Buck line coils (inductors) and power management ICs fail to deliver stable current",
            "VCC_MAIN or VDD_BOOST voltage regulation failure"
        ],
        "severity": "Critical"
    },
    "Kernel instructglon fetch Abort": {
        "description": "Direct failure of the CPU execution core itself.",
        "causes": [
            "Extreme power instability on processor blade",
            "Buck line coils (inductors) and power management ICs fail to deliver stable current"
        ],
        "severity": "Critical"
    }
}

THREE_MINUTE_REBOOT_INFO = {
    "description": "Three-minute reboot cycle (180 seconds)",
    "cause": "Watchdog timer timeout due to failed sensor handshake",
    "mechanism": {
        "processor": "Always-On Processor (AOP)",
        "process": "thermalmonitord subsystem",
        "trigger": "Missing sensor data feed",
        "action": "SMC PANIC - ASSERTION FAILED event"
    },
    "sensor_types": [
        "Thermal sensors",
        "Voltage lines",
        "Barometers",
        "NTC thermistors on peripheral flex cables"
    ],
    "diagnostic_requirement": "Logic board must be mounted in test chassis fully populated with verified OEM parts",
    "note": "Cannot bench-test logic boards in isolation - removing flex cables triggers same panic"
}

FAULT_CODES = {
    **LEGACY_FAULT_CODES,
    **IPHONE_13_CODES,
    **IPHONE_14_BASE_CODES,
    **IPHONE_14_PRO_CODES,
    **IPHONE_15_BASE_CODES,
    **IPHONE_15_PRO_CODES,
    **IPHONE_16_CODES,
    **IPHONE_17_CODES
}


def get_fault_code_info(code: str, device_series: str = None) -> dict:
    """
    Get information about a fault code
    
    Args:
        code: Fault code (string or hex)
        device_series: Device series for context
        
    Returns:
        Dictionary with fault code information
    """
    code = str(code).lower()
    
    if code in FAULT_CODES:
        return FAULT_CODES[code]
    
    try:
        if code.startswith('0x'):
            decimal_value = int(code, 16)
        else:
            decimal_value = int(code)
        
        if decimal_value in UNIVERSAL_CODES:
            info = UNIVERSAL_CODES[decimal_value]
            return {
                "description": info["description"],
                "device_series": "Universal (iPhone 13+)",
                "decimal_value": decimal_value,
                "hex": info.get("hex", hex(decimal_value))
            }
    except (ValueError, TypeError):
        pass
    
    return {
        "description": "Unknown fault code",
        "device_series": "Unknown",
        "note": "No information available for this code"
    }


def decode_bitwise_fault_code(hex_code: str, device_series: str = None) -> dict:
    """
    Decode a bitwise fault code to identify multiple simultaneous failures
    
    Args:
        hex_code: Hexadecimal fault code (e.g., "0x1c0000")
        device_series: Device series for context
        
    Returns:
        Dictionary with decoded fault components
    """
    try:
        if hex_code.startswith('0x'):
            decimal_value = int(hex_code, 16)
        else:
            decimal_value = int(hex_code, 10)
        
        decoded_components = []
        remaining_value = decimal_value
        
        for bit_value, info in sorted(UNIVERSAL_CODES.items(), reverse=True):
            if remaining_value >= bit_value:
                decoded_components.append({
                    "bit_value": bit_value,
                    "hex": info.get("hex", hex(bit_value)),
                    "description": info["description"]
                })
                remaining_value -= bit_value
        
        return {
            "original_code": hex_code,
            "decimal_value": decimal_value,
            "decoded_components": decoded_components,
            "component_count": len(decoded_components),
            "is_combinational": len(decoded_components) > 1,
            "remaining_value": remaining_value if remaining_value > 0 else None
        }
    except (ValueError, TypeError):
        return {
            "error": "Invalid fault code format",
            "original_code": hex_code
        }


def search_fault_codes(keyword: str) -> list:
    """
    Search fault codes by keyword
    
    Args:
        keyword: Search keyword
        
    Returns:
        List of matching fault codes
    """
    results = []
    keyword = keyword.lower()
    
    for code, info in FAULT_CODES.items():
        if keyword in info["description"].lower() or keyword in info["device_series"].lower():
            results.append({"code": code, **info})
    
    for decimal, info in UNIVERSAL_CODES.items():
        if keyword in info["description"].lower():
            results.append({
                "code": hex(decimal),
                "description": info["description"],
                "device_series": "Universal (iPhone 13+)",
                "decimal_value": decimal,
                "hex": info.get("hex", hex(decimal))
            })
    
    return results


def get_i2c_bus_info(bus_name: str, device_architecture: str = None) -> dict:
    """
    Get I2C bus information for a specific bus
    
    Args:
        bus_name: I2C bus name (e.g., "i2c0", "i2c1", "i2c2", "i2c3", "SMC i2Cm0", "SMC i2Cm1")
        device_architecture: Device architecture (e.g., "iPhone 6 / 6P")
        
    Returns:
        Dictionary with I2C bus information
    """
    bus_name = bus_name.lower()
    
    if bus_name not in I2C_BUS_MAPPINGS:
        return {
            "error": "Unknown I2C bus",
            "bus_name": bus_name
        }
    
    bus_info = I2C_BUS_MAPPINGS[bus_name]
    
    if device_architecture and device_architecture in bus_info:
        return {
            "bus_name": bus_name,
            "architecture": device_architecture,
            **bus_info[device_architecture]
        }
    
    return {
        "bus_name": bus_name,
        "available_architectures": list(bus_info.keys()),
        **bus_info
    }


def get_deep_subsystem_panic_info(panic_string: str) -> dict:
    """
    Get information about deep subsystem panic
    
    Args:
        panic_string: Panic string from log (e.g., "AOP NMI POWER", "EXBrightComponent")
        
    Returns:
        Dictionary with panic information
    """
    for panic_key, info in DEEP_SUBSYSTEM_PANICS.items():
        if panic_key.lower() in panic_string.lower():
            return {
                "panic_type": panic_key,
                **info
            }
    
    return {
        "error": "Unknown deep subsystem panic",
        "panic_string": panic_string
    }


def is_three_minute_reboot(panic_log: str) -> dict:
    """
    Determine if panic indicates a three-minute reboot cycle
    
    Args:
        panic_log: Full panic log text
        
    Returns:
        Dictionary with analysis results
    """
    indicators = [
        "thermalmonitord",
        "watchdog",
        "SMC PANIC",
        "ASSERTION FAILED",
        "sensor",
        "thermal",
        "temperature",
        "overheat",
        "watchdog timeout",
        "WDT",
        "thermal shutdown",
        "thermal throttling"
    ]
    
    found_indicators = [ind for ind in indicators if ind.lower() in panic_log.lower()]
    
    return {
        "is_three_minute_reboot": len(found_indicators) >= 2,
        "found_indicators": found_indicators,
        "indicator_count": len(found_indicators),
        "confidence": "high" if len(found_indicators) >= 4 else "medium" if len(found_indicators) >= 2 else "low",
        "info": THREE_MINUTE_REBOOT_INFO
    }


HARDWARE_TOPOGRAPHY = {
    "logic_board_types": {
        "single_layer": {
            "description": "Single-layer logic board design",
            "devices": ["iPhone 5s - iPhone 8"],
            "characteristics": "Simpler design, easier to repair"
        },
        "dual_layer_sandwich": {
            "description": "Dual-layer sandwich design with inter-board solder joints",
            "devices": ["iPhone X - iPhone 13 Mini"],
            "vulnerability": "Severe kinetic impacts cause inter-board solder joint fractures",
            "symptoms": "Gyroscope communication failures (0x400, 0x20000)",
            "solution": "Complete logic board separation, reballing of interposer, thermal bonding"
        },
        "triple_layer": {
            "description": "Triple-layer logic board design",
            "devices": ["iPhone 14+"],
            "characteristics": "Most complex design, highest density"
        }
    },
    "component_locations": {
        "charging_port_flex": {
            "components": ["Bottom microphone", "Barometer", "Charging IC", "Air pressure sensor (iPhone 16+)"],
            "vulnerability": "Primary environmental ingress point for liquid damage",
            "fault_codes": ["mic1", "prs0", "0x800", "0x100000", "0x40000", "0x80000", "0x300000"]
        },
        "power_button_flex": {
            "components": ["Power button", "Secondary thermistors", "Rear camera flash microphone"],
            "fault_codes": ["mic2", "0x10000", "0x1048576"]
        },
        "proximity_flex": {
            "components": ["Proximity sensor", "Ambient light sensor", "Earpiece"],
            "location": "Top earpiece sensor array",
            "fault_codes": ["0x1000", "0x200000", "0x80000", "0x524288"]
        },
        "wireless_charging_coil": {
            "components": ["Wireless charging coil", "Calibrated sensor (iPhone 17+)"],
            "location": "Back glass assembly",
            "vulnerability": "Must be disconnected during back glass removal",
            "fault_codes": ["0x400000", "0x200000", "0x8388608"],
            "security_note": "iPhone 17+ has Secure Enclave pairing requiring System Configuration tool"
        },
        "battery_fpc": {
            "components": ["Battery connector", "Gas Gauge IC (Tigris/Tristar)", "Battery data line"],
            "protocol": "SWI or HDQ communication",
            "fault_codes": ["tg0b", "0x41", "0xa1", "169"],
            "vulnerability": "Microscopic deformation in FPC connector can sever data line"
        },
        "nand_flash": {
            "components": ["NAND flash memory chip", "PCIe storage controller"],
            "location": "Logic board substrate",
            "fault_codes": ["ans2", "Ememory", "Ememory apcie", "Invalid queue element linkage"],
            "cause": "Severe kinetic impacts causing inter-board solder joint fractures or ripped copper pads",
            "severity": "Critical - logic board substrate failure"
        }
    },
    "diagnostic_methodologies": {
        "diode_mode_testing": {
            "description": "Digital multimeter in Diode Mode for electrical diagnostics",
            "procedure": [
                "Place positive (red) probe on known ground plane",
                "Place negative (black) probe on FPC pins associated with failing I2C bus",
                "Measure voltage drop across semiconductor junctions in reverse bias",
                "Compare readings to known-good schematic database"
            ],
            "interpretation": {
                "OL (Open Loop)": "Severed trace deep within substrate, requires physical layer separation",
                "0.000V": "Direct short to ground, component pulling current away from CPU"
            }
        },
        "voltage_injection": {
            "description": "Apply regulated low-voltage DC to shorted line and identify heating component",
            "procedure": [
                "Apply heavily regulated low-voltage DC (e.g., 1.8V) directly to shorted line",
                "Use thermal imaging camera to identify microscopic component generating heat",
                "Remove or replace the glowing component to clear the I2C line"
            ],
            "equipment": ["Digital multimeter", "Variable DC power supply", "Thermal imaging camera"]
        },
        "microsoldering": {
            "description": "Advanced board-level repair using microscopic soldering techniques",
            "techniques": [
                "IC replacement (U4000, U4200 for battery data issues)",
                "FPC connector repair or replacement",
                "Inter-board solder joint reballing",
                "Trace repair for severed copper traces"
            ],
            "equipment": ["Microscope", "Hot air rework station", "Soldering iron", "Flux", "Solder wire"]
        },
        "logic_board_separation": {
            "description": "Separate dual-layer logic board for sandwich separation repairs",
            "applicable": ["iPhone X - iPhone 13 Mini"],
            "procedure": [
                "Heat logic board to soften adhesive between layers",
                "Carefully separate layers using specialized tools",
                "Reball interposer with new solder balls",
                "Thermally bond layers back together"
            ],
            "severity": "Advanced repair requiring specialized equipment and training"
        }
    },
    "repair_guidelines": {
        "oem_parts_requirement": {
            "description": "Many modern iOS devices require OEM parts for proper operation",
            "affected_devices": ["iPhone 15 Pro+", "iPhone 16+", "iPhone 17+"],
            "reason": "Kernel actively rejects uncalibrated third-party sensors",
            "calibration": "Components must be digitally paired using Apple's proprietary tools"
        },
        "test_chassis_requirement": {
            "description": "Logic boards cannot be bench-tested in isolation",
            "reason": "Removing flex cables triggers same watchdog timeout panic",
            "requirement": "Logic board must be mounted in test chassis fully populated with verified OEM parts",
            "example": "iPhone 11 requires both charging port flex and power button flex connected"
        },
        "liquid_damage_protocol": {
            "description": "Protocol for liquid-damaged devices",
            "steps": [
                "Ultrasonic cleaning of logic board",
                "Inspect all flex cables for corrosion",
                "Check charging port assembly for liquid ingress",
                "Test all I2C buses with diode mode",
                "Replace corroded components",
                "Calibrate sensors after repair"
            ]
        },
        "secure_enclave_pairing": {
            "description": "Secure Enclave component pairing requirements",
            "affected": ["iPhone 17+ wireless charging coil"],
            "procedure": "Must use Apple's proprietary System Configuration tool for digital pairing",
            "consequence": "System failure if uncalibrated or wrong part used"
        }
    }
}


def get_hardware_topography_info(component: str = None) -> dict:
    """
    Get hardware topography information
    
    Args:
        component: Optional component name to get specific information
        
    Returns:
        Dictionary with hardware topography information
    """
    if component:
        component_lower = component.lower()
        
        for key, value in HARDWARE_TOPOGRAPHY["component_locations"].items():
            if component_lower in key or component_lower in str(value).lower():
                return {
                    "component": key,
                    **value
                }
        
        return {
            "error": "Component not found in topography database",
            "component": component
        }
    
    return HARDWARE_TOPOGRAPHY


def get_diagnostic_methodology(method_name: str) -> dict:
    """
    Get diagnostic methodology information
    
    Args:
        method_name: Name of diagnostic method
        
    Returns:
        Dictionary with methodology information
    """
    method_lower = method_name.lower()
    
    for key, value in HARDWARE_TOPOGRAPHY["diagnostic_methodologies"].items():
        if method_lower in key.lower():
            return {
                "method": key,
                **value
            }
    
    return {
        "error": "Diagnostic method not found",
        "method": method_name
    }


def get_repair_guideline(guideline: str) -> dict:
    """
    Get repair guideline information
    
    Args:
        guideline: Name of guideline
        
    Returns:
        Dictionary with guideline information
    """
    guideline_lower = guideline.lower()
    
    for key, value in HARDWARE_TOPOGRAPHY["repair_guidelines"].items():
        if guideline_lower in key.lower():
            return {
                "guideline": key,
                **value
            }
    
    return {
        "error": "Repair guideline not found",
        "guideline": guideline
    }
