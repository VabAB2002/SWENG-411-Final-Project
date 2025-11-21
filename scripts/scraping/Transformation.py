import json
import re
import unicodedata

# --- Configuration ---
INPUT_FILES = {
    "Majors": "Majors_cleaned.json",
    "Minors": "Minors_cleaned.json",
    "Certificates": "Certificates_cleaned.json"
}
OUTPUT_FILE = "academic_programs_rules.json"

def clean_text(text):
    """Removes non-breaking spaces and extra whitespace."""
    if not text: return ""
    # Normalize unicode (turns \u00a0 into standard space)
    text = unicodedata.normalize("NFKD", text)
    return " ".join(text.split())

def parse_credits_needed(section_title, section_desc):
    """
    Tries to extract the number of credits required from the title or description.
    Example: "Supporting Courses (select 6 credits)" -> returns 6
    """
    text = (section_title + " " + section_desc).lower()
    
    # Logic 1: Look for "select X credits"
    match = re.search(r"select\s+(\d+)(?:–\d+)?\s+credits", text)
    if match:
        return int(match.group(1))
    
    # Logic 2: Look for "X credits" in title if it contains "prescribed" or "required"
    if "prescribed" in text or "required" in text:
        match = re.search(r"\((\d+)(?:–\d+)?\s+credits\)", text)
        if match:
            return int(match.group(1))
            
    return 0 # Default to 0 (meaning 'take all' or unknown)

def determine_rule_type(section_title, section_desc):
    """Decides if a section is MANDATORY (AND) or SELECTIVE (OR)."""
    text = (section_title + " " + section_desc).lower()
    
    if "select" in text or "option" in text or "supporting" in text or "additional" in text:
        return "subset" # Pick X from List
    return "all" # Default to Mandatory

def transform_program(program_data, program_type):
    """Converts a single program entry into Engine-Ready format."""
    transformed = {
        "id": clean_text(program_data.get('programName', 'Unknown')),
        "type": program_type,
        "url": program_data.get('programUrl', ''),
        "rules": []
    }

    # Handle the nested 'allSections' or 'courseSections' depending on file structure
    # Your Major file uses 'coursesTabContent' -> 'allSections'
    # Your Minor file uses 'coursesTabContent' -> 'allSections' AND 'courseSections' (duplicate)
    
    sections = []
    if 'coursesTabContent' in program_data and 'allSections' in program_data['coursesTabContent']:
        sections = program_data['coursesTabContent']['allSections']
    elif 'courseSections' in program_data:
        sections = program_data['courseSections']

    for section in sections:
        title = clean_text(section.get('sectionTitle', ''))
        desc = clean_text(section.get('sectionDescription', ''))
        
        # Skip empty sections
        if not section.get('courses'):
            continue

        rule = {
            "name": title,
            "type": determine_rule_type(title, desc),
            "credits_needed": parse_credits_needed(title, desc),
            "courses": []
        }

        for course in section.get('courses', []):
            c_code = clean_text(course.get('courseCode', ''))
            
            # Clean "Course Code" edge cases (sometimes might have generic text)
            if len(c_code) < 4: continue 

            course_entry = {
                "code": c_code,
                "credits": course.get('credits', 3),
                # Store raw prereqs for the engine to parse later
                "prerequisites_raw": course.get('prerequisites', []) 
            }
            rule["courses"].append(course_entry)
            
        transformed["rules"].append(rule)
        
    return transformed

def main():
    master_database = []
    
    for p_type, filename in INPUT_FILES.items():
        print(f"Processing {p_type} from {filename}...")
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            for entry in data:
                processed = transform_program(entry, p_type)
                master_database.append(processed)
                
        except FileNotFoundError:
            print(f"⚠️ Warning: {filename} not found. Skipping.")

    # Save the clean, consolidated file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(master_database, f, indent=2)

    print(f"\n✅ Success! Generated '{OUTPUT_FILE}' with {len(master_database)} programs.")
    print("This file is now ready for the Recommendation Engine.")

if __name__ == "__main__":
    main()