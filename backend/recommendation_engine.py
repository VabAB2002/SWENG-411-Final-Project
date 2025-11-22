import json
import re

# --- 1. CONFIGURATION ---
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

PROGRAMS_FILE = os.path.join(DATA_DIR, 'academic_programs_rules.json')
WORLD_CAMPUS_MASTER = os.path.join(DATA_DIR, 'world_campus_courses_master.json')
GENED_SUPPLEMENTARY = os.path.join(DATA_DIR, 'gened_supplementary.json')    

def load_data():
    print("Loading database...")
    try:
        # Load programs (unchanged)
        with open(PROGRAMS_FILE, 'r') as f:
            programs_db = json.load(f)
        
        # Load World Campus master courses (primary)
        with open(WORLD_CAMPUS_MASTER, 'r') as f:
            master_courses = json.load(f)
        
        # Load supplementary GenEd courses (fallback)
        with open(GENED_SUPPLEMENTARY, 'r') as f:
            supplementary_courses = json.load(f)
        
        # Merge with master taking priority (master overwrites supplementary)
        courses_db = {**supplementary_courses, **master_courses}
        
        # Load prerequisite configuration
        try:
            prereq_config_path = os.path.join(os.path.dirname(__file__), 'config', 'prerequisite_config.json')
            with open(prereq_config_path, 'r') as f:
                prereq_config = json.load(f)
            print(f"  → Loaded prerequisite config (hierarchy rules: {prereq_config.get('hierarchy_rules', {}).get('enabled', False)})")
        except FileNotFoundError:
            print(f"  ⚠️  prerequisite_config.json not found, using defaults")
            prereq_config = {
                "hierarchy_rules": {"enabled": True, "same_department_higher_level": True, "minimum_level_difference": 0}
            }
        
        # Load course equivalencies
        try:
            equivalency_path = os.path.join(DATA_DIR, 'course_equivalencies.json')
            with open(equivalency_path, 'r') as f:
                equivalency_map = json.load(f)
            print(f"  → Loaded {len(equivalency_map)} course equivalencies")
        except FileNotFoundError:
            print(f"  ⚠️  course_equivalencies.json not found, equivalencies disabled")
            equivalency_map = {}
        
        print(f"Loaded {len(programs_db)} Programs and {len(courses_db)} Course Definitions.")
        print(f"  → {len(master_courses)} World Campus courses")
        print(f"  → {len(supplementary_courses)} supplementary courses")
        return programs_db, courses_db, equivalency_map, prereq_config
    except FileNotFoundError as e:
        print(f"CRITICAL ERROR: Missing file. {e}")
        return [], {}, {}, {}

# --- 2. PARSING & UTILS ---

def normalize_code(code):
    if not code: return ""
    return code.replace(" ", "").replace("\xa0", "").upper()

def parse_course_string(course_code):
    if not course_code: return None, 0
    clean = normalize_code(course_code)
    match = re.match(r"([A-Z]+)(\d+)", clean)
    if match:
        return match.group(1), int(match.group(2))
    return None, 0

def get_course_credits(code, courses_db, default=3.0):
    norm_code = normalize_code(code)
    if norm_code in courses_db:
        try:
            val = str(courses_db[norm_code].get('credits', default)).split('-')[0]
            return float(val)
        except: return default
    return default

def get_course_prereqs(code, courses_db):
    """Fetches raw prerequisite text for display."""
    norm_code = normalize_code(code)
    if norm_code in courses_db:
        return courses_db[norm_code].get('prerequisites_raw', 'No prerequisites listed.')
    return "No data available."

def extract_course_codes(text_chunk):
    return re.findall(r"([A-Z]{2,5}\s+\d{1,4}[A-Z]?)", text_chunk)

