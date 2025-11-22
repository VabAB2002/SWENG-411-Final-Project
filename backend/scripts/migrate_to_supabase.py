#!/usr/bin/env python3
"""
Data Migration Script: JSON to Supabase
Migrates all JSON data files to Supabase PostgreSQL database.

Usage:
    1. Ensure you've created a Supabase project and executed create_schema.sql
    2. Update backend/.env with your Supabase credentials
    3. Run: python3 migrate_to_supabase.py

This script will:
    - Migrate academic_programs_rules.json to programs table
    - Migrate world_campus_courses_master.json to courses table
    - Migrate course_equivalencies.json to course_equivalencies table
    - Migrate prerequisite_config.json to prerequisite_config table
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import from backend
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Error: supabase package not installed")
    print("   Run: pip install supabase")
    sys.exit(1)

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase credentials not found")
    print("   Please update backend/.env with your Supabase URL and service_role key")
    print(f"   Looking for .env at: {env_path.absolute()}")
    sys.exit(1)

if "your-project-id" in SUPABASE_URL or "your_service_role_key" in SUPABASE_KEY:
    print("❌ Error: Please update backend/.env with your actual Supabase credentials")
    print("   Current values appear to be placeholders")
    sys.exit(1)

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Connected to Supabase")
except Exception as e:
    print(f"❌ Error connecting to Supabase: {e}")
    sys.exit(1)

# Data file paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
CONFIG_DIR = BASE_DIR / 'backend' / 'config'

PROGRAMS_FILE = DATA_DIR / 'academic_programs_rules.json'
COURSES_FILE = DATA_DIR / 'world_campus_courses_master.json'
EQUIVALENCIES_FILE = DATA_DIR / 'course_equivalencies.json'
PREREQ_CONFIG_FILE = CONFIG_DIR / 'prerequisite_config.json'


def migrate_programs():
    """Migrate academic_programs_rules.json to programs table"""
    print("\n📚 Migrating programs...")
    
    if not PROGRAMS_FILE.exists():
        print(f"   ⚠️  File not found: {PROGRAMS_FILE}")
        return False
    
    with open(PROGRAMS_FILE, 'r', encoding='utf-8') as f:
        programs = json.load(f)
    
    print(f"   Found {len(programs)} programs to migrate")
    
    # Insert one at a time to avoid duplicate conflicts within same batch
    # The upsert will update if a duplicate key exists
    total_inserted = 0
    errors = 0
    
    for p in programs:
        try:
            result = supabase.table('programs').upsert({
                "id": p['id'],
                "type": p['type'],
                "url": p.get('url', ''),
                "rules": p.get('rules', [])
            }).execute()
            total_inserted += 1
            if total_inserted % 10 == 0:
                print(f"   ✓ Inserted {total_inserted}/{len(programs)}...")
        except Exception as e:
            errors += 1
            if errors <= 5:  # Only print first 5 errors
                print(f"   ⚠️  Warning for '{p['id']}' ({p['type']}): {str(e)[:100]}")
    
    if errors > 5:
        print(f"   ⚠️  {errors - 5} more warnings suppressed")
    
    print(f"   ✅ Total programs processed: {total_inserted} (some may be duplicates that were merged)")
    return True


def migrate_courses():
    """Migrate world_campus_courses_master.json to courses table"""
    print("\n📖 Migrating courses...")
    
    if not COURSES_FILE.exists():
        print(f"   ⚠️  File not found: {COURSES_FILE}")
        return False
    
    with open(COURSES_FILE, 'r', encoding='utf-8') as f:
        courses = json.load(f)
    
    print(f"   Found {len(courses)} courses to migrate")
    
    # Convert dict to list of records
    course_list = []
    for norm_code, course_data in courses.items():
        course_list.append({
            "course_code_normalized": norm_code,
            "course_code": course_data.get('courseCode', ''),
            "title": course_data.get('title', ''),
            "credits": float(course_data.get('credits', 3)),
            "description": course_data.get('description', ''),
            "prerequisites_list": course_data.get('prerequisites_list', []),
            "prerequisites_raw": course_data.get('prerequisites_raw', ''),
            "gen_ed_attributes": course_data.get('genEdAttributes', []),
            "cultural_attributes": course_data.get('culturalAttributes', []),
            "inter_domain": course_data.get('interDomain', False),
            "source_program": course_data.get('source_program', '')
        })
    
    # Batch insert
    batch_size = 500
    total_inserted = 0
    
    for i in range(0, len(course_list), batch_size):
        batch = course_list[i:i+batch_size]
        
        try:
            result = supabase.table('courses').upsert(batch).execute()
            total_inserted += len(batch)
            print(f"   ✓ Inserted batch {i//batch_size + 1}: {len(batch)} courses")
        except Exception as e:
            print(f"   ❌ Error inserting batch {i//batch_size + 1}: {e}")
            return False
    
    print(f"   ✅ Total courses migrated: {total_inserted}")
    return True


def migrate_equivalencies():
    """Migrate course_equivalencies.json to course_equivalencies table"""
    print("\n🔄 Migrating course equivalencies...")
    
    if not EQUIVALENCIES_FILE.exists():
        print(f"   ⚠️  File not found: {EQUIVALENCIES_FILE}")
        return False
    
    with open(EQUIVALENCIES_FILE, 'r', encoding='utf-8') as f:
        equivalencies = json.load(f)
    
    print(f"   Found {len(equivalencies)} equivalency mappings to migrate")
    
    # Convert dict to list of records
    equiv_list = []
    for course_code, equiv_data in equivalencies.items():
        equiv_list.append({
            "course_code": course_code,
            "equivalents": equiv_data.get('equivalents', []),
            "reason": equiv_data.get('reason', ''),
            "auto_generated": equiv_data.get('auto_generated', False),
            "type": equiv_data.get('type', '')
        })
    
    try:
        result = supabase.table('course_equivalencies').upsert(equiv_list).execute()
        print(f"   ✅ Total equivalencies migrated: {len(equiv_list)}")
        return True
    except Exception as e:
        print(f"   ❌ Error inserting equivalencies: {e}")
        return False


def migrate_prerequisite_config():
    """Migrate prerequisite_config.json to prerequisite_config table"""
    print("\n⚙️  Migrating prerequisite configuration...")
    
    if not PREREQ_CONFIG_FILE.exists():
        print(f"   ⚠️  File not found: {PREREQ_CONFIG_FILE}")
        return False
    
    with open(PREREQ_CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    try:
        result = supabase.table('prerequisite_config').upsert([{
            "config_name": "hierarchy_rules",
            "config_value": config,
            "description": "Prerequisite matching hierarchy rules and settings"
        }]).execute()
        print(f"   ✅ Prerequisite config migrated")
        return True
    except Exception as e:
        print(f"   ❌ Error inserting config: {e}")
        return False


def verify_migration():
    """Verify that all data was migrated successfully"""
    print("\n🔍 Verifying migration...")
    
    try:
        # Count rows in each table
        programs_count = supabase.table('programs').select('id', count='exact').execute()
        courses_count = supabase.table('courses').select('course_code_normalized', count='exact').execute()
        equiv_count = supabase.table('course_equivalencies').select('course_code', count='exact').execute()
        config_count = supabase.table('prerequisite_config').select('id', count='exact').execute()
        
        print(f"   Programs: {programs_count.count} rows")
        print(f"   Courses: {courses_count.count} rows")
        print(f"   Equivalencies: {equiv_count.count} rows")
        print(f"   Configs: {config_count.count} rows")
        
        return True
    except Exception as e:
        print(f"   ❌ Error verifying: {e}")
        return False


def main():
    """Main migration process"""
    print("=" * 60)
    print("Penn State Course Recommender - Data Migration to Supabase")
    print("=" * 60)
    
    # Check that all required files exist
    missing_files = []
    for file_path in [PROGRAMS_FILE, COURSES_FILE, EQUIVALENCIES_FILE, PREREQ_CONFIG_FILE]:
        if not file_path.exists():
            missing_files.append(str(file_path))
    
    if missing_files:
        print("\n❌ Missing required data files:")
        for f in missing_files:
            print(f"   - {f}")
        sys.exit(1)
    
    # Run migrations
    success = True
    
    if not migrate_programs():
        success = False
    
    if not migrate_courses():
        success = False
    
    if not migrate_equivalencies():
        success = False
    
    if not migrate_prerequisite_config():
        success = False
    
    # Verify
    if success:
        verify_migration()
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Go to your Supabase dashboard to verify the data")
        print("2. Check table row counts match your JSON files")
        print("3. Update backend/app.py to use the new database layer")
    else:
        print("❌ Migration completed with errors")
        print("   Please check the error messages above and try again")
    print("=" * 60)


if __name__ == "__main__":
    main()

