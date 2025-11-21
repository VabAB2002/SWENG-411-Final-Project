import json
import re
import unicodedata

# --- CONFIGURATION ---
INPUT_FILES = {
    "Majors": "Majors_cleaned.json",
    "Minors": "Minors_cleaned.json",
    "Certificates": "Certificates_cleaned.json"
}
OUTPUT_FILE = "academic_programs_rules.json"

def clean_text(text):
    if not text: return ""
    text = unicodedata.normalize("NFKD", text)
    return " ".join(text.split())

def parse_credits_needed(section_title, section_desc):
    text = (section_title + " " + section_desc).lower()
    match = re.search(r"select\s+(\d+)(?:–\d+)?\s+credits", text)
    if match: return int(match.group(1))
    match = re.search(r"\((\d+)(?:–\d+)?\s+credits\)", text)
    if match: return int(match.group(1))
    return 0

def determine_rule_type(section_title, section_desc):
    text = (section_title + " " + section_desc).lower()
    if "select" in text or "option" in text or "supporting" in text or "additional" in text or "electives" in text:
        return "subset" 
    return "all"

def transform_program(program_data, program_type):
    transformed = {
        "id": clean_text(program_data.get('programName', 'Unknown')),
        "type": program_type,
        "url": program_data.get('programUrl', '#'),
        "rules": []
    }

    sections = []
    if 'coursesTabContent' in program_data and program_data['coursesTabContent']:
        if 'allSections' in program_data['coursesTabContent']:
            sections = program_data['coursesTabContent']['allSections']
    elif 'courseSections' in program_data:
        sections = program_data['courseSections']

    if not sections: return None

    for section in sections:
        title = clean_text(section.get('sectionTitle', ''))
        desc = clean_text(section.get('sectionDescription', ''))
        
        if not section.get('courses'): continue

        rule_type = determine_rule_type(title, desc)
        credits_needed = parse_credits_needed(title, desc)
        
        if rule_type == "all" and credits_needed == 0:
            total_cr = 0
            for c in section.get('courses', []):
                try: total_cr += float(c.get('credits', 3))
                except: total_cr += 3
            credits_needed = int(total_cr)

        rule = {
            "name": title,
            "type": rule_type,
            "credits_needed": credits_needed,
            "courses": []
        }

        for course in section.get('courses', []):
            c_code = clean_text(course.get('courseCode', ''))
            if len(c_code) < 2: continue 
            
            # --- NEW: Capture Metadata ---
            course_entry = {
                "code": c_code,
                "credits": course.get('credits', 3),
                "title": clean_text(course.get('title', '')),
                "description": clean_text(course.get('description', '')),
                # 'additionalInfo' often contains the raw prereq text
                "prerequisites_text": clean_text(course.get('additionalInfo', '')), 
                # Keep the list for logic
                "prerequisites_list": course.get('prerequisites', [])
            }
            rule["courses"].append(course_entry)
            
        transformed["rules"].append(rule)
        
    return transformed

def apply_logic_patches(database):
    # (Keep your Business Minor patch here exactly as before)
    for prog in database:
        if prog['id'] == "Business" and prog['type'] == "Minors":
            print("   ✨ Applying Patch: Business Minor")
            new_rules = []
            
            # Manually recreate Accounting with metadata manually added since we are hardcoding
            new_rules.append({
                "name": "Accounting Foundation",
                "type": "group_option",
                "groups": [
                    {"name": "Option A", "courses": [{"code": "ACCTG 211", "credits": 4, "title": "Financial/Managerial Accounting", "prerequisites_text": "Prerequisite: MATH 21"}]},
                    {"name": "Option B", "courses": [{"code": "ACCTG 201", "credits": 3, "title": "Intro to Financial Accounting"}, {"code": "ACCTG 202", "credits": 3, "title": "Intro to Managerial Accounting"}]}
                ]
            })
            # (Simplified Business Core for brevity - engine will use backups for metadata if missing here)
            new_rules.append({
                "name": "Business Core", "type": "all", "credits_needed": 6,
                "courses": [{"code": "MGMT 301", "credits": 3}, {"code": "MKTG 301W", "credits": 3}]
            })
            
            for rule in prog['rules']:
                if "Additional" in rule['name']:
                    rule['type'] = 'subset'
                    rule['credits_needed'] = 3
                    new_rules.append(rule)
                elif "Supporting" in rule['name']:
                    rule['type'] = 'dynamic_subset'
                    rule['credits_needed'] = 6
                    rule['constraints'] = {
                        "primary_pool": {
                            "description": "400-level Business Courses",
                            "min_credits_needed": 3,
                            "departments": ["ACCTG", "BA", "EBF", "ECON", "ENTR", "FIN", "HPA", "IB", "LHR", "MIS", "MGMT", "MKTG", "SCM", "STAT"],
                            "level_min": 400, "level_max": 499
                        },
                        "secondary_pool": {"courses": [c['code'] for c in rule['courses']]}
                    }
                    new_rules.append(rule)
            prog['rules'] = new_rules
            
        # Economics Patch
        if prog['id'] == "Economics" and prog['type'] == "Minors":
             for rule in prog['rules']:
                if "Supporting" in rule['name']:
                    rule['type'] = 'dynamic_subset'
                    rule['credits_needed'] = 6
                    rule['constraints'] = {
                        "primary_pool": { "description": "400-level Economics", "min_credits_needed": 0, "departments": ["ECON"], "level_min": 400, "level_max": 499 },
                        "secondary_pool": { "courses": [c['code'] for c in rule['courses']] }
                    }

def main():
    master_database = []
    print("🚀 Starting Data Transformation (v2 - Rich Metadata)...")

    for p_type, filename in INPUT_FILES.items():
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            for entry in data:
                processed = transform_program(entry, p_type)
                if processed: master_database.append(processed)
        except FileNotFoundError:
            print(f"   ⚠️ Warning: {filename} not found.")

    apply_logic_patches(master_database)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(master_database, f, indent=2)

    print(f"\n✅ Success! Generated '{OUTPUT_FILE}' with Titles & Descriptions.")

if __name__ == "__main__":
    main()