import axiosInstance from '@/lib/axios';
import { ReviewItem } from '@/types';

export const reviewsAPI = {
  getReviews: async (bookId: string): Promise<ReviewItem[]> => {
    const response = await axiosInstance.get(
      `/api/comments-ratings/book/${bookId}/`
    );
    return response.data.results || response.data;
  },

  createReview: async (
    bookId: string,
    data: { rating: number; comment: string }
  ): Promise<ReviewItem> => {
    const response = await axiosInstance.post(
      `/api/comments-ratings/`,
      {
        book_id: bookId,
        ...data,
      }
    );
    return response.data;
  },
};
