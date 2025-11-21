import re
import json

# --- MOCK DATA FROM YOUR UPLOAD ---
test_cases = [
    {
        "code": "AGBM 106",
        "raw": "AGBM 101 or ECON 102 or STAT 200 or STAT 240 or STAT 250 or SCM 200"
    },
    {
        "code": "CMPSC 200",
        "raw": "MATH 140 or MATH 140A or MATH 140B or MATH 140E or MATH 140G or MATH 140H Enforced Concurrent at Enrollment: MATH 141 or MATH 141B or MATH 141E or MATH 141G or MATH 141H Recommended Preparation: MATH 220"
    },
    {
        "code": "ENGL 202D",
        "raw": "4th Semester standing and one of the following courses: ENGL 15 or ENGL 15A or ENGL 15S or ENGL 15E or ESL 15 or ENGL 30H or ENGL 30T or ENGL 137H or CAS 137H"
    }
]

def extract_course_codes(text_chunk):
    """Finds all strings that look like 'MATH 140' or 'ENGL 15A'"""
    # Regex: 2-5 letters, space, 1-4 digits, optional 1 letter suffix
    return re.findall(r"([A-Z]{2,5}\s+\d{1,4}[A-Z]?)", text_chunk)

def parse_prerequisites(raw_text):
    """
    Converts raw text into a Logic Tree.
    Structure: [Group1, Group2]
    Where Group is a list of OPTIONS (OR logic).
    The Groups are combined via AND logic.
    """
    if not raw_text or "None" in raw_text:
        return []

    # 1. Clean up the "Noise"
    # Replace "Enforced Concurrent..." with a special splitter " AND "
    # This treats Concurrent courses as a requirement (AND)
    clean_text = raw_text.replace("Enforced Concurrent at Enrollment:", " AND ")
    clean_text = clean_text.replace("Enforced Prerequisite at Enrollment:", "")
    
    # Remove "Recommended Preparation" (Usually not required for cost)
    if "Recommended Preparation" in clean_text:
        clean_text = clean_text.split("Recommended Preparation")[0]

    # 2. Split by "AND" keywords (including our custom one)
    # This creates high-level groups that ALL must be satisfied
    and_groups = re.split(r" AND | and |;", clean_text)
    
    logic_tree = []
    
    for group in and_groups:
        # 3. Inside a group, find all OPTIONS (OR logic)
        # We extract just the codes. If they are in the same string separated by 'or', they are options.
        
        # Find all codes in this chunk
        codes = extract_course_codes(group)
        
        # If we found codes, add them as a list of options
        if codes:
            # Remove duplicates in the option list
            unique_options = list(set(codes))
            logic_tree.append(unique_options)
            
    return logic_tree

# --- RUN THE TEST ---
print(f"{'COURSE':<10} | {'PARSED LOGIC TREE (Outer list = AND, Inner list = OR)'}")
print("-" * 80)

for case in test_cases:
    tree = parse_prerequisites(case['raw'])
    print(f"{case['code']:<10} | {json.dumps(tree)}")