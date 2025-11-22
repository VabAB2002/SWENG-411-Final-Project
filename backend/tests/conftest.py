"""
Pytest configuration and shared fixtures for recommendation engine tests.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import recommendation_engine as engine

@pytest.fixture
def sample_courses_db():
    """Sample courses database for testing."""
    return {
        "ECON102": {
            "courseCode": "ECON 102",
            "title": "Introductory Microeconomic Analysis",
            "credits": 3.0,
            "prerequisites_raw": "",
            "genEdAttributes": []
        },
        "ECON104": {
            "courseCode": "ECON 104",
            "title": "Introductory Macroeconomic Analysis",
            "credits": 3.0,
            "prerequisites_raw": "",
            "genEdAttributes": []
        },
        "ECON302": {
            "courseCode": "ECON 302",
            "title": "Intermediate Microeconomic Analysis",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite ECON 102",
            "genEdAttributes": []
        },
        "ECON442": {
            "courseCode": "ECON 442",
            "title": "Advanced Economics",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite ECON 302",
            "genEdAttributes": ["GH"]
        },
        "ECON471": {
            "courseCode": "ECON 471",
            "title": "Growth and Development",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite ECON 302 or ECON 304",
            "genEdAttributes": []
        },
        "CMPSC131": {
            "courseCode": "CMPSC 131",
            "title": "Programming and Computation I",
            "credits": 3.0,
            "prerequisites_raw": "",
            "genEdAttributes": []
        },
        "CMPSC132": {
            "courseCode": "CMPSC 132",
            "title": "Programming and Computation II",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite CMPSC 131",
            "genEdAttributes": []
        },
        "CMPSC465": {
            "courseCode": "CMPSC 465",
            "title": "Data Structures and Algorithms",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite CMPSC 132 and MATH 140",
            "genEdAttributes": []
        },
        "MATH140": {
            "courseCode": "MATH 140",
            "title": "Calculus with Analytic Geometry I",
            "credits": 4.0,
            "prerequisites_raw": "",
            "genEdAttributes": []
        },
        "MGMT301": {
            "courseCode": "MGMT 301",
            "title": "Basic Management Concepts",
            "credits": 3.0,
            "prerequisites_raw": "Prerequisite ECON 102 or ECON 104",
            "genEdAttributes": []
        }
    }

@pytest.fixture
def sample_programs_db():
    """Sample programs database for testing."""
    return [
        {
            "id": "Business",
            "type": "Minors",
            "url": "https://example.com/business",
            "rules": [
                {
                    "name": "Business Core",
                    "type": "all",
                    "credits_needed": 6,
                    "courses": [
                        {"code": "MGMT 301", "credits": 3},
                        {"code": "MKTG 301W", "credits": 3}
                    ]
                },
                {
                    "name": "Supporting Courses (select 6 credits)",
                    "type": "dynamic_subset",
                    "credits_needed": 6,
                    "constraints": {
                        "primary_pool": {
                            "departments": ["ACCTG", "BA", "EBF", "ECON", "ENTR", "FIN", "HPA", "IB", "LHR", "MIS", "MGMT", "MKTG", "SCM", "STAT"],
                            "level_min": 400,
                            "level_max": 999,
                            "min_credits_needed": 3
                        },
                        "secondary_pool": {
                            "courses": ["CAS 404", "ENGL 419"]
                        }
                    }
                }
            ]
        },
        {
            "id": "Economics",
            "type": "Minors",
            "url": "https://example.com/economics",
            "rules": [
                {
                    "name": "Prescribed Courses (12 credits)",
                    "type": "all",
                    "credits_needed": 12,
                    "courses": [
                        {"code": "ECON 102", "credits": 3},
                        {"code": "ECON 104", "credits": 3},
                        {"code": "ECON 302", "credits": 3},
                        {"code": "ECON 304", "credits": 3}
                    ]
                },
                {
                    "name": "Supporting Courses and Related Areas (select 6 credits)",
                    "type": "dynamic_subset",
                    "credits_needed": 6,
                    "constraints": {
                        "primary_pool": {
                            "departments": ["ECON"],
                            "level_min": 400,
                            "level_max": 499,
                            "min_credits_needed": 0
                        },
                        "secondary_pool": {
                            "courses": ["ECON 402", "ECON 471"]
                        }
                    }
                }
            ]
        }
    ]

@pytest.fixture
def sample_equivalency_map():
    """Sample equivalency map for testing."""
    return {
        "MATH140": {
            "equivalents": ["MATH 140A", "MATH 140B"],
            "reason": "Course equivalency",
            "type": "exact"
        }
    }

@pytest.fixture
def sample_prereq_config():
    """Sample prerequisite configuration for testing."""
    return {
        "hierarchy_rules": {
            "enabled": True,
            "same_department_higher_level": True,
            "minimum_level_difference": 0
        }
    }

