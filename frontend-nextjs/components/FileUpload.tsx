'use client';

import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { FaUpload, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  status: 'success' | 'error' | 'uploading' | null;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, status }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileUpload(files[0]);
    }
  };

  return (
    <motion.div
      className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-all duration-300 cursor-pointer ${
        isDragging
          ? 'border-penn-blue bg-penn-light'
          : 'border-gray-300 hover:border-penn-blue bg-gray-50 hover:bg-penn-light'
      }`}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileSelect}
        className="hidden"
      />
      
      <div className="flex flex-col items-center gap-3">
        {status === 'success' ? (
          <>
            <FaCheckCircle className="text-4xl text-success" />
            <p className="text-success font-medium">Transcript uploaded successfully!</p>
          </>
        ) : status === 'error' ? (
          <>
            <FaTimesCircle className="text-4xl text-error" />
            <p className="text-error font-medium">Error uploading transcript</p>
          </>
        ) : status === 'uploading' ? (
          <>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <FaUpload className="text-4xl text-penn-blue" />
            </motion.div>
            <p className="text-penn-blue font-medium">Uploading...</p>
          </>
        ) : (
          <>
            <FaUpload className="text-4xl text-gray-400" />
            <div>
              <p className="text-gray-700 font-medium">
                Drop PDF here or click to upload
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Penn State Transcript (PDF format)
              </p>
            </div>
          </>
        )}
      </div>
    </motion.div>
  );
};

export default FileUpload;

