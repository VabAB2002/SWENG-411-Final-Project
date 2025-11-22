'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaTimes, FaInfoCircle } from 'react-icons/fa';
import PrerequisiteTree from './PrerequisiteTree';
import { PrerequisiteModalProps } from '@/types';

const PrerequisiteModal: React.FC<PrerequisiteModalProps> = ({ 
  isOpen, 
  onClose, 
  course, 
  prerequisites, 
  coursesData = {}, 
  userHistory = [] 
}) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
              <div className="bg-penn-blue text-white px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FaInfoCircle className="text-2xl" />
                  <h3 className="text-xl font-bold">Course Prerequisites</h3>
                </div>
                <button
                  onClick={onClose}
                  className="text-white hover:text-gray-200 transition-colors"
                >
                  <FaTimes className="text-xl" />
                </button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {coursesData && Object.keys(coursesData).length > 0 ? (
                  <PrerequisiteTree 
                    courseCode={course} 
                    userHistory={userHistory}
                    coursesData={coursesData}
                  />
                ) : (
                  <div>
                    <div className="bg-penn-light rounded-lg p-4 mb-4">
                      <h4 className="font-bold text-penn-blue text-lg mb-2">{course}</h4>
                    </div>
                    
                    <div className="prose prose-sm max-w-none">
                      <h5 className="text-gray-700 font-semibold mb-2">Prerequisites:</h5>
                      <p className="text-gray-600 whitespace-pre-wrap leading-relaxed">
                        {prerequisites || 'No prerequisites listed.'}
                      </p>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="bg-gray-50 px-6 py-4 flex justify-end">
                <button
                  onClick={onClose}
                  className="btn-primary"
                >
                  Got it
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default PrerequisiteModal;

