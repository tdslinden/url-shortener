import axios, { AxiosError } from 'axios';
import type {
  URLStatsResponse,
  CreateURLRequest,
  CreateURLResponse,
  APIError
} from '@/types/url.types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

export const urlShortenerAPI = {
  createURL: async (data: CreateURLRequest): Promise<CreateURLResponse> => {
    try {
      const response = await api.post<CreateURLResponse>('/urls', data);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  },

  getStats: async (shortCode: string): Promise<URLStatsResponse> => {
    try {
      const response = await api.get<URLStatsResponse>(`/urls/${shortCode}/stats`);
      return response.data;
    } catch (error) {
      throw handleAPIError(error);
    }
  }
}

function handleAPIError(error: unknown): Error {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<APIError>;
    const message: string = axiosError.response?.data?.error || "An API error occurred."
    return new Error(message);
  }
  return new Error("An unexpected error occurred.")
}