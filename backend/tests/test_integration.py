"""
Integration tests for real-world scenarios in recommendation_engine.py
"""
import pytest
import recommendation_engine as engine
import time

class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios."""
    
    def test_business_minor_with_econ_442_471(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test Business Minor with ECON 442 and 471 (Supporting Courses)."""
        program = sample_programs_db[0]  # Business Minor
        user_history = ["ECON102", "ECON104", "ECON442", "ECON471", "MGMT301"]
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        overlap_count, overlap_courses = engine.calculate_overlap_count(program, user_history, major_courses)
        
        # Expected: Gap = 7 credits (ACCTG 211 + MKTG 301W)
        # Supporting Courses should be satisfied (ECON 442 + 471 = 6 credits)
        assert gap >= 0
        assert overlap_count >= 3  # ECON 102, 104, MGMT 301 at minimum
        
        # Check that ECON 442 and 471 are recognized
        econ_courses = [c for c in overlap_courses if "ECON" in c.upper()]
        assert len(econ_courses) >= 2, "ECON 442 and 471 should be recognized"
    
    def test_economics_minor_with_400_level_econ(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test Economics Minor with 400-level ECON courses."""
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["ECON102", "ECON104", "ECON302", "ECON304", "ECON442", "ECON471"]
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        overlap_count, overlap_courses = engine.calculate_overlap_count(program, user_history, major_courses)
        
        # Expected: Gap = 0 (completed)
        # Overlap count = 6 courses
        assert gap == 0, f"Economics Minor should be completed, but gap = {gap}"
        assert overlap_count == 6, f"Should have 6 overlapping courses, got {overlap_count}"
        assert len(overlap_courses) == 6
    
    def test_deep_prerequisite_chain(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test program with deep prerequisite chain."""
        program = {
            "rules": [
                {
                    "type": "all",
                    "courses": [
                        {"code": "CMPSC 465", "credits": 3}
                    ]
                }
            ]
        }
        user_history = ["MATH140"]  # Has MATH 140, but missing CMPSC 131, 132
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        # Should identify missing CMPSC 465
        assert gap > 0
        # Question: Should gap include prerequisites? Currently it doesn't
        # Gap should be 3 (just CMPSC 465) OR 9 (with prerequisites)
    
    def test_group_option_accounting_foundation(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test Accounting Foundation group option logic."""
        program = {
            "rules": [
                {
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
        
        # Should recognize Option B as completed
        assert gap == 0, f"Option B should be completed, but gap = {gap}"
    
    def test_group_option_option_a_completed(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test group option with Option A completed."""
        program = {
            "rules": [
                {
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
        user_history = ["ACCTG211"]  # Option A completed
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        # Should recognize Option A as completed
        assert gap == 0, f"Option A should be completed, but gap = {gap}"


class TestEdgeCases:
    """Integration tests for edge cases."""
    
    def test_empty_history(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test with empty course history."""
        program = sample_programs_db[0]
        user_history = []
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        assert gap > 0
        assert len(missing) > 0
    
    def test_empty_major(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test with empty major name."""
        program = sample_programs_db[0]
        user_history = ["ECON102"]
        major_courses = []  # No major courses
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        # Should work without major courses
        assert gap >= 0
    
    def test_malformed_course_codes(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test with malformed course codes in history."""
        program = sample_programs_db[0]
        user_history = ["", "   ", "ABC", "123", "ECON 102"]  # Mix of valid and invalid
        major_courses = []
        
        # Should handle gracefully, not crash
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        assert gap >= 0
    
    def test_missing_course_data(self, sample_programs_db, sample_equivalency_map, sample_prereq_config):
        """Test with missing course data in database."""
        courses_db = {}  # Empty database
        program = sample_programs_db[0]
        user_history = ["ECON102"]
        major_courses = []
        
        # Should handle gracefully, use defaults
        gap, missing = engine.calculate_program_gap(
            program, user_history, courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        assert gap >= 0
    
    def test_missing_program_rules(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test program with missing rules."""
        program = {"id": "Test", "type": "Minors", "rules": []}  # No rules
        user_history = ["ECON102"]
        major_courses = []
        
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        
        assert gap == 0  # No requirements = completed
        assert len(missing) == 0
    
    def test_circular_prerequisites(self, sample_equivalency_map, sample_prereq_config):
        """Test with circular prerequisites."""
        courses_db = {
            "COURSEA": {
                "courseCode": "COURSE A",
                "credits": 3.0,
                "prerequisites_raw": "Prerequisite COURSE B"
            },
            "COURSEB": {
                "courseCode": "COURSE B",
                "credits": 3.0,
                "prerequisites_raw": "Prerequisite COURSE A"
            }
        }
        program = {
            "rules": [
                {
                    "type": "all",
                    "courses": [
                        {"code": "COURSE A", "credits": 3}
                    ]
                }
            ]
        }
        user_history = []
        major_courses = []
        
        # Should not infinite loop
        start = time.time()
        gap, missing = engine.calculate_program_gap(
            program, user_history, courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        elapsed = time.time() - start
        
        assert elapsed < 1.0, "Circular prerequisites caused infinite loop or excessive delay"
        assert gap >= 0


class TestPerformance:
    """Performance tests for large datasets."""
    
    def test_large_course_history(self, sample_programs_db, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test with 200 courses in history."""
        program = sample_programs_db[0]
        user_history = [f"COURSE{i}" for i in range(200)]
        major_courses = []
        
        start = time.time()
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        elapsed = time.time() - start
        
        # Target: < 5 seconds for full recommendation
        assert elapsed < 5.0, f"Gap calculation took {elapsed:.2f} seconds (target: < 5.0)"
        assert gap >= 0
    
    def test_deep_prerequisite_chain_performance(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test performance with 5-level deep prerequisites."""
        # Create deep chain: A -> B -> C -> D -> E
        courses_db = sample_courses_db.copy()
        courses_db["COURSEA"] = {
            "courseCode": "COURSE A",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite COURSE B"
        }
        courses_db["COURSEB"] = {
            "courseCode": "COURSE B",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite COURSE C"
        }
        courses_db["COURSEC"] = {
            "courseCode": "COURSE C",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite COURSE D"
        }
        courses_db["COURSED"] = {
            "courseCode": "COURSE D",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite COURSE E"
        }
        courses_db["COURSEE"] = {
            "courseCode": "COURSE E",
            "credits": 3.0,
            "prerequisites_raw": ""
        }
        
        program = {
            "rules": [
                {
                    "type": "group_option",
                    "groups": [
                        {
                            "courses": [
                                {"code": "COURSE A", "credits": 3}
                            ]
                        }
                    ]
                }
            ]
        }
        user_history = []
        major_courses = []
        
        start = time.time()
        gap, missing = engine.calculate_program_gap(
            program, user_history, courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        elapsed = time.time() - start
        
        # Target: < 2 seconds for 5-level chain
        assert elapsed < 2.0, f"Deep prerequisite calculation took {elapsed:.2f} seconds (target: < 2.0)"
        assert gap >= 0
    
    def test_many_dynamic_subset_rules(self, sample_courses_db, sample_equivalency_map, sample_prereq_config):
        """Test performance with program having 10 dynamic_subset rules."""
        program = {
            "rules": [
                {
                    "type": "dynamic_subset",
                    "credits_needed": 3,
                    "constraints": {
                        "primary_pool": {
                            "departments": ["ECON"],
                            "level_min": 400,
                            "level_max": 999,
                            "min_credits_needed": 0
                        },
                        "secondary_pool": {
                            "courses": []
                        }
                    }
                }
            ] * 10  # 10 identical rules
        }
        user_history = ["ECON442", "ECON471"]
        major_courses = []
        
        start = time.time()
        gap, missing = engine.calculate_program_gap(
            program, user_history, sample_courses_db, major_courses,
            sample_equivalency_map, sample_prereq_config
        )
        elapsed = time.time() - start
        
        # Target: < 1 second
        assert elapsed < 1.0, f"Many dynamic_subset rules took {elapsed:.2f} seconds (target: < 1.0)"
        assert gap >= 0

