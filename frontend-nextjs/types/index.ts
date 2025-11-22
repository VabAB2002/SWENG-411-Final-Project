// Type definitions for the Penn State Degree Optimizer

export interface Course {
  code?: string;
  title?: string;
  credits?: string | number;
  prerequisites_raw?: string;
  [key: string]: any; // Allow additional properties from the database
}

export interface CoursesData {
  [courseCode: string]: Course;
}

export interface MissingCourse {
  text: string;
  credits?: number;
  status: 'missing' | 'major_covered' | 'subset_selection';
  subset?: string[];
  prereqs?: string;
}

export interface TripleDip {
  course: string;
  title: string;
  matches: string[];
}

export interface Program {
  id: string;
  program_name: string;
  program_type: string;
  program_url?: string;
  gap_credits: number;
  missing_courses: MissingCourse[];
  optimizations: TripleDip[];
  optimization_count: number;
  overlap_count: number;
  overlap_courses: string[];
}

export interface FormData {
  major: string;
  transcript: string;
  genEdNeeds: string[];
  goal: string;
}

export interface StudentData {
  major: string;
  transcript: string;
  genEdNeeds: string[];
  goal: string;
}

export interface RecommendationRequest {
  history: string[];
  major: string;
  gen_ed_needs: string[];
  interest_filter: string;
}

export interface RecommendationResponse {
  status: string;
  count: number;
  recommendations: Program[];
}

export interface CoursesResponse {
  status: string;
  courses: CoursesData;
}

export interface MajorsResponse {
  [key: string]: any; // Array of major strings
}

export interface UploadTranscriptResponse {
  status: string;
  courses: string[];
}

export interface ErrorResponse {
  error: string;
}

// Component Props Types
export interface SearchFormProps {
  onSubmit: (formData: FormData) => void;
  isLoading: boolean;
}

export interface ResultsSectionProps {
  results: Program[];
  allResults: Program[];
  studentData: FormData | null;
  activeFilter: string;
  onFilterChange: (filter: string) => void;
}

export interface ProgramCardProps {
  program: Program;
  studentData: FormData | null;
}

export interface CourseChipProps {
  course: MissingCourse;
}

export interface FilterButtonsProps {
  activeFilter: string;
  onFilterChange: (filter: string) => void;
  resultCounts: {
    all: number;
    Majors: number;
    Minors: number;
    Certificates: number;
  };
}

export interface PrerequisiteModalProps {
  isOpen: boolean;
  onClose: () => void;
  course: string;
  prerequisites: string;
  coursesData: CoursesData;
  userHistory: string[];
}

export interface PrerequisiteTreeProps {
  courseCode: string;
  coursesData: CoursesData;
  userHistory: string[];
  level?: number;
}

export interface FileUploadProps {
  onUpload: (courses: string[]) => void;
}

export interface LoadingSpinnerProps {
  message?: string;
}

export interface HeaderProps {
  // No props needed for now
}

