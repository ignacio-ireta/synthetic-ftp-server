# FTP Server with Synthetic Data Generation

This project implements a Docker-based FTP server that periodically receives synthetic student data files. The data files follow a specific naming convention and structure based on semesters, campuses, student statuses, and periods.

## Project Structure

- `docker-compose.yml`: Docker Compose configuration for the FTP server and data generator
- `Dockerfile.generator`: Dockerfile for the Python data generator
- `data_generator.py`: Python script for generating and uploading synthetic data
- `verify_system.py`: Script to verify the system is working correctly
- `requirements.txt`: Python dependencies for the data generator

## File Naming Convention

Files follow this naming pattern: `dir_{campus}_{student_status}_{period}_{YYYYMMDD}_{HHMMSS}.txt`

Where:
- `campus`: One of 702, 703, 704, 710, 713
- `student_status`: One of act (active), exa (external), ina (inactive)
- `period`: One of I, V, E, C
- `YYYYMMDD`: Current date
- `HHMMSS`: Current time

## File Structure

Each file contains synthetic student data in a fixed-width format:
- Paternal lastname: positions 0-24
- Maternal lastname: positions 25-49
- Name and middle name: positions 50-74
- ID string 1: positions 75-105
- ID string 2: positions 106-124

## Semester Folders

Files are organized into semester folders:
- July-December: first semester of upcoming year (e.g., July-Dec 2015 → "dir2016-1")
- January-June: second semester of current year (e.g., Jan-June 2016 → "dir2016-2")

Each semester contains 60 text files (5 campuses × 3 student statuses × 4 periods).

## Period Schedule

- Period V: January-March
- Period I: April-June
- Period E: July-September
- Period C: October-December

## Setup Instructions

1. Install Docker and Docker Compose
2. Clone this repository
3. Start the system:
   ```
   docker-compose up -d
   ```
4. Verify the system:
   ```
   docker exec -it data-generator python verify_system.py
   ```

## FTP Connection Details

- Host: localhost
- Port: 21
- Username: admin
- Password: password
- Passive mode port range: 21000-21010

## Customization

You can customize the following in `docker-compose.yml`:
- FTP user credentials
- Port mappings
- Volume mounts

In `data_generator.py`, you can customize:
- Synthetic data dictionaries
- File generation frequency
- Number of records per file 