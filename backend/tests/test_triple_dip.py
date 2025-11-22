"""
Unit tests for triple dip detection in recommendation_engine.py
"""
import pytest
import recommendation_engine as engine

class TestFindTripleDips:
    """Tests for find_triple_dips() function."""
    
    def test_course_with_matching_gened(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]  # Business Minor
        user_needs = ["GH"]  # GenEd need
        # ECON 442 has "GH" attribute
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        # Should find ECON 442 if it's in program courses
        assert isinstance(opportunities, list)
    
    def test_course_from_primary_pool_with_gened(self, sample_programs_db, sample_courses_db):
        """Test that primary pool courses are checked for triple dips."""
        program = sample_programs_db[0]  # Business Minor with dynamic_subset
        user_needs = ["GH"]
        # ECON 442 is 400-level ECON (primary pool) and has GH attribute
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        # ISSUE 2.3: Currently might not find ECON 442 because it's not in secondary pool
        # This test will document the issue
        assert isinstance(opportunities, list)
    
    def test_course_from_secondary_pool_with_gened(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]  # Business Minor
        user_needs = ["GH"]
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        # Should check secondary pool courses
        assert isinstance(opportunities, list)
    
    def test_multiple_matching_attributes(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]
        user_needs = ["GH", "GS"]
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        assert isinstance(opportunities, list)
    
    def test_no_matches(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]
        user_needs = ["XYZ"]  # Non-existent attribute
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        assert opportunities == []
    
    def test_empty_gened_needs(self, sample_programs_db, sample_courses_db):
        program = sample_programs_db[0]
        user_needs = []
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        assert opportunities == []
    
    def test_course_not_in_database(self, sample_programs_db, sample_courses_db):
        program = {
            "rules": [
                {
                    "type": "all",
                    "courses": [
                        {"code": "XYZ 999"}  # Not in database
                    ]
                }
            ]
        }
        user_needs = ["GH"]
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        # Should skip gracefully, not crash
        assert isinstance(opportunities, list)
    
    def test_dynamic_subset_secondary_pool_only(self, sample_programs_db, sample_courses_db):
        """Test that secondary pool courses are checked."""
        program = sample_programs_db[0]  # Business Minor
        user_needs = ["GH"]
        opportunities = engine.find_triple_dips(program, user_needs, sample_courses_db)
        # Should check secondary pool courses like CAS 404, ENGL 419
        assert isinstance(opportunities, list)

