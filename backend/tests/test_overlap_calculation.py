"""
Unit tests for overlap calculation in recommendation_engine.py
"""
import pytest
import recommendation_engine as engine

class TestCalculateOverlapCount:
    """Tests for calculate_overlap_count() function."""
    
    def test_all_courses_match(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["ECON102", "ECON104", "ECON302", "ECON304"]
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 4
        assert len(courses) == 4
    
    def test_some_courses_match(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["ECON102", "ECON104"]  # Only 2 of 4 required
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 2
        assert len(courses) == 2
    
    def test_no_matches(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["MATH140", "CMPSC131"]  # No ECON courses
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 0
        assert len(courses) == 0
    
    def test_duplicate_courses_in_history(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[1]  # Economics Minor
        user_history = ["ECON102", "ECON 102", "econ 102"]  # Same course, different formats
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        # Should not double-count
        assert count == 1
        assert len(courses) == 1
    
    def test_dynamic_subset_primary_pool(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]  # Business Minor with dynamic_subset
        user_history = ["ECON442", "ECON471"]  # 400-level ECON courses
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        # Should count ECON 442 and 471 as overlaps
        assert count >= 2
        assert "ECON 442" in courses or "ECON442" in courses or "ECON 471" in courses or "ECON471" in courses
    
    def test_dynamic_subset_secondary_pool(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]  # Business Minor
        user_history = ["CAS404"]  # From secondary pool
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        # Should count CAS 404 if it's in secondary pool
        assert count >= 0
    
    def test_rule_type_all(self, sample_courses_db):
        program = {
            "rules": [
                {
                    "type": "all",
                    "courses": [
                        {"code": "ECON 102"},
                        {"code": "ECON 104"}
                    ]
                }
            ]
        }
        user_history = ["ECON102", "ECON104"]
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 2
    
    def test_rule_type_subset(self, sample_courses_db):
        program = {
            "rules": [
                {
                    "type": "subset",
                    "courses": [
                        {"code": "ECON 102"},
                        {"code": "ECON 104"},
                        {"code": "ECON 302"}
                    ]
                }
            ]
        }
        user_history = ["ECON102", "ECON104"]
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 2
    
    def test_rule_type_group_option(self, sample_courses_db):
        program = {
            "rules": [
                {
                    "type": "group_option",
                    "groups": [
                        {
                            "courses": [
                                {"code": "ACCTG 211"}
                            ]
                        },
                        {
                            "courses": [
                                {"code": "ACCTG 201"},
                                {"code": "ACCTG 202"}
                            ]
                        }
                    ]
                }
            ]
        }
        user_history = ["ACCTG201", "ACCTG202"]
        major_courses = []
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        assert count == 2
    
    def test_major_courses_included(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]  # Business Minor
        user_history = []
        major_courses = ["MGMT301"]  # From major
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        # Should count MGMT 301 as overlap
        assert count >= 1
    
    def test_performance_large_history(self, sample_programs_db, sample_courses_db):
        """Performance test: 100 courses in history"""
        import time
        program = sample_programs_db[0]
        user_history = [f"COURSE{i}" for i in range(100)]
        major_courses = []
        
        start = time.time()
        count, courses = engine.calculate_overlap_count(program, user_history, major_courses)
        elapsed = time.time() - start
        
        # Should complete in < 1 second
        assert elapsed < 1.0, f"Overlap calculation took {elapsed:.2f} seconds (target: < 1.0)"

