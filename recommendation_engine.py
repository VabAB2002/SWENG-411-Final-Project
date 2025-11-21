import json
import re

# --- 1. CONFIGURATION ---
PROGRAMS_FILE = 'academic_programs_rules_enriched.json'       
COURSES_FILE = 'gened_courses_golden_record.json'    

def normalize_code(code):
    """
    Aggressive normalization: "ACCTG 201" -> "ACCTG201"
    Handles: "MATH 021" -> "MATH021" and "MATH 21" -> "MATH21"
    """
    if not code: return ""
    # Remove spaces and non-alphanumeric, but keep structure
    normalized = ''.join(ch for ch in code if ch.isalnum()).upper()
    
    # Special handling: Pad single-digit course numbers to 3 digits for comparison
    # This helps match "MATH 21" with "MATH 021"
    match = re.match(r"([A-Z]+)(\d+)([A-Z]?)", normalized)
    if match:
        dept = match.group(1)
        number = match.group(2)
        suffix = match.group(3) or ""
        
        # Pad to 3 digits for courses < 100
        if len(number) <= 2:
            number = number.zfill(3)  # "21" -> "021"
        
        return f"{dept}{number}{suffix}"
    
    return normalized

def parse_course_number(code):
    """
    Extract department and course number for comparison
    Returns: (dept, number) e.g. ("MATH", 140)
    """
    if not code: return None, 0
    normalized = normalize_code(code)
    match = re.match(r"([A-Z]+)(\d+)", normalized)
    if match:
        return match.group(1), int(match.group(2))
    return None, 0

def expand_user_history_with_equivalencies(user_history, courses_db):
    """
    🔥 KEY FIX: Add implied course equivalencies
    
    If student has MATH 140, they automatically satisfy:
    - MATH 021 (basic math)
    - MATH 026 (pre-calculus) 
    - Any lower-level math
    
    This prevents the algorithm from adding phantom prerequisite costs.
    """
    expanded_history = set(user_history)
    
    # Common prerequisite equivalency rules for Penn State
    equivalency_rules = {
        # Math sequence: Higher courses satisfy all lower ones
        'MATH': {
            140: [21, 26, 40, 41, 110],      # Calculus I satisfies all pre-calc
            141: [21, 26, 40, 41, 110, 140], # Calculus II satisfies Calc I + below
            220: [21, 26, 110, 140, 141],    # Matrices satisfies calc sequence
            230: [21, 26, 110, 140, 141, 220],
            250: [21, 26, 110, 140, 141, 220, 230],
        },
        # English sequence
        'ENGL': {
            15: [10],      # ENGL 15 satisfies ENGL 10 if listed
            30: [10, 15],  # ENGL 30 satisfies both
            202: [15, 30], # Writing courses satisfy composition
        },
        # Computer Science sequence
        'CMPSC': {
            121: [101],    # CMPSC 121 satisfies intro programming
            131: [101, 121],
            132: [101, 121, 131],
        },
        # Chemistry sequence
        'CHEM': {
            110: [100],
            111: [100, 110],
        },
        # Physics sequence  
        'PHYS': {
            211: [200, 201],
            212: [200, 201, 211],
        },
        # Statistics
        'STAT': {
            200: [100],
            414: [200, 250],
            415: [200, 250, 414],
        }
    }
    
    # Check each course in user's history
    for completed_course in user_history:
        dept, number = parse_course_number(completed_course)
        if not dept or number == 0:
            continue
            
        # Check if this department has equivalency rules
        if dept in equivalency_rules:
            # Generic rule: Any 200+ level course satisfies 100-level in same dept
            # (Unless specifically listed in dict keys)
            if number >= 200:
                 # Add common lower level markers
                 expanded_history.add(normalize_code(f"{dept}100"))

            # Specific rule lookup
            # We check all keys in the rulebook. If user has a higher/equal course, grant the lower ones.
            for key_num, granted_list in equivalency_rules[dept].items():
                if number >= key_num:
                    for granted_num in granted_list:
                        expanded_history.add(normalize_code(f"{dept}{granted_num}"))
    
    return list(expanded_history)

