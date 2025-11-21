import json
import unicodedata

# --- CONFIGURATION ---
RULES_FILE = 'academic_programs_rules.json'          # Your Main Structure
METADATA_FILE = 'gened_courses_golden_record.json'   # Your Data Source
OUTPUT_FILE = 'academic_programs_rules_enriched.json' # The Final Product
MISSING_FILE = 'courses_missing_metadata.json'       # The Log of what we missed

def normalize_code(code):
    """
    Standardizes course codes to ensure matching works.
    Example: "ACCTG 201" -> "ACCTG201"
    """
    if not code: return ""
    # Remove spaces and non-breaking spaces, convert to UPPER
    return "".join(ch for ch in code if ch.isalnum()).upper()

def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Could not find {filename}")
        return None

def main():
    print("🚀 Starting Data Enrichment Process...")

    # 1. Load Files
    rules_data = load_json(RULES_FILE)
    metadata_list = load_json(METADATA_FILE)

    if not rules_data or not metadata_list:
        return

    # 2. Convert Metadata List to a Fast Lookup Dictionary
    print("   ... Indexing Golden Record")
    golden_db = {}
    for item in metadata_list:
        code = normalize_code(item.get('courseCode', ''))
        if code:
            golden_db[code] = item

    # 3. Iterate and Enrich
    print("   ... Merging Data")
    missing_courses = set() 
    enriched_count = 0

    for program in rules_data:
        for rule in program.get('rules', []):
            
            # Function to enrich a single course object
            def enrich_course(course_obj):
                nonlocal enriched_count
                code_raw = course_obj.get('code', '')
                code_norm = normalize_code(code_raw)
                
                if code_norm in golden_db:
                    # MATCH FOUND! Merge data.
                    gold_data = golden_db[code_norm]
                    
                    # --- NEW: Add Title and URL ---
                    course_obj['title'] = gold_data.get('title', '')
                    course_obj['detailsUrl'] = gold_data.get('detailsUrl', '')
                    
                    # Inject GenEd Attributes
                    course_obj['genEdAttributes'] = gold_data.get('genEdAttributes', [])
                    
                    # Inject Inter-Domain status
                    course_obj['interDomain'] = gold_data.get('interDomain', False)
                    
                    enriched_count += 1
                else:
                    # NO MATCH. Log it.
                    missing_courses.add(code_raw)

            # A. Check standard course lists
            for course in rule.get('courses', []):
                enrich_course(course)

            # B. Check Dynamic Subsets (Secondary Pool)
            if rule.get('type') == 'dynamic_subset':
                constraints = rule.get('constraints', {})
                secondary = constraints.get('secondary_pool', {}).get('courses', [])
                
                # Note: Secondary pool usually lists strings, not objects.
                # We check them for reporting, but can't easily enrich strings 
                # without changing the data structure.
                for c_code in secondary:
                    if normalize_code(c_code) not in golden_db:
                        missing_courses.add(c_code)

            # C. Check Group Options (Accounting Split)
            if rule.get('type') == 'group_option':
                for group in rule.get('groups', []):
                    for course in group.get('courses', []):
                        enrich_course(course)

    # 4. Save Results
    print(f"   ... Saving Enriched Data to '{OUTPUT_FILE}'")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(rules_data, f, indent=2)

    # 5. Save Missing Report
    # Convert set to sorted list of objects for nicer reading
    missing_report = [{"code": c, "reason": "Not found in Golden Record"} for c in sorted(list(missing_courses))]
    
    with open(MISSING_FILE, 'w') as f:
        json.dump(missing_report, f, indent=2)

    print("\n✅ DONE!")
    print(f"   - Enriched {enriched_count} course instances with Titles & URLs.")
    print(f"   - Identified {len(missing_courses)} unique courses missing metadata.")
    print("   - Your 'academic_programs_rules_enriched.json' now has full details.")

if __name__ == "__main__":
    main()