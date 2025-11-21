import React from 'react';
import { motion } from 'framer-motion';
import { FaExternalLinkAlt, FaStar, FaCheckCircle } from 'react-icons/fa';
import CourseChip from './CourseChip';

const ProgramCard = ({ program, index }) => {
  const isCompleted = program.gap_credits === 0;
  const todoItems = program.missing_courses.filter(
    c => c.status !== 'major_covered'
  );
  const coveredItems = program.missing_courses.filter(
    c => c.status === 'major_covered'
  );

  return (
    <motion.div
      className="card overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      whileHover={{ y: -5 }}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-50 to-white px-6 py-4 border-b-2 border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold text-penn-blue">
            #{index + 1}
          </span>
          <a
            href={program.program_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xl font-bold text-penn-navy hover:text-penn-blue transition-colors flex items-center gap-2 group"
          >
            {program.program_name}
            <FaExternalLinkAlt className="text-sm opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
        </div>
        
        <div className={`px-4 py-2 rounded-full font-bold text-sm ${
          isCompleted 
            ? 'bg-success text-white' 
            : 'bg-penn-light text-penn-blue'
        }`}>
          {isCompleted ? (
            <span className="flex items-center gap-2">
              <FaCheckCircle /> Completed!
            </span>
          ) : (
            `${Math.ceil(program.gap_credits)} Credits Needed`
          )}
        </div>
      </div>

      {/* Body */}
      <div className="px-6 py-5">
        {/* Triple Dip Opportunities */}
        {program.optimizations && program.optimizations.length > 0 && (
          <div className="mb-5 bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-warning font-bold mb-3">
              <FaStar className="text-xl" />
              <span>Triple Dip Opportunities</span>
            </div>
            <div className="space-y-2">
              {program.optimizations.map((opt, idx) => (
                <div key={idx} className="text-sm">
                  <span className="font-semibold text-gray-800">{opt.course}</span>
                  <span className="text-gray-600"> covers </span>
                  <span className="font-medium text-warning">{opt.matches.join(' + ')}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* To-Do List */}
        {todoItems.length > 0 ? (
          <div className="mb-5">
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
              ⚠️ To-Do List
            </h4>
            <div className="space-y-2">
              {todoItems.map((item, idx) => (
                <CourseChip key={idx} course={item} status={item.status} />
              ))}
            </div>
          </div>
        ) : isCompleted ? (
          <div className="text-center py-4 text-success font-medium">
            🎉 You have completed all requirements!
          </div>
        ) : null}

        {/* Covered by Major */}
        {coveredItems.length > 0 && (
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">
              ✅ Covered by Major
            </h4>
            <div className="space-y-2">
              {coveredItems.map((item, idx) => (
                <CourseChip key={idx} course={item} status={item.status} />
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ProgramCard;