def clean_prereq_for_display(raw_text):
    """
    Returns None if there are no real prerequisites, hiding the Info button.
    """
    if not raw_text: return None
    text = str(raw_text).strip()
    if text in ["None", "[]", "", "['None']"]: return None
    if text.lower() == "none": return None
    return text

def build_backup_db(programs_db):
    """
    Extracts course definitions from the Enriched Rules file.
    """
    backup_db = {}
    
    for prog in programs_db:
        for rule in prog.get('rules', []):
            
            # Helper to add course to db
            def add_course(c):
                code = normalize_code(c.get('code', ''))
                if not code: return
                
                raw_p = c.get('prerequisites_text', '')
                if not raw_p:
                    raw_p = str(c.get('prerequisites_list', []))

                backup_db[code] = {
                    "courseCode": c.get('code'),
                    "credits": c.get('credits', 3),
                    "title": c.get('title', ''), 
                    "prerequisites_raw": "", # Empty for logic to avoid loops
                    "prerequisites_display": raw_p,
                    "genEdAttributes": c.get('genEdAttributes', []) 
                }

            # 1. Standard lists
            for c in rule.get('courses', []):
                add_course(c)

            # 2. Group Options
            if rule.get('type') == 'group_option':
                for group in rule.get('groups', []):
                    for c in group.get('courses', []):
                        add_course(c)

    print(f"   -> Extracted {len(backup_db)} course definitions from Rules.")
    return backup_db

def load_data():
    print("Loading database...")
    try:
        with open(PROGRAMS_FILE, 'r') as f:
            programs_db = json.load(f)
        
        with open(COURSES_FILE, 'r') as f:
            raw_courses = json.load(f)
            courses_db = {normalize_code(c['courseCode']): c for c in raw_courses}
            
        backup_db = build_backup_db(programs_db)
        
        for code, data in backup_db.items():
            if code in courses_db:
                existing_geneds = courses_db[code].get('genEdAttributes', [])
                courses_db[code].update(data)
                if not data.get('genEdAttributes') and existing_geneds:
                     courses_db[code]['genEdAttributes'] = existing_geneds
            else:
                data['prerequisites_raw'] = data.pop('prerequisites_display', '')
                courses_db[code] = data
                
        print(f"Loaded {len(programs_db)} Programs.")
        print(f"Loaded {len(courses_db)} Total Courses.")
        return programs_db, courses_db
        
    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: Missing file. {e}")
        return [], {}

# --- 2. PARSING & UTILS ---

def get_course_credits(code, courses_db, default=3.0):
    norm_code = normalize_code(code)
    if norm_code in courses_db:
        try:
            val = str(courses_db[norm_code].get('credits', default)).split('-')[0]
            return float(val)
        except: return default
    return default

def extract_course_codes(text_chunk):
    return re.findall(r"([A-Z]{2,5}\s+\d{1,4}[A-Z]?)", text_chunk)

def parse_prerequisites_to_tree(raw_text):
    if not raw_text or "None" in raw_text: return []
    clean_text = raw_text.replace("Enforced Concurrent at Enrollment:", " AND ").replace("Enforced Prerequisite at Enrollment:", "")
    if "Recommended Preparation" in clean_text: clean_text = clean_text.split("Recommended Preparation")[0]
    and_groups = re.split(r" AND | and |;", clean_text)
    logic_tree = []
    for group in and_groups:
        codes = extract_course_codes(group)
        if codes:
            logic_tree.append(list(set(codes)))
    return logic_tree

# --- 3. COST CALCULATOR (WITH FIX) ---