def course_satisfies_prerequisite(required_code, user_history, equivalency_map=None, prereq_config=None):
    """
    Intelligent prerequisite checking with three tiers:
    
    Tier 1: Exact match - Direct course code match
    Tier 2: Equivalency map - Explicitly defined equivalent courses
    Tier 3: Hierarchy rules - Same department, higher level courses
    
    Args:
        required_code: The prerequisite course code
        user_history: List of normalized course codes from user's transcript
        equivalency_map: Dictionary of course equivalencies
        prereq_config: Configuration dict with hierarchy rules
    
    Returns:
        Boolean indicating if prerequisite is satisfied
    """
    norm_required = normalize_code(required_code)
    
    # Tier 1: Exact match
    if norm_required in user_history:
        return True
    
    # Tier 2: Check equivalency map
    if equivalency_map and norm_required in equivalency_map:
        equivalents = equivalency_map[norm_required].get('equivalents', [])
        for equiv in equivalents:
            if normalize_code(equiv) in user_history:
                return True
    
    # Tier 3: Check same-department higher-level courses (if enabled)
    if prereq_config and prereq_config.get('hierarchy_rules', {}).get('same_department_higher_level', False):
        req_dept, req_num = parse_course_string(required_code)
        min_diff = prereq_config.get('hierarchy_rules', {}).get('minimum_level_difference', 0)
        
        if req_dept and req_num > 0:
            for user_course in user_history:
                user_dept, user_num = parse_course_string(user_course)
                if user_dept == req_dept and user_num >= req_num + min_diff:
                    return True
    
    return False

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

# --- 3. COST CALCULATOR ---

def calculate_recursive_cost(code, user_history, courses_db, visited=None, known_credits=None, equivalency_map=None, prereq_config=None):
    norm_code = normalize_code(code)
    
    # Use intelligent prerequisite checking
    if course_satisfies_prerequisite(code, user_history, equivalency_map, prereq_config):
        return 0
    
    if visited is None: visited = set()
    if norm_code in visited: return 0
    visited.add(norm_code)

    if norm_code in courses_db:
        own_cost = get_course_credits(norm_code, courses_db)
    elif known_credits is not None:
        own_cost = float(known_credits)
    else:
        own_cost = 3.0
    
    if norm_code not in courses_db: return own_cost 

    raw_prereqs = courses_db[norm_code].get('prerequisites_raw', '')
    logic_tree = parse_prerequisites_to_tree(raw_prereqs)
    
    total_prereq_cost = 0
    for or_group in logic_tree:
        group_costs = []
        for option in or_group:
            cost = calculate_recursive_cost(option, user_history, courses_db, visited.copy(), None, equivalency_map, prereq_config)
            group_costs.append(cost)
        if group_costs: total_prereq_cost += min(group_costs)

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
        dept, number = parse_course_string(norm_code)
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

# --- 5. MAIN CALCULATOR ---

def calculate_program_gap(program, user_history, courses_db, major_courses=[], equivalency_map=None, prereq_config=None):
    total_gap_credits = 0
    missing_courses = []
    
    for rule in program.get('rules', []):
        
        if rule.get('type') == 'all':
            for course in rule.get('courses', []):
                code_display = course['code']
                code_norm = normalize_code(code_display)
                rule_credits = course.get('credits', 3.0)

                # For REQUIRED courses, check EXACT match only (no equivalency/hierarchy)
                # Equivalency and hierarchy rules should only apply to PREREQUISITES
                if code_norm in user_history: continue 
                if code_norm in major_courses:
                    missing_courses.append({"text": f"{code_display} (Covered by Major)", "status": "major_covered"})
                    continue 
                
                # Course is missing - add to gap (just the course itself, no prerequisites)
                total_gap_credits += rule_credits
                prereqs = get_course_prereqs(code_display, courses_db)
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
                
                if code_norm in user_history: credits_earned += c_credits
                elif code_norm in major_courses: credits_earned += c_credits
                else: potential_options.append(code_display)

            remaining = max(0, credits_needed - credits_earned)
            if remaining > 0:
                total_gap_credits += remaining
                options_str = ", ".join(potential_options[:3]) 
                if len(potential_options) > 3: options_str += "..."
                missing_courses.append({"text": f"Select {int(remaining)} credits from: {options_str}", "status": "subset_missing"})

        elif rule.get('type') == 'dynamic_subset':
            d_gap, d_missing = calculate_dynamic_gap(rule, user_history, courses_db)
            total_gap_credits += d_gap
            for msg in d_missing:
                missing_courses.append({"text": msg, "status": "missing"})
                
        elif rule.get('type') == 'group_option':
            best_gap = 999
            best_option_text = ""
            
            for group in rule.get('groups', []):
                group_gap = 0
                group_text = []
                for course in group.get('courses', []):
                    code_display = course['code']
                    code_norm = normalize_code(code_display)
                    rule_credits = course.get('credits', 3.0)
                    
                    if code_norm not in user_history and code_norm not in major_courses:
                        cost = calculate_recursive_cost(code_display, user_history, courses_db, known_credits=rule_credits, equivalency_map=equivalency_map, prereq_config=prereq_config)
                        group_gap += cost
                        group_text.append(code_display)
                
                if group_gap < best_gap:
                    best_gap = group_gap
                    if group_gap == 0: best_option_text = "Completed"
                    else: best_option_text = " + ".join(group_text)

            if best_gap > 0:
                total_gap_credits += best_gap
                missing_courses.append({"text": f"Take: {best_option_text}", "status": "missing"})

    return total_gap_credits, missing_courses

