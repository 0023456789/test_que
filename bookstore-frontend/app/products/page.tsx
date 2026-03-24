'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { booksAPI } from '@/api/books';
import { Book } from '@/types';
import { LoadingSkeleton, StarRating } from '@/components/common/UI';

export default function ProductsPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');

  useEffect(() => {
    loadBooks();
  }, [search, selectedCategory]);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const data = await booksAPI.getBooks({
        search: search || undefined,
        category: selectedCategory || undefined,
      });
      setBooks(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Book Catalog</h1>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Search</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by title or author..."
              className="w-full border border-gray-300 rounded px-4 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full border border-gray-300 rounded px-4 py-2"
            >
              <option value="">All Categories</option>
              <option value="fiction">Fiction</option>
              <option value="non-fiction">Non-Fiction</option>
              <option value="children">Children</option>
              <option value="biography">Biography</option>
            </select>
          </div>
        </div>
      </div>

      {/* Books Grid */}
      {loading ? (
        <LoadingSkeleton />
      ) : books.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {books.map((book) => (
            <Link href={`/products/${book.id}`} key={book.id}>
              <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition cursor-pointer overflow-hidden">
                <div className="bg-gray-200 h-40 rounded-t"></div>
                <div className="p-4">
                  <h3 className="font-bold text-sm truncate">{book.title}</h3>
                  <p className="text-gray-600 text-xs mb-2">{book.author}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold text-blue-600">${book.price}</span>
                    <StarRating rating={4} />
                  </div>
                  {book.stock_quantity < 5 && (
                    <p className="text-red-600 text-xs mt-2">Only {book.stock_quantity} left!</p>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <p className="text-gray-600 mb-4">No books found</p>
          <button
            onClick={() => {
              setSearch('');
              setSelectedCategory('');
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