def calculate_recursive_cost(code, expanded_history, courses_db, visited=None, known_credits=None):
    """
    🔥 FIXED: Now uses expanded history with equivalencies
    """
    norm_code = normalize_code(code)
    
    # Check against expanded history (includes implied prerequisites)
    if norm_code in expanded_history:
        return 0
    
    if visited is None: visited = set()
    if norm_code in visited: return 0
    visited.add(norm_code)

    # Get course's own cost
    if norm_code in courses_db:
        own_cost = get_course_credits(norm_code, courses_db)
    elif known_credits is not None:
        own_cost = float(known_credits)
    else:
        own_cost = 3.0
    
    # If course not in database, can't calculate prerequisites
    if norm_code not in courses_db: 
        return own_cost 

    # Calculate prerequisite cost
    raw_prereqs = courses_db[norm_code].get('prerequisites_raw', '')
    logic_tree = parse_prerequisites_to_tree(raw_prereqs)
    
    total_prereq_cost = 0
    for or_group in logic_tree:
        group_costs = []
        for option in or_group:
            cost = calculate_recursive_cost(option, expanded_history, courses_db, visited.copy())
            group_costs.append(cost)
        if group_costs: 
            total_prereq_cost += min(group_costs)

    return own_cost + total_prereq_cost

# --- 4. MAJOR & DYNAMIC LOGIC ---

def get_prescribed_major_courses(major_name, programs_db):
    major_courses = []
    target_major = next((p for p in programs_db if p['id'].lower() == major_name.lower() and p['type'] == 'Majors'), None)
    if not target_major: return []
    for rule in target_major.get('rules', []):
        if rule.get('type') == 'all':
            for course in rule.get('courses', []):
                major_courses.append(normalize_code(course['code']))
    return major_courses

def calculate_dynamic_gap(rule, user_history, courses_db):
    constraints = rule.get('constraints', {})
    pool_a = constraints.get('primary_pool', {})
    pool_b = constraints.get('secondary_pool', {})
    credits_in_a = 0
    credits_in_b = 0
    
    for norm_code in user_history:
        dept, number = parse_course_number(norm_code)
        if not dept: continue

        if dept in pool_a.get('departments', []) and pool_a.get('level_min', 0) <= number <= pool_a.get('level_max', 999):
            credits_in_a += get_course_credits(norm_code, courses_db)
            continue
        
        pool_b_norm = [normalize_code(c) for c in pool_b.get('courses', [])]
        if norm_code in pool_b_norm:
            credits_in_b += get_course_credits(norm_code, courses_db)

    total_target = rule.get('credits_needed', 0)
    target_a = pool_a.get('min_credits_needed', 0)
    missing_a = max(0, target_a - credits_in_a)
    total_have = credits_in_a + credits_in_b
    gap = missing_a + max(0, total_target - total_have - missing_a)
    
    missing_desc = []
    if missing_a > 0:
        depts = ", ".join(pool_a.get('departments', [])[:3]) 
        missing_desc.append(f"Need {int(missing_a)} cr: {pool_a['level_min']}-level {depts}...")
    if (gap - missing_a) > 0:
        missing_desc.append(f"Need {int(gap - missing_a)} cr: Any options from list")
    return gap, missing_desc

# --- 5. MAIN CALCULATOR (WITH FIX) ---

