import React from 'react';
import { motion } from 'framer-motion';
import ProgramCard from './ProgramCard';

const ResultsSection = ({ results }) => {
  if (!results || results.length === 0) {
    return (
      <motion.div
        className="text-center py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <p className="text-gray-500 text-lg">
          No matches found. Try adjusting your criteria.
        </p>
      </motion.div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-penn-blue mb-2">
          Your Personalized Recommendations
        </h2>
        <p className="text-gray-600">
          Found {results.length} program{results.length !== 1 ? 's' : ''} ranked by credits needed
        </p>
      </div>

      {results.map((program, index) => (
        <ProgramCard key={program.id} program={program} index={index} />
      ))}
    </motion.div>
  );
};

export default ResultsSection;

