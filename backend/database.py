"""
Database Access Layer for Supabase
Handles loading data from Supabase PostgreSQL and caching it in memory for fast access.

This module maintains the same performance characteristics as the original JSON file approach
by loading all data into memory at startup, while gaining the benefits of a proper database
for data management and updates.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check if credentials are configured
SUPABASE_CONFIGURED = (
    SUPABASE_URL and 
    SUPABASE_KEY and 
    "your-project-id" not in SUPABASE_URL and 
    "your_service_role_key" not in SUPABASE_KEY
)

# Only import supabase if configured
if SUPABASE_CONFIGURED:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except ImportError:
        print("⚠️  Warning: supabase package not installed")
        print("   Run: pip install supabase")
        SUPABASE_CONFIGURED = False
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to Supabase: {e}")
        SUPABASE_CONFIGURED = False

# In-memory cache (loaded at startup)
_cache = {
    "programs": None,
    "courses": None,
    "equivalencies": None,
    "prereq_config": None
}


def load_all_data():
    """
    Load all data from Supabase into memory at startup.
    
    This maintains current performance while using a database backend.
    Data is loaded once and cached in memory for fast access during runtime.
    
    Returns:
        tuple: (programs_list, courses_dict, equivalencies_dict, prereq_config_dict)
    
    Raises:
        Exception: If Supabase is not configured or connection fails
    """
    if not SUPABASE_CONFIGURED:
        raise Exception(
            "Supabase not configured. Please:\n"
            "1. Create a Supabase project at https://supabase.com\n"
            "2. Execute backend/scripts/create_schema.sql in Supabase SQL Editor\n"
            "3. Run backend/scripts/migrate_to_supabase.py to import data\n"
            "4. Update backend/.env with your Supabase credentials"
        )
    
    print("📥 Loading data from Supabase...")
    
    try:
        # Load programs
        print("   → Loading programs...")
        programs_response = supabase.table('programs').select('*').execute()
        programs = programs_response.data
        _cache['programs'] = programs
        print(f"   ✓ Loaded {len(programs)} programs")
        
        # Load courses (convert to dict with normalized code as key)
        print("   → Loading courses...")
        courses_response = supabase.table('courses').select('*').execute()
        courses_data = courses_response.data
        
        # Convert to dict format matching original JSON structure
        courses_dict = {}
        for c in courses_data:
            courses_dict[c['course_code_normalized']] = {
                'courseCode': c['course_code'],
                'title': c['title'],
                'credits': c['credits'],
                'description': c['description'],
                'prerequisites_list': c['prerequisites_list'],
                'prerequisites_raw': c['prerequisites_raw'],
                'genEdAttributes': c['gen_ed_attributes'],
                'culturalAttributes': c['cultural_attributes'],
                'interDomain': c['inter_domain'],
                'source_program': c['source_program']
            }
        
        _cache['courses'] = courses_dict
        print(f"   ✓ Loaded {len(courses_dict)} courses")
        
        # Load equivalencies (convert to dict)
        print("   → Loading course equivalencies...")
        equiv_response = supabase.table('course_equivalencies').select('*').execute()
        equiv_data = equiv_response.data
        
        equiv_dict = {}
        for e in equiv_data:
            equiv_dict[e['course_code']] = {
                'equivalents': e['equivalents'],
                'reason': e['reason'],
                'auto_generated': e['auto_generated'],
                'type': e['type']
            }
        
        _cache['equivalencies'] = equiv_dict
        print(f"   ✓ Loaded {len(equiv_dict)} equivalency mappings")
        
        # Load prerequisite config
        print("   → Loading prerequisite configuration...")
        config_response = supabase.table('prerequisite_config') \
            .select('config_value') \
            .eq('config_name', 'hierarchy_rules') \
            .execute()
        
        if config_response.data and len(config_response.data) > 0:
            prereq_config = config_response.data[0]['config_value']
        else:
            # Default config if not found in database
            prereq_config = {
                "hierarchy_rules": {
                    "enabled": True,
                    "same_department_higher_level": True,
                    "minimum_level_difference": 0
                }
            }
            print("   ⚠️  Using default prerequisite config (not found in database)")
        
        _cache['prereq_config'] = prereq_config
        print("   ✓ Loaded prerequisite configuration")
        
        print(f"✅ Database load complete: {len(programs)} programs, {len(courses_dict)} courses")
        
        return (
            _cache['programs'],
            _cache['courses'],
            _cache['equivalencies'],
            _cache['prereq_config']
        )
    
    except Exception as e:
        print(f"❌ Error loading data from Supabase: {e}")
        print("\nTroubleshooting:")
        print("1. Verify Supabase credentials in backend/.env")
        print("2. Ensure schema was created (run create_schema.sql)")
        print("3. Ensure data was migrated (run migrate_to_supabase.py)")
        print("4. Check Supabase dashboard for any service issues")
        raise


def get_cached_data():
    """
    Return cached data without reloading from database.
    
    If cache is empty, this will trigger a load from database.
    
    Returns:
        tuple: (programs_list, courses_dict, equivalencies_dict, prereq_config_dict)
    """
    if _cache['programs'] is None:
        return load_all_data()
    
    return (
        _cache['programs'],
        _cache['courses'],
        _cache['equivalencies'],
        _cache['prereq_config']
    )


def reload_cache():
    """
    Force reload of all data from database.
    
    Useful for development when data changes without restarting the server.
    
    Returns:
        tuple: (programs_list, courses_dict, equivalencies_dict, prereq_config_dict)
    """
    print("🔄 Reloading data from database...")
    _cache['programs'] = None
    _cache['courses'] = None
    _cache['equivalencies'] = None
    _cache['prereq_config'] = None
    return load_all_data()


def is_cache_loaded():
    """
    Check if cache is currently loaded.
    
    Returns:
        bool: True if cache is loaded, False otherwise
    """
    return _cache['programs'] is not None


# Optional: Functions for updating data (for future enhancements)

def update_program(program_id, updated_data):
    """
    Update a program in the database and refresh cache.
    
    Args:
        program_id (str): Program ID
        updated_data (dict): Updated program data
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not SUPABASE_CONFIGURED:
        return False
    
    try:
        supabase.table('programs').update(updated_data).eq('id', program_id).execute()
        reload_cache()
        return True
    except Exception as e:
        print(f"Error updating program: {e}")
        return False


def update_course(course_code, updated_data):
    """
    Update a course in the database and refresh cache.
    
    Args:
        course_code (str): Normalized course code
        updated_data (dict): Updated course data
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not SUPABASE_CONFIGURED:
        return False
    
    try:
        supabase.table('courses').update(updated_data).eq('course_code_normalized', course_code).execute()
        reload_cache()
        return True
    except Exception as e:
        print(f"Error updating course: {e}")
        return False


# Module-level initialization message
if SUPABASE_CONFIGURED:
    print("✓ Database module initialized (Supabase connected)")
else:
    print("⚠️  Database module initialized (Supabase not configured - please update .env)")

