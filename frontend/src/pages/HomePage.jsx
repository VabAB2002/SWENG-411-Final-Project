import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import SearchForm from '../components/SearchForm';
import ResultsSection from '../components/ResultsSection';
import LoadingSpinner from '../components/LoadingSpinner';
import { getRecommendations } from '../services/api';

function HomePage() {
  const [allResults, setAllResults] = useState(null); // Store all results
  const [filteredResults, setFilteredResults] = useState(null); // Store filtered results
  const [activeFilter, setActiveFilter] = useState('all'); // Current filter
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState(null); // Store form data for passing to detail page
  const resultsRef = useRef(null);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    setFormData(formData); // Save form data
    
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
        setFilteredResults(response.recommendations); // Initially show all
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

  const handleFilterChange = (filter) => {
    setActiveFilter(filter);
    
    if (filter === 'all') {
      setFilteredResults(allResults);
    } else {
      // Filter by program type
      const filtered = allResults.filter(program => program.program_type === filter);
      setFilteredResults(filtered);
    }
  };

  return (
    <main className="container mx-auto px-4 py-8 max-w-7xl">
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
            allResults={allResults}
            studentData={formData}
            activeFilter={activeFilter}
            onFilterChange={handleFilterChange}
          />
        ) : null}
      </div>
    </main>
  );
}

export default HomePage;

