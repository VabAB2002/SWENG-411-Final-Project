import React from 'react';
import { motion } from 'framer-motion';
import { FaGraduationCap } from 'react-icons/fa';

const Header = () => {
  return (
    <motion.header 
      className="bg-gradient-to-r from-penn-blue to-penn-navy text-white shadow-xl sticky top-0 z-50"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: "spring", stiffness: 100 }}
    >
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-center gap-3">
          <motion.div
            animate={{ rotate: [0, -10, 10, -10, 0] }}
            transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
          >
            <FaGraduationCap className="text-4xl md:text-5xl" />
          </motion.div>
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
              Penn State Degree Optimizer
            </h1>
            <p className="text-penn-light text-sm md:text-base mt-1">
              Find your fastest path to a Minor or Certificate
            </p>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;

