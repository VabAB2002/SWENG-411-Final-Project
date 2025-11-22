import axios, { AxiosInstance } from 'axios';
import { 
  RecommendationRequest, 
  RecommendationResponse, 
  UploadTranscriptResponse,
  CoursesResponse 
} from '@/types';

// Use environment variable for API base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5001';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMajors = async (): Promise<string[]> => {
  try {
    const response = await api.get<string[]>('/majors');
    return response.data;
  } catch (error) {
    console.error('Error fetching majors:', error);
    throw error;
  }
};

export const uploadTranscript = async (file: File): Promise<UploadTranscriptResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<UploadTranscriptResponse>('/upload_transcript', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading transcript:', error);
    throw error;
  }
};

export const getRecommendations = async (data: RecommendationRequest): Promise<RecommendationResponse> => {
  try {
    const response = await api.post<RecommendationResponse>('/recommend', data);
    return response.data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

export const getCourses = async (): Promise<CoursesResponse> => {
  try {
    const response = await api.get<CoursesResponse>('/courses');
    return response.data;
  } catch (error) {
    console.error('Error fetching courses:', error);
    throw error;
  }
};

export default api;

