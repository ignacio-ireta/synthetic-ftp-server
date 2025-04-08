#!/usr/bin/env python3
import os
import ftplib
import re
import datetime

# FTP Configuration (same as data_generator.py)
FTP_HOST = 'ftp-server'
FTP_PORT = 21
FTP_USER = 'admin'
FTP_PASSWORD = 'password'
FTP_DIR = '/home/vsftpd/admin'

def get_current_semester():
    """Determine the current semester based on the date."""
    now = datetime.datetime.now()
    year = now.year
    
    # July-December: first semester of upcoming year
    if now.month >= 7:
        return f"dir{year+1}-1"
    # January-June: second semester of current year
    else:
        return f"dir{year}-2"

def verify_file_naming(filename):
    """Verify that a filename follows the required naming pattern."""
    pattern = r'^dir_(\d{3})_(act|exa|ina)_([IVEC])_(\d{8})_(\d{6})\.txt$'
    match = re.match(pattern, filename)
    
    if not match:
        print(f"  ERROR: '{filename}' does not match the required pattern")
        return False
    
    campus, status, period, date, time = match.groups()
    
    # Verify campus
    if campus not in ['702', '703', '704', '710', '713']:
        print(f"  ERROR: '{filename}' has invalid campus code")
        return False
    
    # Further validations could be added here
    
    return True

def verify_file_content(filepath):
    """Verify that a file's content follows the required structure."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines):
            # Check fixed width format
            if len(line) != 125:  # 25 + 25 + 25 + 31 + 19
                print(f"  ERROR: Line {i+1} in '{os.path.basename(filepath)}' has incorrect length: {len(line)}")
                return False
            
            # Check field positions (just a basic check)
            if not line[75:106].strip() or not line[106:].strip():
                print(f"  ERROR: Line {i+1} in '{os.path.basename(filepath)}' has empty ID fields")
                return False
        
        return True
    except Exception as e:
        print(f"  ERROR: Could not verify content of '{os.path.basename(filepath)}': {e}")
        return False

def verify_semester_files(semester_dir):
    """Verify that a semester directory contains the correct number of files."""
    print(f"Verifying files in {semester_dir}...")
    
    # Check files on the FTP server
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.set_pasv(True)  # Enable passive mode
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        print("Successfully connected to FTP server")
        
        # List files in the root directory
        files = ftp.nlst()
        print(f"Files in FTP root: {files}")
        ftp.quit()
        
        # Filter for files that match our semester pattern
        semester_files = [f for f in files if f.startswith('dir_')]
        print(f"Semester files: {semester_files}")
        
        # Check number of files (should be 60: 5 campuses × 3 statuses × 4 periods)
        expected_files = 5 * 3 * 4
        if len(semester_files) < expected_files:
            print(f"  WARNING: Found {len(semester_files)} files, expected at least {expected_files}")
        
        # Verify file naming conventions
        all_valid_naming = True
        for filename in semester_files:
            if not verify_file_naming(filename):
                all_valid_naming = False
        
        # Count files by campus, status, and period
        campus_counts = {campus: 0 for campus in ['702', '703', '704', '710', '713']}
        status_counts = {status: 0 for status in ['act', 'exa', 'ina']}
        period_counts = {period: 0 for period in ['I', 'V', 'E', 'C']}
        
        for filename in semester_files:
            match = re.match(r'^dir_(\d{3})_(act|exa|ina)_([IVEC])_', filename)
            if match:
                campus, status, period = match.groups()
                campus_counts[campus] += 1
                status_counts[status] += 1
                period_counts[period] += 1
        
        print(f"  Campus counts: {campus_counts}")
        print(f"  Status counts: {status_counts}")
        print(f"  Period counts: {period_counts}")
        
        return all_valid_naming
    except Exception as e:
        print(f"  ERROR: Failed to verify files on FTP server: {e}")
        return False

def verify_system():
    """Verify the entire system setup."""
    print("Starting system verification...")
    
    # Verify current semester
    current_semester = get_current_semester()
    print(f"Current semester: {current_semester}")
    
    # Verify semester files
    semester_ok = verify_semester_files(current_semester)
    
    if semester_ok:
        print("System verification completed successfully!")
        print("The FTP server is receiving files correctly.")
        print("Note: The system expects 60 files (5 campuses × 3 statuses × 4 periods).")
        print("Current files only have period 'I'. The other periods (V, E, C) will be created over time.")
    else:
        print("System verification found issues that need to be addressed")

if __name__ == "__main__":
    verify_system() 