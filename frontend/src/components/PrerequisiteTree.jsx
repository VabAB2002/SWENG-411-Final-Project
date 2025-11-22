import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaCheckCircle, FaTimesCircle, FaCircle, FaChevronDown, FaChevronRight } from 'react-icons/fa';

function PrerequisiteTree({ course, userHistory = [], coursesData = {} }) {
  const [prerequisites, setPrerequisites] = useState([]);
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  useEffect(() => {
    parsePrerequisites();
  }, [course, coursesData]);

  const parsePrerequisites = () => {
    // Get prerequisite data for the course
    const courseData = coursesData[course.replace(/\s+/g, '')];
    
    if (!courseData || !courseData.prerequisites_raw) {
      setPrerequisites([]);
      return;
    }

    const prereqText = courseData.prerequisites_raw;
    
    // Extract course codes using regex (matches patterns like CMPSC 121, MATH 140, etc.)
    const coursePattern = /[A-Z]{2,5}\s*\d{3}[A-Z]?/g;
    const matches = prereqText.match(coursePattern) || [];
    
    // Remove duplicates and format
    const uniquePrereqs = [...new Set(matches)].map(code => {
      const normalized = code.replace(/\s+/g, '');
      return {
        code: code,
        normalized: normalized,
        status: checkPrereqStatus(normalized, userHistory),
        raw: prereqText
      };
    });

    setPrerequisites(uniquePrereqs);
  };

  const checkPrereqStatus = (courseCode, history) => {
    // Normalize course codes for comparison
    const normalizedHistory = history.map(c => 
      c.replace(/\s+/g, '').toUpperCase()
    );
    const normalizedCode = courseCode.replace(/\s+/g, '').toUpperCase();

    if (normalizedHistory.includes(normalizedCode)) {
      return 'met';
    }

    // Check if this prerequisite itself has prerequisites that are met
    const prereqData = coursesData[normalizedCode];
    if (prereqData && prereqData.prerequisites_raw) {
      // Has prerequisites - check if they're met
      const nestedPattern = /[A-Z]{2,5}\s*\d{3}[A-Z]?/g;
      const nestedMatches = prereqData.prerequisites_raw.match(nestedPattern) || [];
      const allMet = nestedMatches.every(nested => 
        normalizedHistory.includes(nested.replace(/\s+/g, '').toUpperCase())
      );
      if (allMet && nestedMatches.length > 0) {
        return 'available';
      }
    } else if (!prereqData || !prereqData.prerequisites_raw) {
      // No prerequisites - available to take
      return 'available';
    }

    return 'notMet';
  };

  const toggleNode = (courseCode) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(courseCode)) {
        newSet.delete(courseCode);
      } else {
        newSet.add(courseCode);
      }
      return newSet;
    });
  };

  const getNestedPrerequisites = (courseCode) => {
    const normalized = courseCode.replace(/\s+/g, '').toUpperCase();
    const courseData = coursesData[normalized];
    
    if (!courseData || !courseData.prerequisites_raw) {
      return [];
    }

    const coursePattern = /[A-Z]{2,5}\s*\d{3}[A-Z]?/g;
    const matches = courseData.prerequisites_raw.match(coursePattern) || [];
    
    return [...new Set(matches)].map(code => {
      const norm = code.replace(/\s+/g, '');
      return {
        code: code,
        normalized: norm,
        status: checkPrereqStatus(norm, userHistory)
      };
    });
  };

  const renderPrereqNode = (prereq, depth = 0, isLast = false) => {
    const hasNested = coursesData[prereq.normalized]?.prerequisites_raw;
    const isExpanded = expandedNodes.has(prereq.code);
    const nestedPrereqs = hasNested ? getNestedPrerequisites(prereq.code) : [];

    return (
      <motion.div
        key={prereq.code}
        className="relative"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className={`flex items-start gap-3 py-2 px-3 rounded-lg mb-2 ${
          depth > 0 ? 'ml-8' : ''
        } ${
          prereq.status === 'met' 
            ? 'bg-green-50 border border-green-200' 
            : prereq.status === 'available'
            ? 'bg-blue-50 border border-blue-200'
            : 'bg-red-50 border border-red-200'
        }`}>
          {/* Connector line */}
          {depth > 0 && (
            <div className="absolute left-0 top-0 w-8 h-full flex items-start pt-5">
              <div className="w-full h-0.5 bg-gray-300"></div>
            </div>
          )}

          {/* Expand/collapse button */}
          {hasNested && nestedPrereqs.length > 0 ? (
            <button
              onClick={() => toggleNode(prereq.code)}
              className="text-gray-600 hover:text-gray-800 flex-shrink-0 mt-1"
            >
              {isExpanded ? <FaChevronDown /> : <FaChevronRight />}
            </button>
          ) : (
            <div className="w-4"></div>
          )}

          {/* Status Icon */}
          <div className="flex-shrink-0 mt-1">
            {prereq.status === 'met' ? (
              <FaCheckCircle className="text-green-600 text-lg" />
            ) : prereq.status === 'available' ? (
              <FaCircle className="text-blue-500 text-lg" />
            ) : (
              <FaTimesCircle className="text-red-600 text-lg" />
            )}
          </div>

          {/* Course Info */}
          <div className="flex-1">
            <p className={`font-semibold ${
              prereq.status === 'met' 
                ? 'text-green-800' 
                : prereq.status === 'available'
                ? 'text-blue-800'
                : 'text-red-800'
            }`}>
              {prereq.code}
            </p>
            <p className="text-xs text-gray-600 mt-1">
              {prereq.status === 'met' 
                ? 'Completed ✓' 
                : prereq.status === 'available'
                ? 'Available to take'
                : 'Prerequisites not met'}
            </p>
          </div>
        </div>

        {/* Nested prerequisites */}
        <AnimatePresence>
          {isExpanded && nestedPrereqs.length > 0 && (
            <motion.div
              className="ml-4"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              {nestedPrereqs.map((nested, idx) => 
                renderPrereqNode(nested, depth + 1, idx === nestedPrereqs.length - 1)
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    );
  };

  if (!prerequisites || prerequisites.length === 0) {
    return (
      <div className="text-center py-6 text-gray-500">
        <p>No prerequisites found for this course.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <h4 className="font-bold text-gray-800 mb-2">Legend:</h4>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <FaCheckCircle className="text-green-600" />
            <span className="text-gray-700">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <FaCircle className="text-blue-500" />
            <span className="text-gray-700">Available to take</span>
          </div>
          <div className="flex items-center gap-2">
            <FaTimesCircle className="text-red-600" />
            <span className="text-gray-700">Not yet available</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border-2 border-gray-200 p-4">
        <h3 className="font-bold text-penn-navy text-lg mb-4">
          Prerequisites for {course}
        </h3>
        {prerequisites.map((prereq, idx) => 
          renderPrereqNode(prereq, 0, idx === prerequisites.length - 1)
        )}
      </div>
    </div>
  );
}

export default PrerequisiteTree;

