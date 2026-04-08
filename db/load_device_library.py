#!/usr/bin/env python3
"""
Load device library data from library_index.json into PostgreSQL
Usage: python load_device_library.py
       or: DATABASE_URL="postgresql://user:pass@host/db" python load_device_library.py
"""

import json
import asyncpg
import os
import sys
from pathlib import Path
import getpass

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL not set, prompt for connection details
if not DATABASE_URL:
    print("PostgreSQL Connection Details Needed")
    print("=" * 50)
    
    host = input("Host [localhost]: ").strip() or "localhost"
    port = input("Port [5432]: ").strip() or "5432"
    user = input("Username [postgres]: ").strip() or "postgres"
    password = getpass.getpass("Password: ")
    database = input("Database [makergit]: ").strip() or "makergit"
    
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    print("\nConnecting to database...")
    print(f"Host: {host}, Database: {database}\n")

async def load_device_library():
    """Load device library from JSON and insert into PostgreSQL"""
    
    # Read library_index.json
    docs_path = Path(__file__).parent.parent / "docs" / "library_index.json"
    
    if not docs_path.exists():
        print(f"Error: {docs_path} not found")
        sys.exit(1)
    
    with open(docs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    libraries = data.get('libraries', [])
    print(f"Found {len(libraries)} library entries to load")
    
    # Connect to database
    try:
        pool = await asyncpg.create_pool(DATABASE_URL)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)
    
    async with pool.acquire() as conn:
        # Clear existing data (optional - comment out if you want to keep existing)
        # await conn.execute("DELETE FROM device_library")
        
        inserted_count = 0
        skipped_count = 0
        
        for library in libraries:
            try:
                # Extract data from library entry
                name = library.get('name', '')
                version = library.get('version', '')
                author = library.get('author', '')
                category = library.get('category', '')
                architectures = library.get('architectures', [])
                types = library.get('types', [])
                description = library.get('sentence', '')
                repository = library.get('repository', '')
                website = library.get('website', '')
                
                # Create keywords from name and category
                keywords = [name.lower(), category.lower() if category else '']
                if library.get('sentence'):
                    # Extract some key words from sentence
                    keywords.extend([word.lower() for word in library.get('sentence', '').split() if len(word) > 3])
                keywords = list(set(filter(None, keywords)))  # Remove duplicates and empty strings
                
                # Check if already exists (by name and version)
                existing = await conn.fetchrow(
                    "SELECT id FROM device_library WHERE name = $1 AND version = $2",
                    name, version
                )
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Insert into database
                await conn.execute(
                    """
                    INSERT INTO device_library (
                        name, version, author, category, architectures, types,
                        description, repository, website, keywords
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    name, version, author, category, architectures, types,
                    description, repository, website, keywords
                )
                inserted_count += 1
                
            except Exception as e:
                print(f"Error inserting {library.get('name', 'unknown')}: {e}")
                continue
        
        print(f"\nMigration complete:")
        print(f"  - Inserted: {inserted_count}")
        print(f"  - Skipped (already exists): {skipped_count}")
        print(f"  - Total processed: {inserted_count + skipped_count}")
    
    await pool.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(load_device_library())
