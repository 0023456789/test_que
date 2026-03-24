'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { booksAPI } from '@/api/books';
import { reviewsAPI } from '@/api/reviews';
import { Book, ReviewItem } from '@/types';
import { LoadingSpinner, StarRating, ErrorMessage } from '@/components/common/UI';
import { useCart } from '@/hooks';
import { addToCart } from '@/store/cartSlice';
import { useDispatch } from 'react-redux';

export default function ProductPage() {
  const params = useParams();
  const bookId = params.id as string;
  const dispatch = useDispatch();

  const [book, setBook] = useState<Book | null>(null);
  const [reviews, setReviews] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [bookId]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [bookData, reviewsData] = await Promise.all([
        booksAPI.getBook(bookId),
        reviewsAPI.getReviews(bookId).catch(() => []),
      ]);
      setBook(bookData);
      setReviews(reviewsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (book) {
      dispatch(addToCart({ book_id: book.id, quantity, book }));
      alert('Added to cart!');
    }
  };

  const handleSubmitReview = async () => {
    try {
      await reviewsAPI.createReview(bookId, {
        rating: reviewRating,
        comment: reviewComment,
      });
      setReviewComment('');
      setReviewRating(5);
      loadData();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!book) return <ErrorMessage message="Book not found" />;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Product Image & Details */}
      <div className="lg:col-span-1">
        <div className="bg-gray-200 h-80 rounded-lg mb-4"></div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h1 className="text-2xl font-bold mb-2">{book.title}</h1>
          <p className="text-gray-600 mb-2">{book.author}</p>
          <div className="flex items-center gap-2 mb-4">
            <StarRating rating={4} count={42} />
          </div>
          <p className="text-4xl font-bold text-blue-600 mb-4">${book.price}</p>

          {error && <ErrorMessage message={error} />}

          {book.stock_quantity > 0 ? (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Quantity</label>
                <input
                  type="number"
                  min="1"
                  max={book.stock_quantity}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-full border border-gray-300 rounded px-4 py-2"
                />
              </div>
              <button
                onClick={handleAddToCart}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-bold mb-4"
              >
                Add to Cart
              </button>
            </>
          ) : (
            <div className="bg-red-100 text-red-800 p-3 rounded mb-4">
              Out of Stock
            </div>
          )}

          <div className="text-sm text-gray-600 space-y-2">
            <p><span className="font-semibold">ISBN:</span> {book.isbn}</p>
            <p><span className="font-semibold">Stock:</span> {book.stock_quantity} available</p>
            <p><span className="font-semibold">Category:</span> {book.category}</p>
          </div>
        </div>
      </div>

      {/* Description & Reviews */}
      <div className="lg:col-span-2 space-y-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Description</h2>
          <p className="text-gray-700">{book.description}</p>
        </div>

        {/* Reviews */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">Customer Reviews ({reviews.length})</h2>

          {/* Add Review Form */}
          <div className="mb-6 pb-6 border-b">
            <h3 className="font-bold mb-3">Leave a Review</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">Rating</label>
                <StarRating rating={reviewRating} onRate={setReviewRating} />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Comment</label>
                <textarea
                  value={reviewComment}
                  onChange={(e) => setReviewComment(e.target.value)}
                  rows={3}
                  className="w-full border border-gray-300 rounded px-4 py-2"
                  placeholder="Share your thoughts..."
                />
              </div>
              <button
                onClick={handleSubmitReview}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Submit Review
              </button>
            </div>
          </div>

          {/* Display Reviews */}
          {reviews.length > 0 ? (
            <div className="space-y-4">
              {reviews.map((review) => (
                <div key={review.id} className="border-b pb-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold">{review.author_name}</span>
                    <StarRating rating={review.rating} />
                  </div>
                  <p className="text-gray-700">{review.comment}</p>
                  <p className="text-xs text-gray-500 mt-2">{review.created_at}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600">No reviews yet. Be the first to review!</p>
          )}
        </div>
      </div>
    </div>
  );
}
