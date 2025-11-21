#!/usr/bin/env python3
"""
Data Optimization Script for World Campus Course Recommendation System

This script generates optimized data files by:
1. Extracting all courses from academic_programs_rules.json
2. Deduplicating courses with conflict detection
3. Enriching with GenEd attributes from gened_courses_golden_record.json
4. Creating world_campus_courses_master.json (primary lookup)
5. Creating gened_supplementary.json (fallback for non-WC courses)
"""

import json
import re
from collections import defaultdict


def normalize_code(code):
    """Normalize course codes by removing spaces and special characters."""
    if not code:
        return ""
    return code.replace(" ", "").replace("\xa0", "").upper()


def extract_courses_from_programs(programs_data):
    """
    Extract all unique courses from academic_programs_rules.json.
    Returns: (courses_dict, conflicts_dict)
    """
    courses = {}
    conflicts = defaultdict(list)
    
    print("📚 Extracting courses from academic programs...")
    
    for program in programs_data:
        program_id = program.get('id', 'Unknown')
        
        for rule in program.get('rules', []):
            rule_name = rule.get('name', 'Unknown Rule')
            
            # Handle different rule types
            if rule.get('type') in ['all', 'subset']:
                for course in rule.get('courses', []):
                    process_course(course, courses, conflicts, program_id, rule_name)
            
            elif rule.get('type') == 'group_option':
                for group in rule.get('groups', []):
                    for course in group.get('courses', []):
                        process_course(course, courses, conflicts, program_id, rule_name)
            
            elif rule.get('type') == 'dynamic_subset':
                # Handle secondary pool courses
                secondary_pool = rule.get('constraints', {}).get('secondary_pool', {})
                for course_code in secondary_pool.get('courses', []):
                    # Dynamic subset courses may not have full details
                    course_obj = {'code': course_code, 'credits': 3}
                    process_course(course_obj, courses, conflicts, program_id, rule_name)
    
    print(f"✅ Extracted {len(courses)} unique courses")
    return courses, conflicts


def process_course(course, courses_dict, conflicts_dict, program_id, rule_name):
    """Process a single course and detect conflicts."""
    code = course.get('code', '')
    if not code:
        return
    
    norm_code = normalize_code(code)
    prereq_text = course.get('prerequisites_text', '')
    
    # If course already exists, check for conflicts
    if norm_code in courses_dict:
        existing_prereq = courses_dict[norm_code].get('prerequisites_text', '')
        
        # Check if prerequisites differ (ignoring minor variations)
        if prereq_text and existing_prereq and prereq_text.strip() != existing_prereq.strip():
            conflicts_dict[norm_code].append({
                'program': program_id,
                'rule': rule_name,
                'prerequisites_text': prereq_text
            })
    else:
        # Add new course
        courses_dict[norm_code] = {
            'courseCode': code,
            'title': course.get('title', ''),
            'credits': course.get('credits', 3),
            'prerequisites_text': prereq_text,
            'prerequisites_list': course.get('prerequisites_list', []),
            'description': course.get('description', ''),
            'source_program': program_id
        }


def enrich_with_gened_data(world_campus_courses, gened_courses):
    """
    Enrich World Campus courses with GenEd attributes from gened database.
    """
    print("\n🎨 Enriching courses with GenEd attributes...")
    
    # Build lookup dictionary from gened courses
    gened_lookup = {}
    for course in gened_courses:
        norm_code = normalize_code(course.get('courseCode', ''))
        gened_lookup[norm_code] = course
    
    enriched_count = 0
    
    for norm_code, course in world_campus_courses.items():
        if norm_code in gened_lookup:
            gened_data = gened_lookup[norm_code]
            
            # Add GenEd attributes
            course['genEdAttributes'] = gened_data.get('genEdAttributes', [])
            course['culturalAttributes'] = gened_data.get('culturalAttributes', [])
            course['interDomain'] = gened_data.get('interDomain', False)
            
            # Use prerequisites_raw from gened if world campus doesn't have it
            if not course.get('prerequisites_text') and gened_data.get('prerequisites_raw'):
                course['prerequisites_raw'] = gened_data.get('prerequisites_raw')
            else:
                # Rename prerequisites_text to prerequisites_raw for consistency
                course['prerequisites_raw'] = course.pop('prerequisites_text', '')
            
            enriched_count += 1
        else:
            # Set default values for courses not in gened
            course['genEdAttributes'] = []
            course['culturalAttributes'] = []
            course['interDomain'] = False
            course['prerequisites_raw'] = course.pop('prerequisites_text', '')
    
    print(f"✅ Enriched {enriched_count} courses with GenEd data")
    return world_campus_courses


