'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import SearchForm from '@/components/SearchForm';
import ResultsSection from '@/components/ResultsSection';
import LoadingSpinner from '@/components/LoadingSpinner';
import { getRecommendations } from '@/services/api';
import { FormData, Program } from '@/types';

export default function HomePage() {
  const [allResults, setAllResults] = useState<Program[] | null>(null);
  const [filteredResults, setFilteredResults] = useState<Program[] | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<FormData | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (formData: FormData) => {
    setIsLoading(true);
    setError(null);
    setFormData(formData);
    
    try {
      // Parse transcript into array
      const history = formData.transcript
        .replace(/\n/g, ',')
        .split(',')
        .map(c => c.trim().toUpperCase())
        .filter(c => c.length > 1);

      const requestData = {
        history,
        major: formData.major,
        gen_ed_needs: formData.genEdNeeds,
        interest_filter: formData.goal,
      };

      const response = await getRecommendations(requestData);
      
      if (response.status === 'success') {
        setAllResults(response.recommendations);
        setFilteredResults(response.recommendations);
        setActiveFilter('all');
        
        // Smooth scroll to results
        setTimeout(() => {
          resultsRef.current?.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
          });
        }, 100);
      } else {
        setError('Failed to get recommendations. Please try again.');
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Connection error. Please make sure the server is running.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFilterChange = (filter: string) => {
    setActiveFilter(filter);
    
    if (filter === 'all') {
      setFilteredResults(allResults);
    } else {
      // Filter by program type
      const filtered = allResults?.filter(program => program.program_type === filter) || [];
      setFilteredResults(filtered);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <SearchForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && (
        <motion.div
          className="mt-8 p-4 bg-red-50 border-2 border-error rounded-lg text-error text-center font-medium max-w-2xl mx-auto"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {error}
        </motion.div>
      )}

      <div ref={resultsRef} className="mt-12">
        {isLoading ? (
          <LoadingSpinner />
        ) : filteredResults ? (
          <ResultsSection 
            results={filteredResults} 
            allResults={allResults || []}
            studentData={formData}
            activeFilter={activeFilter}
            onFilterChange={handleFilterChange}
          />
        ) : null}
      </div>
    </div>
  );
}
