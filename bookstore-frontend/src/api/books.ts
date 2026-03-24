import axiosInstance from '@/lib/axios';
import { Book, BookFilter } from '@/types';

export const booksAPI = {
  getBooks: async (filters?: BookFilter): Promise<Book[]> => {
    const params = new URLSearchParams();
    if (filters?.search) params.append('search', filters.search);
    if (filters?.category) params.append('category', filters.category);
    if (filters?.price_min) params.append('price_min', filters.price_min.toString());
    if (filters?.price_max) params.append('price_max', filters.price_max.toString());

    const response = await axiosInstance.get('/api/books/', { params });
    return response.data.results || response.data;
  },

  getBook: async (bookId: string): Promise<Book> => {
    const response = await axiosInstance.get(`/api/books/${bookId}/`);
    return response.data;
  },

  createBook: async (data: Partial<Book>): Promise<Book> => {
    const response = await axiosInstance.post('/api/books/', data);
    return response.data;
  },

  updateBook: async (bookId: string, data: Partial<Book>): Promise<Book> => {
    const response = await axiosInstance.put(`/api/books/${bookId}/`, data);
    return response.data;
  },

  deleteBook: async (bookId: string): Promise<void> => {
    await axiosInstance.delete(`/api/books/${bookId}/`);
  },

  getRecommendations: async (): Promise<Book[]> => {
    const response = await axiosInstance.get('/api/recommender/recommendations/');
    return response.data.results || response.data;
  },
};
