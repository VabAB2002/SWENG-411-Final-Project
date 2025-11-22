import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import ProgramCard from './ProgramCard';
import FilterButtons from './FilterButtons';

const ResultsSection = ({ results, allResults, studentData, activeFilter, onFilterChange }) => {
  // Calculate counts for each filter
  const counts = useMemo(() => {
    if (!allResults) return { all: 0, minors: 0, certificates: 0, genEd: 0 };
    
    return {
      all: allResults.length,
      minors: allResults.filter(p => p.program_type === 'Minors').length,
      certificates: allResults.filter(p => p.program_type === 'Certificates').length,
      genEd: allResults.filter(p => p.program_type === 'General Education').length,
    };
  }, [allResults]);

  if (!results || results.length === 0) {
    return (
      <motion.div
        className="text-center py-12"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <p className="text-gray-500 text-lg">
          {activeFilter !== 'all' 
            ? `No ${activeFilter} programs found. Try a different filter.`
            : 'No matches found. Try adjusting your criteria.'}
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
        <p className="text-gray-600 mb-6">
          Found {results.length} program{results.length !== 1 ? 's' : ''} 
          {activeFilter !== 'all' ? ` in ${activeFilter}` : ''} ranked by credits needed
        </p>

        {/* Filter Buttons */}
        <FilterButtons 
          activeFilter={activeFilter}
          onFilterChange={onFilterChange}
          counts={counts}
        />
      </div>

      {results.map((program, index) => (
        <ProgramCard 
          key={program.id} 
          program={program} 
          index={index} 
          studentData={studentData}
        />
      ))}
    </motion.div>
  );
};

export default ResultsSection;

