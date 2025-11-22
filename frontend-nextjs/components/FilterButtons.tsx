'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { FilterButtonsProps } from '@/types';

const FilterButtons: React.FC<FilterButtonsProps> = ({ activeFilter, onFilterChange, resultCounts }) => {
  const filters = [
    { id: 'all', label: 'All Programs', count: resultCounts.all },
    { id: 'Minors', label: 'Minors', count: resultCounts.Minors },
    { id: 'Certificates', label: 'Certificates', count: resultCounts.Certificates },
  ];

  return (
    <div className="flex flex-wrap gap-3 justify-center mb-8">
      {filters.map((filter) => (
        <motion.button
          key={filter.id}
          onClick={() => onFilterChange(filter.id)}
          className={`px-6 py-3 rounded-lg font-semibold transition-all border-2 ${
            activeFilter === filter.id
              ? 'bg-penn-blue text-white border-penn-blue shadow-lg'
              : 'bg-white text-penn-blue border-penn-blue hover:bg-penn-light'
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          {filter.label}
          {filter.count !== undefined && (
            <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-bold ${
              activeFilter === filter.id
                ? 'bg-white text-penn-blue'
                : 'bg-penn-light text-penn-blue'
            }`}>
              {filter.count}
            </span>
          )}
        </motion.button>
      ))}
    </div>
  );
};

export default FilterButtons;

