#!/usr/bin/env python3
"""
Equivalency Generator for Course Prerequisites

This script analyzes academic_programs_rules.json to automatically detect
and generate course equivalencies based on:
1. Courses appearing as "A or B" in prerequisite text
2. Same-department course hierarchies
3. Common prerequisite patterns

No hardcoding - all generated from data analysis.
"""

import json
import re
from collections import defaultdict


def normalize_code(code):
    """Normalize course codes."""
    if not code:
        return ""
    return code.replace(" ", "").replace("\xa0", "").upper()


def parse_course_string(course_code):
    """Parse course code into department and number."""
    if not course_code:
        return None, 0
    clean = normalize_code(course_code)
    match = re.match(r"([A-Z]+)(\d+)", clean)
    if match:
        return match.group(1), int(match.group(2))
    return None, 0


def extract_course_codes(text):
    """Extract all course codes from text."""
    return re.findall(r"([A-Z]{2,5}\s+\d{1,4}[A-Z]?)", text)


def analyze_or_patterns(programs_data):
    """
    Find courses that appear as alternatives to each other ('A or B').
    ONLY courses that substitute for each other, NOT prerequisite relationships.
    
    Example: "ENGL 015 or ENGL 030" → these are equivalents
    NOT: "Prerequisite: MATH 021" → MATH 021 is not equivalent to the course
    """
    equivalencies = defaultdict(set)
    
    print("📊 Analyzing 'or' patterns for true equivalencies...")
    
    # Conservative approach: Only find courses that explicitly substitute each other
    # Look at group_option rules where courses are genuine alternatives
    for program in programs_data:
        for rule in program.get('rules', []):
            
            # group_option rules define true alternatives (Option A vs Option B)
            if rule.get('type') == 'group_option':
                # Within each group, courses are equivalent to each other
                for group in rule.get('groups', []):
                    group_courses = group.get('courses', [])
                    # If this option has multiple courses, they form a package
                    # Don't mark them as equivalent individually
                    if len(group_courses) == 1:
                        # Single course options across groups are alternatives
                        course_code = normalize_code(group_courses[0].get('code', ''))
                        if course_code:
                            # Mark this as part of a group option
                            # We'll handle this specially - don't add to equivalencies yet
                            pass
            
            # Also look for simple "X or Y" patterns in prerequisites
            # where both courses appear at same level (like ENGL 015 or ENGL 030)
            courses = []
            if rule.get('type') in ['all', 'subset']:
                courses = rule.get('courses', [])
            
            for course in courses:
                prereq_text = course.get('prerequisites_text', '')
                if not prereq_text:
                    continue
                
                # Look for parenthesized OR groups: "(ENGL 015 or ENGL 030)"
                paren_groups = re.findall(r'\(([^)]+(?:or|OR)[^)]+)\)', prereq_text)
                
                for group in paren_groups:
                    codes = extract_course_codes(group)
                    # Only if we have exactly 2 courses in a parenthesized OR
                    if len(codes) == 2 and 'or' in group.lower():
                        # Check if they're same department (usually true equivalents)
                        dept1, num1 = parse_course_string(codes[0])
                        dept2, num2 = parse_course_string(codes[1])
                        
                        if dept1 == dept2:
                            # Same department alternativesare likely equivalent
                            norm1 = normalize_code(codes[0])
                            norm2 = normalize_code(codes[1])
                            equivalencies[norm1].add(norm2)
                            equivalencies[norm2].add(norm1)
    
    print(f"   Found {len(equivalencies)} courses with OR-based equivalencies")
    return equivalencies


