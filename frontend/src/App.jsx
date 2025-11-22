import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import DetailPage from './pages/DetailPage';

function App() {
  return (
    <div className="min-h-screen">
      <Header />
      
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/program/:programId" element={<DetailPage />} />
      </Routes>

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

