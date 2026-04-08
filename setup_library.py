#!/usr/bin/env python3
"""
Quick setup script for MakerGit device library autocomplete feature
This script validates the environment and helps with initial setup
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

def check_python_version():
    """Ensure Python 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_postgres():
    """Check if PostgreSQL is available"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    print("❌ PostgreSQL not found. Please install PostgreSQL.")
    return False

def check_requirements():
    """Check if required Python packages are installed"""
    try:
        import asyncpg
        import fastapi
        import pydantic
        print("✅ Required Python packages installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("   Install with: pip install -r backend/requirements.txt")
        return False

def check_database_tables():
    """Check if database tables exist"""
    try:
        import asyncpg
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres@localhost:5432/makergit"
        )
        
        async def check():
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = $1",
                    "device_library"
                )
                await conn.close()
                return result > 0
            except:
                return False
        
        has_table = asyncio.run(check())
        if has_table:
            print("✅ Database tables exist")
            return True
        else:
            print("❌ Database tables not found")
            return False
    except Exception as e:
        print(f"⚠️  Could not check database: {e}")
        return False

def check_frontend_files():
    """Check if frontend files exist"""
    files = [
        'frontend/index.html',
        'frontend/app.js',
        'frontend/styles.css'
    ]
    
    all_exist = True
    for file in files:
        if not Path(file).exists():
            print(f"❌ Missing: {file}")
            all_exist = False
    
    if all_exist:
        print("✅ Frontend files present")
    return all_exist

def check_library_data():
    """Check if device library data exists"""
    if Path('docs/library_index.json').exists():
        print("✅ Library data file exists")
        return True
    else:
        print("❌ docs/library_index.json not found")
        return False

def print_setup_instructions():
    """Print helpful setup instructions"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║          MakerGit Library Autocomplete Setup Guide          ║
╚══════════════════════════════════════════════════════════════╝

1. CREATE DATABASE TABLES
   Run: psql -U postgres -d makergit -f db/schema.sql

2. LOAD DEVICE LIBRARY DATA
   Run: python3 db/load_device_library.py
   
   (Optional) Monitor progress:
   Watch library counts with:
   psql -c "SELECT COUNT(*) FROM device_library;"

3. INSTALL DEPENDENCIES (if not done)
   Run: pip install -r backend/requirements.txt

4. START BACKEND SERVER
   Run: cd backend && python -m uvicorn src.app:app --reload

5. START FRONTEND SERVER
   In another terminal:
   cd frontend && python -m http.server 8080
   
   Then visit: http://localhost:8080

6. TEST AUTOCOMPLETE
   - Go to "My Devices" tab
   - Start typing in "Device Type" field
   - Should see suggestions appear

═══════════════════════════════════════════════════════════════

ENVIRONMENT VARIABLES (Optional):
- DATABASE_URL: PostgreSQL connection string
  Default: postgresql://postgres@localhost:5432/makergit

API ENDPOINTS FOR TESTING:
- Device search: http://localhost:8000/api/library/library/devices/search?q=ESP32
- Component search: http://localhost:8000/api/library/library/components/search?q=resistor
- Library stats: http://localhost:8000/api/library/library/stats

TROUBLESHOOTING:
1. Check backend logs for errors
2. Verify database connection: 
   psql "postgresql://postgres@localhost:5432/makergit"
3. Ensure all tables created:
   psql -c "\\dt" | grep -E "(device_library|component_library|devices|boms)"
""")

def main():
    print("\n🔍 MakerGit Library Autocomplete - Environment Check\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("PostgreSQL", check_postgres),
        ("Python Packages", check_requirements),
        ("Database Tables", check_database_tables),
        ("Frontend Files", check_frontend_files),
        ("Library Data", check_library_data),
    ]
    
    passed = 0
    for name, check_func in checks:
        print(f"\n{name}:")
        if check_func():
            passed += 1
        print()
    
    print(f"\n{'='*60}")
    print(f"Summary: {passed}/{len(checks)} checks passed")
    print(f"{'='*60}\n")
    
    if passed < len(checks):
        print("⚠️  Some checks failed. Please review the instructions above.\n")
    else:
        print("✅ All checks passed! System is ready.\n")
    
    print_setup_instructions()

if __name__ == "__main__":
    main()
