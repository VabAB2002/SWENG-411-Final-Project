-- Penn State Course Recommendation System - Supabase Schema
-- This schema is designed to store academic program and course data

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table 1: Programs
-- Stores all academic programs (Majors, Minors, Certificates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS programs (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('Majors', 'Minors', 'Certificates', 'General Education')),
    url TEXT,
    rules JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast filtering by program type
CREATE INDEX IF NOT EXISTS idx_programs_type ON programs(type);

-- Index for JSONB rules (for future queries if needed)
CREATE INDEX IF NOT EXISTS idx_programs_rules ON programs USING GIN(rules);

-- ============================================================================
-- Table 2: Courses
-- Stores all course information including prerequisites and GenEd attributes
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses (
    course_code_normalized TEXT PRIMARY KEY,
    course_code TEXT NOT NULL,
    title TEXT,
    credits NUMERIC(4,1) DEFAULT 3.0,
    description TEXT,
    prerequisites_list TEXT[] DEFAULT ARRAY[]::TEXT[],
    prerequisites_raw TEXT,
    gen_ed_attributes TEXT[] DEFAULT ARRAY[]::TEXT[],
    cultural_attributes TEXT[] DEFAULT ARRAY[]::TEXT[],
    inter_domain BOOLEAN DEFAULT FALSE,
    source_program TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast search by course code
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(course_code);

-- Index for GenEd attributes (GIN index for array searching)
CREATE INDEX IF NOT EXISTS idx_courses_gen_ed ON courses USING GIN(gen_ed_attributes);

-- Index for cultural attributes
CREATE INDEX IF NOT EXISTS idx_courses_cultural ON courses USING GIN(cultural_attributes);

-- Index for inter-domain courses
CREATE INDEX IF NOT EXISTS idx_courses_inter_domain ON courses(inter_domain) WHERE inter_domain = TRUE;

-- ============================================================================
-- Table 3: Course Equivalencies
-- Stores course equivalency mappings for prerequisite checking
-- ============================================================================
CREATE TABLE IF NOT EXISTS course_equivalencies (
    course_code TEXT PRIMARY KEY,
    equivalents TEXT[] DEFAULT ARRAY[]::TEXT[],
    reason TEXT,
    auto_generated BOOLEAN DEFAULT FALSE,
    type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for searching equivalents
CREATE INDEX IF NOT EXISTS idx_equivalencies_array ON course_equivalencies USING GIN(equivalents);

-- ============================================================================
-- Table 4: Prerequisite Configuration
-- Stores system configuration for prerequisite matching rules
-- ============================================================================
CREATE TABLE IF NOT EXISTS prerequisite_config (
    id SERIAL PRIMARY KEY,
    config_name TEXT UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast config lookup
CREATE INDEX IF NOT EXISTS idx_prereq_config_name ON prerequisite_config(config_name);

-- ============================================================================
-- Update Timestamp Trigger Function
-- Automatically updates the updated_at column
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update triggers to all tables
CREATE TRIGGER update_programs_updated_at
    BEFORE UPDATE ON programs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_courses_updated_at
    BEFORE UPDATE ON courses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equivalencies_updated_at
    BEFORE UPDATE ON course_equivalencies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prereq_config_updated_at
    BEFORE UPDATE ON prerequisite_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Row Level Security (RLS) Policies
-- For production: Enable RLS and create appropriate policies
-- For development: Tables are publicly readable
-- ============================================================================

-- Note: RLS is disabled by default for ease of development
-- To enable in production, uncomment and configure appropriate policies:

-- ALTER TABLE programs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE course_equivalencies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE prerequisite_config ENABLE ROW LEVEL SECURITY;

-- Example read policy (uncomment to use):
-- CREATE POLICY "Public read access" ON programs FOR SELECT USING (true);

-- ============================================================================
-- Helpful Queries for Verification
-- ============================================================================

-- Check table row counts:
-- SELECT 'programs' as table_name, COUNT(*) FROM programs
-- UNION ALL
-- SELECT 'courses', COUNT(*) FROM courses
-- UNION ALL
-- SELECT 'course_equivalencies', COUNT(*) FROM course_equivalencies
-- UNION ALL
-- SELECT 'prerequisite_config', COUNT(*) FROM prerequisite_config;

-- Check GenEd courses:
-- SELECT course_code, title, gen_ed_attributes 
-- FROM courses 
-- WHERE array_length(gen_ed_attributes, 1) > 0 
-- LIMIT 10;

-- Check programs by type:
-- SELECT type, COUNT(*) FROM programs GROUP BY type;

-- ============================================================================
-- Schema Version
-- ============================================================================
COMMENT ON TABLE programs IS 'Academic programs (v1.0): Stores majors, minors, certificates, and GenEd requirements';
COMMENT ON TABLE courses IS 'Course catalog (v1.0): Stores all course information and metadata';
COMMENT ON TABLE course_equivalencies IS 'Course equivalencies (v1.0): Maps equivalent courses for prerequisite checking';
COMMENT ON TABLE prerequisite_config IS 'System configuration (v1.0): Stores prerequisite matching rules and settings';

