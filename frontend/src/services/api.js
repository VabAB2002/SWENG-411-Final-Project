import axios from 'axios';

const API_BASE_URL = import.meta.env.DEV 
  ? 'http://127.0.0.1:5001'
  : '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMajors = async () => {
  try {
    const response = await api.get('/majors');
    return response.data;
  } catch (error) {
    console.error('Error fetching majors:', error);
    throw error;
  }
};

export const uploadTranscript = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload_transcript', formData, {
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

export const getRecommendations = async (data) => {
  try {
    const response = await api.post('/recommend', data);
    return response.data;
  } catch (error) {
    console.error('Error getting recommendations:', error);
    throw error;
  }
};

export default api;

