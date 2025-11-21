import React from 'react';
import { motion } from 'framer-motion';

const LoadingSpinner = ({ message = "Analyzing your options..." }) => {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative w-20 h-20">
        <motion.div
          className="absolute inset-0 border-4 border-penn-light rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        <motion.div
          className="absolute inset-0 border-4 border-transparent border-t-penn-blue rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
        />
      </div>
      <motion.p
        className="mt-6 text-penn-blue font-medium text-lg"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {message}
      </motion.p>
    </div>
  );
};

export default LoadingSpinner;