def find_triple_dips(program, user_needs, courses_db):
    opportunities = []
    all_program_courses = []
    for rule in program.get('rules', []):
        for c in rule.get('courses', []):
            all_program_courses.append(normalize_code(c['code']))
        if rule.get('type') == 'dynamic_subset':
            secondary = rule.get('constraints', {}).get('secondary_pool', {}).get('courses', [])
            all_program_courses.extend([normalize_code(c) for c in secondary])
        if rule.get('type') == 'group_option':
             for g in rule.get('groups', []):
                 for c in g.get('courses', []):
                     all_program_courses.append(normalize_code(c['code']))
            
    for norm_code in set(all_program_courses):
        if norm_code in courses_db:
            c_data = courses_db[norm_code]
            attrs = c_data.get('genEdAttributes', [])
            matches = [req for req in user_needs if req in attrs]
            if matches:
                opportunities.append({"course": c_data['courseCode'], "matches": matches, "title": c_data.get('title', '')})
    return opportunities

def calculate_overlap_count(program, user_history, major_courses):
    """
    Calculate how many courses from user's history overlap with program requirements.
    
    This provides the "Overlap Count" metric shown in documentation, complementing
    the "Gap Credits" metric.
    
    Args:
        program: Program dict with rules
        user_history: List of normalized course codes from user's transcript
        major_courses: List of normalized course codes from user's major
    
    Returns:
        tuple: (overlap_count, overlapping_courses_list)
    """
    combined_history = set(user_history + major_courses)
    overlapping_courses = []
    
    for rule in program.get('rules', []):
        if rule.get('type') == 'all':
            for course in rule.get('courses', []):
                code_norm = normalize_code(course['code'])
                if code_norm in combined_history:
                    overlapping_courses.append(course['code'])
        
        elif rule.get('type') == 'subset':
            for course in rule.get('courses', []):
                code_norm = normalize_code(course['code'])
                if code_norm in combined_history:
                    overlapping_courses.append(course['code'])
        
        elif rule.get('type') == 'dynamic_subset':
            # Check primary pool (department-level matches)
            constraints = rule.get('constraints', {})
            primary_pool = constraints.get('primary_pool', {})
            departments = primary_pool.get('departments', [])
            level_min = primary_pool.get('level_min', 0)
            level_max = primary_pool.get('level_max', 999)
            
            for norm_code in combined_history:
                dept, number = parse_course_string(norm_code)
                if dept and dept in departments:
                    if level_min <= number <= level_max:
                        # Get the original course code format from user_history
                        # Find matching course in original format
                        for orig_code in user_history + major_courses:
                            if normalize_code(orig_code) == norm_code:
                                # Check normalized codes to avoid duplicates like "ECON471" and "ECON 471"
                                if normalize_code(orig_code) not in [normalize_code(c) for c in overlapping_courses]:
                                    overlapping_courses.append(orig_code)
                                break
            
            # Check secondary pool courses (specific courses)
            secondary = rule.get('constraints', {}).get('secondary_pool', {}).get('courses', [])
            for course_code in secondary:
                code_norm = normalize_code(course_code)
                if code_norm in combined_history:
                    # Check normalized codes to avoid duplicates
                    if code_norm not in [normalize_code(c) for c in overlapping_courses]:
                        overlapping_courses.append(course_code)
        
        elif rule.get('type') == 'group_option':
            # Check all courses in all groups
            for group in rule.get('groups', []):
                for course in group.get('courses', []):
                    code_norm = normalize_code(course['code'])
                    if code_norm in combined_history:
                        overlapping_courses.append(course['code'])
    
    # Remove duplicates while preserving order (normalize before comparing)
    seen = set()
    unique_overlapping = []
    for c in overlapping_courses:
        normalized = normalize_code(c)
        if normalized not in seen:
            seen.add(normalized)
            unique_overlapping.append(c)
    
    return len(unique_overlapping), unique_overlapping