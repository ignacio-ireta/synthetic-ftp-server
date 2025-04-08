#!/usr/bin/env python3
import os
import random
import ftplib
import time
import datetime
import schedule
from dateutil.relativedelta import relativedelta

# Synthetic data dictionaries
PATERNAL_LASTNAMES = [
    'MARTINEZ', 'ESPINOSA', 'JIMENEZ', 'PEREZ', 'FLORES', 'PEREZ', 'VILLANUEVA',
    'OROZCO', 'SANCHEZ', 'AGEA', 'FLORES', 'HERNANDEZ', 'TONACATL', 'MEDINA',
    'VARGAS', 'VIACOBO', 'ALANIS', 'BALDERAS', 'DIAZ', 'FUENTES', 'MERAZ',
    'ALCANTARA', 'RICO', 'ORTEGA', 'OJEDA'
]

MATERNAL_LASTNAMES = [
    'RODRIGUEZ', 'RIVERA', 'LUNA', 'GONZALEZ', 'ORTIZ', 'CHAVEZ', 'BARAJAS',
    'OCARANZA', 'SANCHEZ', 'CONTRERAS', 'IBARRA', 'SILVA', 'RESENDIZ', 'CARBAJAL',
    'VELAZQUEZ', 'FLORES', 'CONSTANTINO', 'BRICEÑO', 'JARAMILLO', 'HERNANDEZ',
    'RODRIGUEZ', 'GARCIA', 'MALAGON', 'ENRIQUEZ', 'MARTINEZ'
]

NAMES = [
    'ANA', 'JOSE', 'DOLORES', 'CLAUDIA', 'JUAN', 'GABRIEL', 'KARLA', 'PEDRO',
    'FELIPE', 'CARMEN', 'RAUL', 'DIANNE', 'YISSEL', 'JOSE', 'SANDRA', 'ALFREDO',
    'GLORIA', 'FRANCISCO', 'BEATRIZ', 'JOSE', 'DEYANI', 'JUAN', 'VIANEY', 'JAIRO', 'ANA'
]

MIDDLE_NAMES = [
    'IVAN', 'FERNANDA', 'LETICIA', 'LUIS', 'IVAN', 'ALEJANDRA', 'ROBERTO',
    'ELEAZAR', 'MARIANA', 'ANGELICA', 'AURORA', 'NEKIZ', 'ERANDENI', 'ALEJANDRO',
    'SAYIL', 'JAVIER', 'MONSERRAT', 'FERNANDA', 'RUBIA', 'ANTONIO', 'ARMANDO',
    'LAURA', 'JAVIER', 'ELVIRA', 'HUNABKU'
]

ID_STRINGS1 = [
    '311108916710432158320141ESC54', '413090517710432158320131ESC56',
    '310293503702434163120151ESC54', '414046500710432158320141ESC56',
    '415120856702434163120151ESC56', '414059779703132163720141ESC56',
    '415028707703133164820151ESC56', '415071002703132163720151ESC56',
    '415119557710432158320151ESC56', '414490219703216157220142ESC56',
    '414071614703216157220141ESC56', '414004243703131156720141ESC56',
    '414039821703131156720141ESC56', '415019938703132163720151ESC56',
    '413085519703131156820131ESC56', '413081140703216157420131ESC56',
    '415069885710433159620151ESC56', '414049154702434163120141ESC70',
    '413041021703216157220131ESC56', '310264343703216157220151ESC67',
    '415055736703216157220151ESC56', '312011851703216157220151ESC54',
    '415011279710433159620151ESC56', '415131227703131156720151ESC56',
    '415120100702434163120151ESC56'
]

ID_STRINGS2 = [
    '2021120152F10091994', '2019120152F16061993', '2021120152F15021994',
    '2020120152F24021995', '2016220151F12081993', '2021120152M03081996',
    '2021120152M30071995', '2021120152M14121994', '2021100000F23071994',
    '2021120152F08071991', '2020120152M09111994', '2019120141M27121987',
    '2021120152M03101995', '2020120152F01061995', '2021120152F11021996',
    '2020120152F06021995', '2021120152M29051995', '2019120151F02111992',
    '2019120152F05071993', '2020120152F05091994', '2020120152F07051995',
    '2020120152F29101995', '2021120152F11081996', '2021120152M13051990',
    '2020120152M24021995'
]

