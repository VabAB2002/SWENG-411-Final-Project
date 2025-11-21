import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FaInfoCircle } from 'react-icons/fa';
import PrerequisiteModal from './PrerequisiteModal';

const CourseChip = ({ course, status }) => {
  const [showModal, setShowModal] = useState(false);

  const getStatusStyles = () => {
    switch (status) {
      case 'major_covered':
        return 'bg-green-50 text-success border-green-200';
      case 'subset_missing':
        return 'bg-orange-50 text-warning border-orange-200';
      default:
        return 'bg-red-50 text-error border-red-200';
    }
  };

  const hasPrereqs = course.prereqs && 
    course.prereqs !== 'No data available.' && 
    course.prereqs !== 'No prerequisites listed.';

  return (
    <>
      <motion.div
        className={`flex items-center justify-between gap-2 px-4 py-2 rounded-lg border-2 ${getStatusStyles()}`}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        whileHover={{ scale: 1.02 }}
      >
        <span className="font-medium text-sm">{course.text}</span>
        {hasPrereqs && (
          <button
            onClick={() => setShowModal(true)}
            className="text-current hover:opacity-70 transition-opacity flex-shrink-0"
            title="View prerequisites"
          >
            <FaInfoCircle className="text-lg" />
          </button>
        )}
      </motion.div>

      {hasPrereqs && (
        <PrerequisiteModal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          course={course.text}
          prerequisites={course.prereqs}
        />
      )}
    </>
  );
};

export default CourseChip;