def analyze_department_hierarchies(programs_data, courses_master):
    """
    Analyze same-department course progressions.
    Build hierarchy maps for common patterns.
    """
    hierarchies = defaultdict(lambda: {"lower_courses": set(), "reason": ""})
    
    print("\n📊 Analyzing department hierarchies...")
    
    # Get all prerequisite relationships
    prereq_relationships = []
    
    for program in programs_data:
        for rule in program.get('rules', []):
            courses = []
            
            if rule.get('type') in ['all', 'subset']:
                courses = rule.get('courses', [])
            elif rule.get('type') == 'group_option':
                for group in rule.get('groups', []):
                    courses.extend(group.get('courses', []))
            
            for course in courses:
                code = course.get('code', '')
                prereq_list = course.get('prerequisites_list', [])
                
                if code and prereq_list:
                    norm_code = normalize_code(code)
                    dept, num = parse_course_string(code)
                    
                    for prereq in prereq_list:
                        prereq_dept, prereq_num = parse_course_string(prereq)
                        
                        # Same department, higher number
                        if dept and prereq_dept == dept and num > prereq_num:
                            prereq_relationships.append({
                                'higher': norm_code,
                                'lower': normalize_code(prereq),
                                'dept': dept,
                                'gap': num - prereq_num
                            })
    
    # Build hierarchies for courses that are frequently prerequisites
    prereq_counts = defaultdict(int)
    for rel in prereq_relationships:
        prereq_counts[rel['lower']] += 1
    
    # Identify common foundation courses (appear as prereqs 3+ times)
    foundation_courses = {k for k, v in prereq_counts.items() if v >= 3}
    
    for rel in prereq_relationships:
        if rel['lower'] in foundation_courses:
            higher = rel['higher']
            hierarchies[rel['lower']]['lower_courses'].add(higher)
            hierarchies[rel['lower']]['reason'] = f"Foundation course in {rel['dept']}"
    
    print(f"   Identified {len(hierarchies)} foundation courses with hierarchies")
    return hierarchies


def generate_equivalency_map(programs_data, courses_master):
    """
    Main function to generate complete equivalency map.
    """
    print("=" * 60)
    print("🔍 Generating Course Equivalencies")
    print("=" * 60)
    
    # Strategy 1: OR patterns
    or_equivalencies = analyze_or_patterns(programs_data)
    
    # Strategy 2: Department hierarchies
    hierarchies = analyze_department_hierarchies(programs_data, courses_master)
    
    # Merge results
    equivalency_map = {}
    
    # Add OR-based equivalencies
    for norm_code, equiv_set in or_equivalencies.items():
        if len(equiv_set) > 0:
            equivalency_map[norm_code] = {
                "equivalents": sorted(list(equiv_set)),
                "reason": "Appears as alternative in prerequisite text",
                "auto_generated": True,
                "type": "or_pattern"
            }
    
    # Add hierarchy-based equivalencies
    for norm_code, data in hierarchies.items():
        if len(data['lower_courses']) > 0:
            # Add all higher courses as equivalents
            higher_list = sorted(list(data['lower_courses']))
            
            if norm_code in equivalency_map:
                # Merge with existing
                existing = set(equivalency_map[norm_code]['equivalents'])
                equivalency_map[norm_code]['equivalents'] = sorted(list(existing.union(higher_list)))
                equivalency_map[norm_code]['type'] = "or_pattern+hierarchy"
            else:
                equivalency_map[norm_code] = {
                    "equivalents": higher_list,
                    "reason": data['reason'] + " - higher-level courses satisfy this prerequisite",
                    "auto_generated": True,
                    "type": "hierarchy"
                }
    
    return equivalency_map


def main():
    """Main execution."""
    print("\n📂 Loading source data...")
    
    try:
        with open('academic_programs_rules.json', 'r', encoding='utf-8') as f:
            programs_data = json.load(f)
        print(f"   ✓ Loaded {len(programs_data)} programs")
        
        with open('world_campus_courses_master.json', 'r', encoding='utf-8') as f:
            courses_master = json.load(f)
        print(f"   ✓ Loaded {len(courses_master)} courses")
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return
    
    # Generate equivalencies
    equivalency_map = generate_equivalency_map(programs_data, courses_master)
    
    # Save to file
    print("\n💾 Saving course_equivalencies.json...")
    with open('course_equivalencies.json', 'w', encoding='utf-8') as f:
        json.dump(equivalency_map, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print("\n" + "=" * 60)
    print("📊 EQUIVALENCY GENERATION COMPLETE")
    print("=" * 60)
    print(f"Total courses with equivalencies: {len(equivalency_map)}")
    
    or_pattern_count = sum(1 for v in equivalency_map.values() if 'or_pattern' in v.get('type', ''))
    hierarchy_count = sum(1 for v in equivalency_map.values() if v.get('type') == 'hierarchy')
    both_count = sum(1 for v in equivalency_map.values() if v.get('type') == 'or_pattern+hierarchy')
    
    print(f"  → OR-pattern based: {or_pattern_count}")
    print(f"  → Hierarchy based: {hierarchy_count}")
    print(f"  → Both: {both_count}")
    
    # Show some examples
    print("\n📋 Sample Equivalencies:")
    sample_count = 0
    for code, data in sorted(equivalency_map.items())[:5]:
        print(f"  {code}: {', '.join(data['equivalents'][:3])}")
        print(f"     Reason: {data['reason'][:60]}...")
        sample_count += 1
    
    print("\n✅ Equivalency map generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