# Constants
CAMPUSES = ['702', '703', '704', '710', '713']
STUDENT_STATUSES = ['act', 'exa', 'ina']
PERIODS = ['I', 'V', 'E', 'C']

# FTP Configuration
FTP_HOST = 'ftp-server'
FTP_PORT = 21
FTP_USER = 'admin'
FTP_PASSWORD = 'password'
FTP_DIR = '/home/vsftpd/admin'
LOCAL_DIR = '/app/ftp_data'

def pad_string(s, length):
    """Pad a string with spaces to reach the specified length."""
    return s.ljust(length)

def generate_student_record():
    """Generate a single student record in the required fixed-width format."""
    paternal = random.choice(PATERNAL_LASTNAMES)
    maternal = random.choice(MATERNAL_LASTNAMES)
    name = random.choice(NAMES)
    middle = random.choice(MIDDLE_NAMES)
    id_string1 = random.choice(ID_STRINGS1)
    id_string2 = random.choice(ID_STRINGS2)
    
    # Create fixed-width format record
    record = (
        pad_string(paternal, 25) +
        pad_string(maternal, 25) +
        pad_string(f"{name} {middle}", 25) +
        pad_string(id_string1, 31) +
        pad_string(id_string2, 19)
    )
    
    return record

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

def get_active_period():
    """Determine which period is active based on the current date."""
    now = datetime.datetime.now()
    month = now.month
    
    # This is a simplified example - adjust the periods as needed
    if 1 <= month <= 3:
        return 'V'  # Period V (January-March)
    elif 4 <= month <= 6:
        return 'I'  # Period I (April-June)
    elif 7 <= month <= 9:
        return 'E'  # Period E (July-September)
    else:
        return 'C'  # Period C (October-December)

def generate_filename(campus, status, period):
    """Generate a filename based on the specified pattern."""
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    
    filename = f"dir_{campus}_{status}_{period}_{date_str}_{time_str}.txt"
    return filename

def generate_file(campus, status, period, records=50):
    """Generate a file with the specified parameters and synthetic data."""
    filename = generate_filename(campus, status, period)
    
    # Generate student records
    content = ""
    for _ in range(records):
        content += generate_student_record() + "\n"
    
    # Create the semester directory if it doesn't exist
    semester = get_current_semester()
    os.makedirs(os.path.join(LOCAL_DIR, semester), exist_ok=True)
    
    # Write the file
    filepath = os.path.join(LOCAL_DIR, semester, filename)
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Generated file: {filepath}")
    return filepath

def upload_file_to_ftp(filepath):
    """Upload a file to the FTP server."""
    try:
        # Connect to FTP server
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.set_pasv(True)  # Enable passive mode
        ftp.login(FTP_USER, FTP_PASSWORD)
        
        # Get semester directory name
        semester = get_current_semester()
        
        # Create semester directory locally if it doesn't exist
        local_semester_dir = os.path.join(LOCAL_DIR, semester)
        os.makedirs(local_semester_dir, exist_ok=True)
        
        # Upload directly to the admin directory (files will be visible from both local and FTP)
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            ftp.storbinary(f'STOR {filename}', f)
        
        ftp.quit()
        print(f"Uploaded {filename} to FTP server root directory")
        return True
    except Exception as e:
        print(f"Error uploading to FTP: {e}")
        return False

def generate_and_upload_files():
    """Generate and upload files for all campuses and statuses."""
    period = get_active_period()
    semester = get_current_semester()
    
    print(f"Generating files for semester {semester}, period {period}")
    
    for campus in CAMPUSES:
        for status in STUDENT_STATUSES:
            filepath = generate_file(campus, status, period)
            upload_file_to_ftp(filepath)

def schedule_tasks():
    """Set up the scheduler for periodic file generation."""
    # Run once at startup
    generate_and_upload_files()
    
    # Schedule to run daily
    schedule.every().day.at("00:00").do(generate_and_upload_files)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Ensure the local directory exists
    os.makedirs(LOCAL_DIR, exist_ok=True)
    
    # Start the scheduler
    print("Starting synthetic data generator...")
    schedule_tasks() 