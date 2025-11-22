'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaSearch, FaGraduationCap, FaClipboardList } from 'react-icons/fa';
import FileUpload from './FileUpload';
import { getMajors, uploadTranscript } from '@/services/api';
import { SearchFormProps, FormData } from '@/types';

const GENED_OPTIONS = [
  { value: 'GA', label: 'Arts (GA)' },
  { value: 'GH', label: 'Humanities (GH)' },
  { value: 'GS', label: 'Soc/Behavioral (GS)' },
  { value: 'GN', label: 'Natural Science (GN)' },
  { value: 'US', label: 'US Cultures' },
  { value: 'IL', label: "Int'l Cultures" },
];

const SearchForm: React.FC<SearchFormProps> = ({ onSubmit, isLoading }) => {
  const [majors, setMajors] = useState<string[]>([]);
  const [formData, setFormData] = useState<FormData>({
    major: '',
    transcript: '',
    genEdNeeds: [],
    goal: 'Minor',
  });
  const [uploadStatus, setUploadStatus] = useState<'success' | 'error' | 'uploading' | null>(null);

  useEffect(() => {
    loadMajors();
  }, []);

  const loadMajors = async () => {
    try {
      const majorsList = await getMajors();
      setMajors(majorsList);
    } catch (error) {
      console.error('Failed to load majors:', error);
    }
  };

  const handleFileUpload = async (file: File) => {
    setUploadStatus('uploading');
    try {
      const response = await uploadTranscript(file);
      if (response.status === 'success') {
        const existingCourses = formData.transcript.trim();
        const newCourses = response.courses.join(', ');
        setFormData(prev => ({
          ...prev,
          transcript: existingCourses 
            ? `${existingCourses}, ${newCourses}`
            : newCourses
        }));
        setUploadStatus('success');
      } else {
        setUploadStatus('error');
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus('error');
    }
  };

  const handleGenEdToggle = (value: string) => {
    setFormData(prev => ({
      ...prev,
      genEdNeeds: prev.genEdNeeds.includes(value)
        ? prev.genEdNeeds.filter(v => v !== value)
        : [...prev.genEdNeeds, value]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <motion.div
      className="card p-8 max-w-4xl mx-auto"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Major Selection */}
        <div>
          <label className="flex items-center gap-2 text-penn-navy font-bold text-sm uppercase tracking-wide mb-3">
            <FaGraduationCap className="text-penn-blue" />
            1. Select Your Major
          </label>
          <select
            value={formData.major}
            onChange={(e) => setFormData(prev => ({ ...prev, major: e.target.value }))}
            className="input-field"
            required
          >
            <option value="">-- Select Your Major --</option>
            {majors.map(major => (
              <option key={major} value={major}>{major}</option>
            ))}
          </select>
        </div>

        {/* Transcript Input */}
        <div>
          <label className="flex items-center gap-2 text-penn-navy font-bold text-sm uppercase tracking-wide mb-3">
            <FaClipboardList className="text-penn-blue" />
            2. Paste Transcript OR Upload PDF
          </label>
          <FileUpload onFileUpload={handleFileUpload} status={uploadStatus} />
          <textarea
            value={formData.transcript}
            onChange={(e) => setFormData(prev => ({ ...prev, transcript: e.target.value }))}
            placeholder="MATH 140, ECON 102, ENGL 15..."
            className="input-field mt-3 min-h-[120px] resize-y"
            required
          />
        </div>

        {/* GenEd Selection */}
        <div>
          <label className="text-penn-navy font-bold text-sm uppercase tracking-wide mb-3 block">
            3. GenEds Needed
          </label>
          <div className="flex flex-wrap gap-2">
            {GENED_OPTIONS.map(option => (
              <motion.label
                key={option.value}
                className={`checkbox-label ${
                  formData.genEdNeeds.includes(option.value) ? 'checkbox-label-checked' : ''
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <input
                  type="checkbox"
                  checked={formData.genEdNeeds.includes(option.value)}
                  onChange={() => handleGenEdToggle(option.value)}
                  className="sr-only"
                />
                <span className="text-sm font-medium">{option.label}</span>
              </motion.label>
            ))}
          </div>
        </div>

        {/* Goal Selection */}
        <div>
          <label className="text-penn-navy font-bold text-sm uppercase tracking-wide mb-3 block">
            4. Goal
          </label>
          <select
            value={formData.goal}
            onChange={(e) => setFormData(prev => ({ ...prev, goal: e.target.value }))}
            className="input-field"
          >
            <option value="Minor">Find a Minor</option>
            <option value="Certificate">Find a Certificate</option>
          </select>
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={isLoading}
          className="w-full btn-primary flex items-center justify-center gap-2 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={!isLoading ? { scale: 1.02 } : {}}
          whileTap={!isLoading ? { scale: 0.98 } : {}}
        >
          <FaSearch />
          {isLoading ? 'Analyzing...' : 'Analyze My Options'}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default SearchForm;

