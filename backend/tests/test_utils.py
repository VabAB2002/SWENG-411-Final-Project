"""
Unit tests for core utility functions in recommendation_engine.py
"""
import pytest
import recommendation_engine as engine

class TestNormalizeCode:
    """Tests for normalize_code() function."""
    
    def test_normalize_with_space(self):
        assert engine.normalize_code("ECON 102") == "ECON102"
    
    def test_normalize_lowercase(self):
        assert engine.normalize_code("econ 102") == "ECON102"
    
    def test_normalize_double_space(self):
        assert engine.normalize_code("ECON  102") == "ECON102"
    
    def test_normalize_empty_string(self):
        assert engine.normalize_code("") == ""
    
    def test_normalize_whitespace_only(self):
        assert engine.normalize_code("   ") == ""
    
    def test_normalize_none(self):
        assert engine.normalize_code(None) == ""
    
    def test_normalize_no_space(self):
        assert engine.normalize_code("CMPSC465") == "CMPSC465"
    
    def test_normalize_special_chars(self):
        assert engine.normalize_code("ECON-102") == "ECON-102"  # Note: doesn't remove hyphens


class TestParseCourseString:
    """Tests for parse_course_string() function."""
    
    def test_parse_with_space(self):
        dept, number = engine.parse_course_string("ECON 102")
        assert dept == "ECON"
        assert number == 102
    
    def test_parse_no_space(self):
        dept, number = engine.parse_course_string("CMPSC465")
        assert dept == "CMPSC"
        assert number == 465
    
    def test_parse_with_letter_suffix(self):
        dept, number = engine.parse_course_string("MATH 140A")
        assert dept == "MATH"
        assert number == 140  # Letter suffix ignored
    
    def test_parse_invalid_no_dept(self):
        dept, number = engine.parse_course_string("ABC")
        assert dept is None
        assert number == 0
    
    def test_parse_empty_string(self):
        dept, number = engine.parse_course_string("")
        assert dept is None
        assert number == 0
    
    def test_parse_numbers_only(self):
        dept, number = engine.parse_course_string("123")
        assert dept is None
        assert number == 0
    
    def test_parse_none(self):
        dept, number = engine.parse_course_string(None)
        assert dept is None
        assert number == 0


class TestGetCourseCredits:
    """Tests for get_course_credits() function."""
    
    def test_course_exists_with_float_credits(self, sample_courses_db):
        credits = engine.get_course_credits("ECON 102", sample_courses_db)
        assert credits == 3.0
    
    def test_course_exists_with_range_credits(self, sample_courses_db):
        # Add a course with range credits
        sample_courses_db["TEST100"] = {"credits": "3-4", "courseCode": "TEST 100"}
        credits = engine.get_course_credits("TEST 100", sample_courses_db)
        assert credits == 3.0  # Should take first value
    
    def test_course_exists_with_decimal_credits(self, sample_courses_db):
        sample_courses_db["TEST200"] = {"credits": 3.5, "courseCode": "TEST 200"}
        credits = engine.get_course_credits("TEST 200", sample_courses_db)
        assert credits == 3.5
    
    def test_course_not_in_database(self, sample_courses_db):
        credits = engine.get_course_credits("XYZ 999", sample_courses_db)
        assert credits == 3.0  # Default value
    
    def test_course_with_none_credits(self, sample_courses_db):
        sample_courses_db["TEST300"] = {"credits": None, "courseCode": "TEST 300"}
        credits = engine.get_course_credits("TEST 300", sample_courses_db)
        assert credits == 3.0  # Default value
    
    def test_course_with_custom_default(self, sample_courses_db):
        credits = engine.get_course_credits("XYZ 999", sample_courses_db, default=4.0)
        assert credits == 4.0


class TestGetCoursePrereqs:
    """Tests for get_course_prereqs() function."""
    
    def test_course_with_prerequisites(self, sample_courses_db):
        prereqs = engine.get_course_prereqs("ECON 302", sample_courses_db)
        assert prereqs == "Prerequisite ECON 102"
    
    def test_course_without_prerequisites(self, sample_courses_db):
        prereqs = engine.get_course_prereqs("ECON 102", sample_courses_db)
        assert prereqs == "No prerequisites listed."
    
    def test_course_not_in_database(self, sample_courses_db):
        prereqs = engine.get_course_prereqs("XYZ 999", sample_courses_db)
        assert prereqs == "No data available."
    
    def test_course_missing_prereqs_key(self, sample_courses_db):
        sample_courses_db["TEST400"] = {"courseCode": "TEST 400", "title": "Test"}
        prereqs = engine.get_course_prereqs("TEST 400", sample_courses_db)
        assert prereqs == "No prerequisites listed."

