"""
Fault Code Reference Database
Common panic log faults for iPhone devices
"""

FAULT_CODES = {
    # iPhone 12 series and older
    "mic1": {
        "description": "Charging port flex",
        "note": "SE 2020 could be a board issue",
        "device_series": "iPhone 12 and older"
    },
    "mic2": {
        "description": "Power button flex",
        "device_series": "iPhone 12 and older"
    },
    "prs0": {
        "description": "Charging port flex",
        "device_series": "iPhone 12 and older"
    },
    "tg0b": {
        "description": "Battery, battery connector or battery data line",
        "device_series": "iPhone 12 and older"
    },
    "ans2": {
        "description": "NAND related",
        "device_series": "iPhone 12 and older"
    },
    
    # iPhone 13 series
    "0x800": {
        "description": "Charging port flex",
        "device_series": "iPhone 13 series"
    },
    "0x1000": {
        "description": "Proximity flex",
        "device_series": "iPhone 13 series"
    },
    "0x1800": {
        "description": "Charging port flex & proximity flex cable",
        "device_series": "iPhone 13 series"
    },
    "0x400": {
        "description": "Sandwich separation",
        "device_series": "iPhone 13 series"
    },
    
    # iPhone 14 & iPhone 14 Plus
    "0x400000": {
        "description": "Wireless Charging Flex (Back Glass)",
        "device_series": "iPhone 14 & 14 Plus"
    },
    "0x100000": {
        "description": "Charging Port Flex",
        "device_series": "iPhone 14 & 14 Plus"
    },
    "0x500000": {
        "description": "Taptic engine, charging port flex, or battery communication problem",
        "device_series": "iPhone 14 & 14 Plus"
    },
    "0x200000": {
        "description": "Proximity Flex Cable",
        "device_series": "iPhone 14 & 14 Plus"
    },
    
    # iPhone 14 Pro & iPhone 14 Pro Max
    "0x80000": {
        "description": "Proximity flex",
        "device_series": "iPhone 14 Pro & 14 Pro Max"
    },
    "0x40000": {
        "description": "Charging port flex",
        "device_series": "iPhone 14 Pro & 14 Pro Max"
    },
    "0x10000": {
        "description": "Power button flex",
        "device_series": "iPhone 14 Pro & 14 Pro Max"
    },
    "0x20000": {
        "description": "Sandwich separation",
        "device_series": "iPhone 14 Pro & 14 Pro Max"
    },
    
    # iPhone 15 & iPhone 15 Plus
    "0x200000": {
        "description": "Wireless Charging Flex (Back Glass)",
        "device_series": "iPhone 15 & 15 Plus"
    },
    "0x80000": {
        "description": "Charging Port Flex",
        "device_series": "iPhone 15 & 15 Plus"
    },
    "0x100000": {
        "description": "Proximity Flex Cable",
        "device_series": "iPhone 15 & 15 Plus"
    },
    
    # iPhone 15 Pro & iPhone 15 Pro Max
    "0xa1": {
        "description": "Battery",
        "device_series": "iPhone 15 Pro & 15 Pro Max"
    },
    "0x300000": {
        "description": "Charging Port Flex",
        "device_series": "iPhone 15 Pro & 15 Pro Max"
    },
    "0x400000": {
        "description": "Wireless Charging Flex",
        "device_series": "iPhone 15 Pro & 15 Pro Max"
    },
    "0x700000": {
        "description": "Charging Port + Wireless Charging Flex",
        "device_series": "iPhone 15 Pro & 15 Pro Max"
    },
}

# Universal codes (iPhone 13 up)
UNIVERSAL_CODES = {
    32: "Charging circuit",
    64: "Gas gauge",
    65: "Battery data",
    161: "Battery sensor",
    169: "Battery data variant",
    1024: "Gyro",
    2048: "Charge port",
    4096: "Proximity",
    16384: "Battery sensor",
    131072: "Gyro (14 Pro+)",
    262144: "Charge port (14 Pro+)",
    524288: "Proximity (14–17)",
    1048576: "Power button",
    2097152: "Front sensor / Wireless coil",
    3145728: "USB‑C (Pro models)",
    4194304: "Wireless coil",
    5242880: "Battery",
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
    
    # Check in FAULT_CODES
    if code in FAULT_CODES:
        return FAULT_CODES[code]
    
    # Check in UNIVERSAL_CODES (convert to decimal)
    try:
        if code.startswith('0x'):
            decimal_value = int(code, 16)
        else:
            decimal_value = int(code)
        
        if decimal_value in UNIVERSAL_CODES:
            return {
                "description": UNIVERSAL_CODES[decimal_value],
                "device_series": "Universal (iPhone 13+)",
                "decimal_value": decimal_value
            }
    except (ValueError, TypeError):
        pass
    
    return {
        "description": "Unknown fault code",
        "device_series": "Unknown",
        "note": "No information available for this code"
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
    
    for decimal, description in UNIVERSAL_CODES.items():
        if keyword in description.lower():
            results.append({
                "code": hex(decimal),
                "description": description,
                "device_series": "Universal (iPhone 13+)",
                "decimal_value": decimal
            })
    
    return results
