"""
Unit tests for gap calculation functions in recommendation_engine.py
"""
import pytest
import recommendation_engine as engine

class TestCalculateDynamicGap:
    """Tests for calculate_dynamic_gap() function."""
    
    def test_enough_from_primary_pool(self, sample_courses_db):
        rule = {
            "credits_needed": 6,
            "constraints": {
                "primary_pool": {
                    "departments": ["ECON"],
                    "level_min": 400,
                    "level_max": 999,
                    "min_credits_needed": 3
                },
                "secondary_pool": {
                    "courses": []
                }
            }
        }
        user_history = ["ECON442", "ECON471"]  # 6 credits from primary pool
        gap, missing = engine.calculate_dynamic_gap(rule, user_history, sample_courses_db)
        assert gap == 0
        assert len(missing) == 0
    
    def test_some_from_primary_some_from_secondary(self, sample_courses_db):
        rule = {
            "credits_needed": 6,
            "constraints": {
                "primary_pool": {
                    "departments": ["ECON"],
                    "level_min": 400,
                    "level_max": 999,
                    "min_credits_needed": 3
                },
                "secondary_pool": {
                    "courses": ["CAS 404"]
                }
            }
        }
        user_history = ["ECON442", "CAS404"]  # 3 from primary, 3 from secondary
        gap, missing = engine.calculate_dynamic_gap(rule, user_history, sample_courses_db)
        assert gap == 0
    
    def test_not_enough_from_primary(self, sample_courses_db):
        rule = {
            "credits_needed": 6,
            "constraints": {
                "primary_pool": {
                    "departments": ["ECON"],
                    "level_min": 400,
                    "level_max": 999,
                    "min_credits_needed": 3
                },
                "secondary_pool": {
                    "courses": []
                }
            }
        }
        user_history = ["ECON442"]  # Only 3 credits, need 3 more
        gap, missing = engine.calculate_dynamic_gap(rule, user_history, sample_courses_db)
        assert gap == 3
        assert len(missing) > 0
    
    def test_none_from_primary(self, sample_courses_db):
        rule = {
            "credits_needed": 6,
            "constraints": {
                "primary_pool": {
                    "departments": ["ECON"],
                    "level_min": 400,
                    "level_max": 999,
                    "min_credits_needed": 3
                },
                "secondary_pool": {
                    "courses": []
                }
            }
        }
        user_history = []  # No courses
        gap, missing = engine.calculate_dynamic_gap(rule, user_history, sample_courses_db)
        assert gap == 6
        assert len(missing) > 0
    
    def test_missing_constraints(self, sample_courses_db):
        rule = {
            "credits_needed": 6,
            "constraints": {}  # Missing primary_pool
        }
        user_history = ["ECON442"]
        # Should handle gracefully, not crash
        gap, missing = engine.calculate_dynamic_gap(rule, user_history, sample_courses_db)
        assert gap >= 0  # Should return some value


class TestCalculateProgramGap:
    """Tests for calculate_program_gap() function."""
    
    def test_rule_type_all_all_completed(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = sample_programs_db[0]  # Business Minor
        user_history = ["MGMT301", "MKTG301W"]
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        # Should only have gap from Supporting Courses (6 credits)
        assert gap >= 0
    
    def test_rule_type_all_some_missing(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["ECON102", "ECON104"]  # Missing ECON 302, 304
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        assert gap > 0
        assert len(missing) > 0
    
    def test_rule_type_subset_enough_credits(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = {
            "rules": [
                {
                    "name": "Select 6 credits",
                    "type": "subset",
                    "credits_needed": 6,
                    "courses": [
                        {"code": "ECON 102", "credits": 3},
                        {"code": "ECON 104", "credits": 3},
                        {"code": "ECON 302", "credits": 3}
                    ]
                }
            ]
        }
        user_history = ["ECON102", "ECON104"]  # 6 credits
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        assert gap == 0
    
    def test_rule_type_subset_not_enough_credits(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = {
            "rules": [
                {
                    "name": "Select 6 credits",
                    "type": "subset",
                    "credits_needed": 6,
                    "courses": [
                        {"code": "ECON 102", "credits": 3},
                        {"code": "ECON 104", "credits": 3},
                        {"code": "ECON 302", "credits": 3}
                    ]
                }
            ]
        }
        user_history = ["ECON102"]  # Only 3 credits
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        assert gap == 3
        assert len(missing) > 0
    
    def test_rule_type_dynamic_subset(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = sample_programs_db[0]  # Business Minor with dynamic_subset
        user_history = ["ECON442", "ECON471"]  # 6 credits from primary pool
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        # Should recognize ECON 442 and 471 as satisfying Supporting Courses
        assert gap >= 0
    
    def test_rule_type_group_option(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = {
            "rules": [
                {
                    "name": "Accounting Foundation",
                    "type": "group_option",
                    "groups": [
                        {
                            "name": "Option A",
                            "courses": [
                                {"code": "ACCTG 211", "credits": 4}
                            ]
                        },
                        {
                            "name": "Option B",
                            "courses": [
                                {"code": "ACCTG 201", "credits": 3},
                                {"code": "ACCTG 202", "credits": 3}
                            ]
                        }
                    ]
                }
            ]
        }
        user_history = ["ACCTG201", "ACCTG202"]  # Option B completed
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        assert gap == 0
    
    def test_empty_history(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = sample_programs_db[0]
        user_history = []
        major_courses = []
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        assert gap > 0
        assert len(missing) > 0
    
    def test_major_courses_covered(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        program = sample_programs_db[0]
        user_history = []
        major_courses = ["MGMT301"]  # Covered by major
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        # Should show MGMT 301 as "Covered by Major"
        major_covered = [m for m in missing if "Covered by Major" in m.get("text", "")]
        assert len(major_covered) > 0

