import axios from 'axios';
import { SecureStorage } from './SecureStorage';

// Default to localhost for emulator testing, or VITE_API_URL in prod
const baseURL = import.meta.env.VITE_API_URL || 'http://10.0.2.2:8000';

export const ApiClient = axios.create({
  baseURL,
  timeout: 10000,
});

ApiClient.interceptors.request.use(async (config) => {
  const token = await SecureStorage.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

ApiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      // Network error (Offline or API unreachable)
      console.error('Network Error: The API is unreachable. Please check your connection.');
      // In a real app, trigger a Global UI Toast here
      return Promise.reject(new Error('Network error. You might be offline.'));
    }
    
    if (error.response.status === 401) {
      // Unauthorized: clear token and redirect to login
      SecureStorage.removeToken();
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);
