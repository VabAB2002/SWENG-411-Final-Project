import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import ResultsSection from './components/ResultsSection';
import LoadingSpinner from './components/LoadingSpinner';
import { getRecommendations } from './services/api';

function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const resultsRef = useRef(null);

  const handleSubmit = async (formData) => {
    setIsLoading(true);
    setError(null);
    
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
        setResults(response.recommendations);
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

  return (
    <div className="min-h-screen">
      <Header />
      
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
          ) : results ? (
            <ResultsSection results={results} />
          ) : null}
        </div>
      </main>

      <footer className="bg-penn-navy text-white py-8 mt-20">
        <div className="container mx-auto px-4 text-center">
          <p className="text-penn-light">
            Penn State Degree Optimizer • Built with React + Tailwind CSS
          </p>
          <p className="text-sm text-penn-slate mt-2">
            Helping students find their optimal path to graduation
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