def calculate_program_gap(program, user_history, courses_db, major_courses=[]):
    """
    🔥 FIXED: Expands user history with equivalencies before calculations
    """
    # EXPAND HISTORY WITH IMPLIED PREREQUISITES
    expanded_history = expand_user_history_with_equivalencies(user_history, courses_db)
    
    # Convert to set of normalized codes for fast lookup
    expanded_history_set = set(normalize_code(c) for c in expanded_history)
    
    # Also keep a set of just the "Explicit" major courses for the UI tag
    major_courses_set = set(normalize_code(c) for c in major_courses)

    total_gap_credits = 0
    missing_courses = []

    for rule in program.get('rules', []):
        
        if rule.get('type') == 'all':
            for course in rule.get('courses', []):
                code_display = course['code']
                code_norm = normalize_code(code_display)
                rule_credits = course.get('credits', 3.0)

                if code_norm in expanded_history_set:
                    # Check if it was covered specifically by Major explicit list
                    if code_norm in major_courses_set:
                         missing_courses.append({"text": f"{code_display} (Covered by Major)", "status": "major_covered"})
                    continue # Done
                
                # Use expanded history for cost calculation
                cost = calculate_recursive_cost(code_display, expanded_history_set, courses_db, known_credits=rule_credits)
                if cost > 0:
                    total_gap_credits += cost
                    # UI Data
                    raw_p = courses_db.get(code_norm, {}).get('prerequisites_display', '') 
                    if not raw_p: 
                        raw_p = courses_db.get(code_norm, {}).get('prerequisites_raw', '')
                    prereqs = clean_prereq_for_display(raw_p)
                    
                    missing_courses.append({
                        "text": code_display, 
                        "status": "missing",
                        "prereqs": prereqs,
                        "credits": rule_credits
                    })
        
        elif rule.get('type') == 'subset':
            credits_needed = rule.get('credits_needed', 0)
            credits_earned = 0
            potential_options = []
            for course in rule.get('courses', []):
                code_display = course['code']
                code_norm = normalize_code(code_display)
                c_credits = get_course_credits(code_norm, courses_db, default=float(course.get('credits', 3)))
                
                if code_norm in expanded_history_set: 
                    credits_earned += c_credits
                elif code_norm in major_courses_set: # Check original major list too
                    credits_earned += c_credits
                else: 
                    potential_options.append(code_display)

            remaining = max(0, credits_needed - credits_earned)
            if remaining > 0:
                total_gap_credits += remaining
                options_str = ", ".join(potential_options) 
                missing_courses.append({"text": f"Select {int(remaining)} credits from: {options_str}", "status": "subset_missing"})

        elif rule.get('type') == 'dynamic_subset':
            d_gap, d_missing = calculate_dynamic_gap(rule, expanded_history_set, courses_db)
            total_gap_credits += d_gap
            for msg in d_missing:
                missing_courses.append({"text": msg, "status": "missing"})
                
        elif rule.get('type') == 'group_option':
            best_gap = 999
            best_text = ""
            best_prereq = None
            
            for group in rule.get('groups', []):
                g_gap = 0
                g_text = []
                
                for course in group.get('courses', []):
                    display = course['code']
                    norm = normalize_code(display)
                    rule_cr = course.get('credits', 3.0)
                    
                    if norm not in expanded_history_set:
                        cost = calculate_recursive_cost(display, expanded_history_set, courses_db, known_credits=rule_cr)
                        g_gap += cost
                        g_text.append(display)
                
                if g_gap < best_gap:
                    best_gap = g_gap
                    best_text = " + ".join(g_text)
                    if g_text:
                        first = normalize_code(g_text[0])
                        raw_p = courses_db.get(first, {}).get('prerequisites_display', '')
                        if not raw_p: 
                            raw_p = courses_db.get(first, {}).get('prerequisites_raw', '')
                        best_prereq = clean_prereq_for_display(raw_p)

            if best_gap > 0:
                total_gap_credits += best_gap
                missing_courses.append({
                    "text": f"Take: {best_text}", 
                    "status": "missing",
                    "prereqs": best_prereq
                })

    return total_gap_credits, missing_courses

def find_triple_dips(program, user_needs, courses_db):
    opportunities = []
    all_codes = []
    for rule in program.get('rules', []):
        for c in rule.get('courses', []): all_codes.append(normalize_code(c['code']))
        if rule.get('type') == 'group_option':
            for g in rule.get('groups', []):
                for c in g.get('courses', []): all_codes.append(normalize_code(c['code']))
                
    for norm in set(all_codes):
        if norm in courses_db:
            c_data = courses_db[norm]
            matches = [req for req in user_needs if req in c_data.get('genEdAttributes', [])]
            if matches:
                opportunities.append({"course": c_data['courseCode'], "matches": matches})
    return opportunities