"""
Database Manager - SQLite database for crash reports
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from .config import DATABASE_CONFIG


class DatabaseManager:
    """Manage SQLite database for crash reports"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_CONFIG["path"]
        self.timeout = DATABASE_CONFIG["timeout"]
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        cursor = conn.cursor()
        
        # Main crash reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crash_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_udid TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT,
                file_type TEXT,
                file_size INTEGER,
                incident_id TEXT,
                crash_reporter_key TEXT,
                build_version TEXT,
                product_type TEXT,
                os_version TEXT,
                crash_date TEXT,
                crash_time TEXT,
                exception_type TEXT,
                exception_message TEXT,
                process_name TEXT,
                process_id INTEGER,
                parent_process TEXT,
                hardware_model TEXT,
                raw_content TEXT,
                parsed_metadata TEXT,
                extracted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(device_udid, file_name)
            )
        ''')
        
        # Process information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crash_report_id INTEGER,
                process_name TEXT,
                process_id INTEGER,
                parent_process TEXT,
                path TEXT,
                start_time TEXT,
                cpu_time REAL,
                memory_usage INTEGER,
                FOREIGN KEY (crash_report_id) REFERENCES crash_reports(id)
            )
        ''')
        
        # Thread information table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crash_report_id INTEGER,
                thread_id INTEGER,
                thread_name TEXT,
                crashed BOOLEAN DEFAULT 0,
                stack_trace TEXT,
                FOREIGN KEY (crash_report_id) REFERENCES crash_reports(id)
            )
        ''')
        
        # Binary images table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS binary_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crash_report_id INTEGER,
                image_name TEXT,
                image_uuid TEXT,
                image_base_address TEXT,
                image_size INTEGER,
                image_path TEXT,
                FOREIGN KEY (crash_report_id) REFERENCES crash_reports(id)
            )
        ''')
        
        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                udid TEXT UNIQUE NOT NULL,
                device_name TEXT,
                device_class TEXT,
                hardware_model TEXT,
                product_type TEXT,
                os_version TEXT,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crash_device ON crash_reports(device_udid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crash_date ON crash_reports(crash_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crash_type ON crash_reports(exception_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_device_udid ON devices(udid)')
        
        conn.commit()
        conn.close()
    
    def insert_device(self, udid: str, device_info: Dict[str, Any]) -> int:
        """Insert or update device information"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO devices 
            (udid, device_name, device_class, hardware_model, product_type, os_version, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            udid,
            device_info.get('device_name'),
            device_info.get('device_class'),
            device_info.get('hardware_model'),
            device_info.get('product_type'),
            device_info.get('os_version')
        ))
        
        device_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return device_id
    
    def insert_crash_report(self, crash_data: Dict[str, Any]) -> int:
        """Insert a crash report into the database"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO crash_reports
            (device_udid, file_name, file_path, file_type, file_size, incident_id,
             crash_reporter_key, build_version, product_type, os_version, crash_date,
             crash_time, exception_type, exception_message, process_name, process_id,
             parent_process, hardware_model, raw_content, parsed_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            crash_data.get('device_udid'),
            crash_data.get('file_name'),
            crash_data.get('file_path'),
            crash_data.get('file_type'),
            crash_data.get('file_size'),
            crash_data.get('incident_id'),
            crash_data.get('crash_reporter_key'),
            crash_data.get('build_version'),
            crash_data.get('product_type'),
            crash_data.get('os_version'),
            crash_data.get('crash_date'),
            crash_data.get('crash_time'),
            crash_data.get('exception_type'),
            crash_data.get('exception_message'),
            crash_data.get('process_name'),
            crash_data.get('process_id'),
            crash_data.get('parent_process'),
            crash_data.get('hardware_model'),
            crash_data.get('raw_content'),
            json.dumps(crash_data.get('parsed_metadata', {}))
        ))
        
        crash_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return crash_id
    
    def get_crash_reports(self, device_udid: str = None, limit: int = 100) -> List[Dict]:
        """Get crash reports, optionally filtered by device"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if device_udid:
            cursor.execute('''
                SELECT * FROM crash_reports 
                WHERE device_udid = ? 
                ORDER BY crash_date DESC, crash_time DESC 
                LIMIT ?
            ''', (device_udid, limit))
        else:
            cursor.execute('''
                SELECT * FROM crash_reports 
                ORDER BY crash_date DESC, crash_time DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def search_crash_reports(self, query: str, limit: int = 100) -> List[Dict]:
        """Search crash reports by content"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM crash_reports 
            WHERE file_name LIKE ? 
               OR exception_type LIKE ? 
               OR exception_message LIKE ? 
               OR process_name LIKE ?
            ORDER BY crash_date DESC 
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_devices(self) -> List[Dict]:
        """Get all devices"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM devices ORDER BY last_seen DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total crash reports
        cursor.execute('SELECT COUNT(*) FROM crash_reports')
        stats['total_crash_reports'] = cursor.fetchone()[0]
        
        # Total devices
        cursor.execute('SELECT COUNT(*) FROM devices')
        stats['total_devices'] = cursor.fetchone()[0]
        
        # Crash reports by device
        cursor.execute('''
            SELECT device_udid, COUNT(*) as count 
            FROM crash_reports 
            GROUP BY device_udid
        ''')
        stats['crashes_by_device'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Most common exception types
        cursor.execute('''
            SELECT exception_type, COUNT(*) as count 
            FROM crash_reports 
            WHERE exception_type IS NOT NULL
            GROUP BY exception_type 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        stats['top_exceptions'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return stats
    
    def export_to_json(self, output_path: str):
        """Export all crash reports to JSON file"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM crash_reports')
        rows = cursor.fetchall()
        
        data = [dict(row) for row in rows]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        conn.close()
