'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { FaArrowLeft, FaExternalLinkAlt, FaStar, FaCheckCircle, FaInfoCircle } from 'react-icons/fa';
import PrerequisiteModal from '@/components/PrerequisiteModal';
import { getCourses } from '@/services/api';
import { Program, StudentData, CoursesData, MissingCourse } from '@/types';

export default function DetailPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // Get program data and student data from URL params
  const [program, setProgram] = useState<Program | null>(null);
  const [studentData, setStudentData] = useState<StudentData | null>(null);
  
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedCourse, setSelectedCourse] = useState<MissingCourse | null>(null);
  const [showPrereqModal, setShowPrereqModal] = useState<boolean>(false);
  const [coursesData, setCoursesData] = useState<CoursesData>({});
  const [userHistory, setUserHistory] = useState<string[]>([]);

  useEffect(() => {
    // Parse program and student data from URL params
    const programDataStr = searchParams.get('programData');
    const studentDataStr = searchParams.get('studentData');
    
    if (programDataStr) {
      try {
        setProgram(JSON.parse(programDataStr));
      } catch (e) {
        console.error('Failed to parse program data:', e);
      }
    }
    
    if (studentDataStr) {
      try {
        setStudentData(JSON.parse(studentDataStr));
      } catch (e) {
        console.error('Failed to parse student data:', e);
      }
    }
  }, [searchParams]);

  useEffect(() => {
    // Load course data for prerequisite tree
    const loadCoursesData = async () => {
      try {
        const response = await getCourses();
        if (response.status === 'success') {
          setCoursesData(response.courses);
        }
      } catch (error) {
        console.error('Failed to load courses data:', error);
      }
    };

    loadCoursesData();

    // Parse user history from studentData
    if (studentData?.transcript) {
      const history = studentData.transcript
        .replace(/\n/g, ',')
        .split(',')
        .map(c => c.trim().toUpperCase())
        .filter(c => c.length > 1);
      setUserHistory(history);
    }
  }, [studentData]);

  if (!program) {
    return (
      <div className="container mx-auto px-4 py-8">
        <button
          onClick={() => router.push('/')}
          className="flex items-center gap-2 text-penn-blue hover:text-penn-navy mb-4 font-medium"
        >
          <FaArrowLeft /> Back to Search
        </button>
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">Program not found. Please search again.</p>
        </div>
      </div>
    );
  }

  const isCompleted = program.gap_credits === 0;

  const handleShowPrerequisites = (course: MissingCourse) => {
    setSelectedCourse(course);
    setShowPrereqModal(true);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* Back Button */}
      <button
        onClick={() => router.push('/')}
        className="flex items-center gap-2 text-penn-blue hover:text-penn-navy mb-6 font-medium transition-colors"
      >
        <FaArrowLeft /> Back to Results
      </button>

      {/* Header */}
      <motion.div
        className="bg-white rounded-xl shadow-lg p-8 mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-penn-navy mb-3">
              {program.program_name}
            </h1>
            {isCompleted ? (
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-100 text-green-800 rounded-full font-semibold">
                <FaCheckCircle /> Completed!
              </div>
            ) : (
              <p className="text-xl text-gray-700">
                {Math.ceil(program.gap_credits)} credits needed to complete
              </p>
            )}
          </div>
          {program.program_url && (
            <a
              href={program.program_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-6 py-3 bg-penn-blue text-white rounded-lg hover:bg-penn-navy transition-colors font-medium"
            >
              Official Page <FaExternalLinkAlt />
            </a>
          )}
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex border-b border-gray-200">
          {['overview', 'courses', 'progress'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 px-6 py-4 font-semibold transition-all ${
                activeTab === tab
                  ? 'bg-penn-blue text-white border-b-4 border-penn-navy'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="p-8">
          {activeTab === 'overview' && (
            <OverviewTab program={program} />
          )}
          {activeTab === 'courses' && (
            <CoursesTab 
              program={program} 
              onShowPrerequisites={handleShowPrerequisites}
            />
          )}
          {activeTab === 'progress' && (
            <ProgressTab program={program} studentData={studentData} />
          )}
        </div>
      </div>

      {/* Prerequisite Modal */}
      {selectedCourse && (
        <PrerequisiteModal
          isOpen={showPrereqModal}
          onClose={() => {
            setShowPrereqModal(false);
            setSelectedCourse(null);
          }}
          course={selectedCourse.text}
          prerequisites={selectedCourse.prereqs || ''}
          coursesData={coursesData}
          userHistory={userHistory}
        />
      )}
    </div>
  );
}

// Overview Tab Component
function OverviewTab({ program }: { program: Program }) {
  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div>
        <h2 className="text-2xl font-bold text-penn-navy mb-4">Summary</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard 
            label="Credits Needed" 
            value={Math.ceil(program.gap_credits)} 
            color="blue"
          />
          <StatCard 
            label="Courses Overlap" 
            value={program.overlap_count || 0} 
            color="green"
          />
          <StatCard 
            label="Triple Dips" 
            value={program.optimization_count || 0} 
            color="yellow"
          />
        </div>
      </div>

      {program.optimizations && program.optimizations.length > 0 && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-lg p-6">
          <h3 className="flex items-center gap-2 font-bold text-warning text-lg mb-4">
            <FaStar className="text-xl" />
            Triple Dip Opportunities
          </h3>
          <div className="space-y-3">
            {program.optimizations.map((opt, idx) => (
              <div key={idx} className="bg-white rounded-lg p-4 border border-yellow-100">
                <p className="font-semibold text-gray-800 mb-1">{opt.course}</p>
                <p className="text-sm text-gray-600">{opt.title}</p>
                <p className="text-sm text-warning font-medium mt-2">
                  Satisfies: {opt.matches.join(' + ')}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {program.overlap_courses && program.overlap_courses.length > 0 && (
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6">
          <h3 className="font-bold text-green-800 text-lg mb-3">
            Courses You&apos;ve Already Completed
          </h3>
          <div className="flex flex-wrap gap-2">
            {program.overlap_courses.map((course, idx) => (
              <span key={idx} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                {course}
              </span>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

// Courses Tab Component  
function CoursesTab({ program, onShowPrerequisites }: { program: Program; onShowPrerequisites: (course: MissingCourse) => void }) {
  const todoItems = program.missing_courses.filter(c => c.status !== 'major_covered');
  const coveredItems = program.missing_courses.filter(c => c.status === 'major_covered');

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {todoItems.length > 0 ? (
        <div>
          <h2 className="text-xl font-bold text-penn-navy mb-4">⚠️ Required Courses</h2>
          <div className="space-y-3">
            {todoItems.map((course, idx) => (
              <CourseDetailCard 
                key={idx} 
                course={course} 
                onShowPrerequisites={onShowPrerequisites}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="text-center py-12">
          <FaCheckCircle className="text-6xl text-green-500 mx-auto mb-4" />
          <p className="text-2xl font-bold text-green-600">
            🎉 You have completed all requirements!
          </p>
        </div>
      )}

      {coveredItems.length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-penn-navy mb-4">✅ Covered by Major</h2>
          <div className="space-y-2">
            {coveredItems.map((course, idx) => (
              <div key={idx} className="p-4 bg-green-50 rounded-lg border-2 border-green-200 text-green-800 font-medium">
                {course.text}
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

// Progress Tab Component
function ProgressTab({ program, studentData }: { program: Program; studentData: StudentData | null }) {
  // Calculate progress
  const coursesCompleted = studentData?.transcript?.split(',').filter(c => c.trim()).length || 0;
  const creditsCompleted = coursesCompleted * 3; // Rough estimate
  const creditsNeeded = program.gap_credits;
  const totalCredits = creditsCompleted + creditsNeeded;
  const progressPercent = totalCredits > 0 ? (creditsCompleted / totalCredits) * 100 : 0;
  const semestersRemaining = Math.ceil(creditsNeeded / 12);

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div>
        <h2 className="text-2xl font-bold text-penn-navy mb-4">Completion Status</h2>
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-medium">Progress toward completion</span>
            <span className="font-bold text-penn-blue">{Math.round(progressPercent)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-6 overflow-hidden">
            <motion.div 
              className="bg-gradient-to-r from-penn-blue to-penn-navy h-6 rounded-full flex items-center justify-end pr-2"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
            >
              {progressPercent > 10 && (
                <span className="text-white text-xs font-bold">{Math.round(progressPercent)}%</span>
              )}
            </motion.div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg border-2 border-blue-200">
          <p className="text-sm text-blue-700 font-medium mb-1">Credits Completed</p>
          <p className="text-4xl font-bold text-blue-900">{creditsCompleted}</p>
        </div>
        <div className="p-6 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg border-2 border-orange-200">
          <p className="text-sm text-orange-700 font-medium mb-1">Credits Remaining</p>
          <p className="text-4xl font-bold text-orange-900">{Math.ceil(creditsNeeded)}</p>
        </div>
      </div>

      <div className="p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border-2 border-gray-300">
        <p className="text-sm text-gray-600 mb-2">Estimated Time to Completion</p>
        <p className="text-3xl font-bold text-penn-navy">
          {semestersRemaining === 0 ? 'Complete!' : `${semestersRemaining} semester${semestersRemaining !== 1 ? 's' : ''}`}
        </p>
        {semestersRemaining > 0 && (
          <p className="text-sm text-gray-500 mt-2">
            (Based on 12 credits per semester)
          </p>
        )}
      </div>
    </motion.div>
  );
}

// Helper Components
function StatCard({ label, value, color = 'blue' }: { label: string; value: number; color?: 'blue' | 'green' | 'yellow' }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-900',
  };

  return (
    <div className={`p-6 rounded-lg border-2 text-center ${colorClasses[color]}`}>
      <p className="text-sm font-medium opacity-75 mb-1">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

function CourseDetailCard({ course, onShowPrerequisites }: { course: MissingCourse; onShowPrerequisites: (course: MissingCourse) => void }) {
  const hasPrereqs = course.prereqs && 
    course.prereqs !== 'No data available.' && 
    course.prereqs !== 'No prerequisites listed.';

  return (
    <div className="border-2 border-red-200 bg-red-50 rounded-lg p-4 hover:border-red-300 transition-colors">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="font-bold text-red-900 text-lg">{course.text}</p>
          {course.credits && (
            <p className="text-sm text-red-700 mt-1">{course.credits} credits</p>
          )}
        </div>
        {hasPrereqs && (
          <button
            onClick={() => onShowPrerequisites(course)}
            className="flex items-center gap-2 text-penn-blue hover:text-penn-navy font-medium text-sm transition-colors"
            title="View prerequisites"
          >
            <FaInfoCircle className="text-lg" />
            Prerequisites
          </button>
        )}
      </div>
    </div>
  );
}

