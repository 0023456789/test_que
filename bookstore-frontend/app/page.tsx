'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { booksAPI } from '@/api/books';
import { Book } from '@/types';
import { LoadingSkeleton, StarRating } from '@/components/common/UI';

export default function HomePage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [recommended, setRecommended] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [booksData, recData] = await Promise.all([
          booksAPI.getBooks(),
          booksAPI.getRecommendations().catch(() => []),
        ]);
        setBooks(booksData.slice(0, 6));
        setRecommended(recData.slice(0, 6));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16 rounded-lg mb-10">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Welcome to Our Bookstore</h1>
          <p className="text-lg mb-6">Discover thousands of books. Built with production-grade microservices.</p>
          <Link href="/products" className="bg-white text-blue-600 px-8 py-3 rounded-lg font-bold hover:bg-gray-100">
            Start Shopping
          </Link>
        </div>
      </section>

      {/* Featured Books */}
      <section className="mb-10">
        <h2 className="text-3xl font-bold mb-6">Featured Books</h2>
        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {books.map((book) => (
              <Link href={`/products/${book.id}`} key={book.id}>
                <div className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer">
                  <div className="bg-gray-200 h-48 rounded mb-4"></div>
                  <h3 className="font-bold text-lg truncate">{book.title}</h3>
                  <p className="text-gray-600 text-sm mb-2">{book.author}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-blue-600">${book.price}</span>
                    <StarRating rating={4} count={12} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Recommended Section */}
      {recommended.length > 0 && (
        <section>
          <h2 className="text-3xl font-bold mb-6">Recommended for You</h2>
          {loading ? (
            <LoadingSkeleton />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {recommended.map((book) => (
                <Link href={`/products/${book.id}`} key={book.id}>
                  <div className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer bg-gradient-to-br from-yellow-50 to-orange-50">
                    <div className="bg-gray-200 h-48 rounded mb-4"></div>
                    <h3 className="font-bold text-lg truncate">{book.title}</h3>
                    <p className="text-gray-600 text-sm mb-2">{book.author}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold text-blue-600">${book.price}</span>
                      <StarRating rating={5} count={28} />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