def create_supplementary_file(world_campus_courses, gened_courses):
    """
    Create supplementary file with courses NOT in World Campus.
    """
    print("\n📝 Creating supplementary GenEd file...")
    
    wc_codes = set(world_campus_courses.keys())
    supplementary = {}
    
    for course in gened_courses:
        norm_code = normalize_code(course.get('courseCode', ''))
        
        if norm_code not in wc_codes:
            supplementary[norm_code] = {
                'courseCode': course.get('courseCode', ''),
                'title': course.get('title', ''),
                'credits': course.get('credits', '3'),
                'prerequisites_raw': course.get('prerequisites_raw', ''),
                'genEdAttributes': course.get('genEdAttributes', []),
                'culturalAttributes': course.get('culturalAttributes', []),
                'interDomain': course.get('interDomain', False),
                'detailsUrl': course.get('detailsUrl', ''),
                'worldCampusOffering': False
            }
    
    print(f"✅ Created supplementary file with {len(supplementary)} courses")
    return supplementary


def save_conflicts(conflicts, filename='duplicate_conflicts.json'):
    """Save conflict report to JSON file."""
    if conflicts:
        print(f"\n⚠️  Found {len(conflicts)} courses with conflicting prerequisites")
        print("   Saving to duplicate_conflicts.json for manual review...")
        
        # Format conflicts for readability
        formatted_conflicts = {}
        for norm_code, conflict_list in conflicts.items():
            formatted_conflicts[norm_code] = {
                'total_occurrences': len(conflict_list) + 1,
                'conflicts': conflict_list
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(formatted_conflicts, f, indent=2, ensure_ascii=False)
        
        print(f"   Review {filename} to resolve conflicts")
    else:
        print("\n✅ No prerequisite conflicts found!")


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 World Campus Data Optimization Script")
    print("=" * 60)
    
    # Load source data
    print("\n📂 Loading source data files...")
    try:
        with open('academic_programs_rules.json', 'r', encoding='utf-8') as f:
            programs_data = json.load(f)
        print(f"   ✓ Loaded academic_programs_rules.json ({len(programs_data)} programs)")
        
        with open('gened_courses_golden_record.json', 'r', encoding='utf-8') as f:
            gened_courses = json.load(f)
        print(f"   ✓ Loaded gened_courses_golden_record.json ({len(gened_courses)} courses)")
    except FileNotFoundError as e:
        print(f"❌ ERROR: Could not find required file: {e}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON format: {e}")
        return
    
    # Phase 1: Extract and deduplicate
    world_campus_courses, conflicts = extract_courses_from_programs(programs_data)
    
    # Phase 2: Save conflicts for review
    save_conflicts(conflicts)
    
    # Phase 3: Enrich with GenEd data
    world_campus_courses = enrich_with_gened_data(world_campus_courses, gened_courses)
    
    # Phase 4: Create supplementary file
    supplementary_courses = create_supplementary_file(world_campus_courses, gened_courses)
    
    # Phase 5: Save master file
    print("\n💾 Saving world_campus_courses_master.json...")
    # Sort by course code for readability
    sorted_master = dict(sorted(world_campus_courses.items()))
    with open('world_campus_courses_master.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_master, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved {len(sorted_master)} World Campus courses")
    
    # Phase 6: Save supplementary file
    print("\n💾 Saving gened_supplementary.json...")
    sorted_supplementary = dict(sorted(supplementary_courses.items()))
    with open('gened_supplementary.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_supplementary, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved {len(sorted_supplementary)} supplementary courses")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total World Campus courses:        {len(world_campus_courses)}")
    print(f"Courses with GenEd attributes:     {sum(1 for c in world_campus_courses.values() if c.get('genEdAttributes'))}")
    print(f"Supplementary courses:             {len(supplementary_courses)}")
    print(f"Prerequisite conflicts detected:   {len(conflicts)}")
    print(f"\nTotal courses available:           {len(world_campus_courses) + len(supplementary_courses)}")
    print("=" * 60)
    print("\n✅ Data optimization complete!")
    print("\nNext steps:")
    print("1. Review duplicate_conflicts.json if conflicts were found")
    print("2. Update recommendation_engine.py to use new data files")
    print("3. Test the system with sample data")
    print("=" * 60)


if __name__ == "__main__":
    main()

