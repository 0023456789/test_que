'use client';

import React, { useEffect, useState } from 'react';
import { useCart } from '@/hooks';
import { booksAPI } from '@/api/books';
import Link from 'next/link';
import { Book } from '@/types';
import { X } from 'lucide-react';
import { removeFromCart } from '@/store/cartSlice';
import { useDispatch } from 'react-redux';

export default function CartPage() {
  const dispatch = useDispatch();
  const { items, totalPrice } = useCart();
  const [books, setBooks] = useState<Map<string, Book>>(new Map());

  useEffect(() => {
    const loadBooks = async () => {
      try {
        const allBooks = await booksAPI.getBooks();
        const booksMap = new Map(allBooks.map((b) => [b.id, b]));
        setBooks(booksMap);
      } catch (err) {
        console.error('Error loading books:', err);
      }
    };
    loadBooks();
  }, []);

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg mb-4">Your cart is empty</p>
        <Link
          href="/products"
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Continue Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-6">Shopping Cart</h2>
          <div className="space-y-4">
            {items.map((item) => {
              const book = books.get(item.book_id);
              return (
                <div key={item.book_id} className="flex justify-between items-center border-b pb-4">
                  <div className="flex-1">
                    <Link href={`/products/${item.book_id}`}>
                      <p className="font-semibold hover:text-blue-600">{book?.title || 'Loading...'}</p>
                    </Link>
                    <p className="text-sm text-gray-600">{book?.author}</p>
                    <p className="text-lg font-bold text-blue-600 mt-2">${book?.price}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-lg font-semibold">Qty: {item.quantity}</span>
                    <button
                      onClick={() => dispatch(removeFromCart(item.book_id))}
                      className="text-red-600 hover:text-red-800"
                    >
                      <X size={20} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md h-fit">
        <h3 className="text-lg font-bold mb-4">Order Summary</h3>
        <div className="space-y-2 mb-4">
          <div className="flex justify-between">
            <span>Subtotal:</span>
            <span>${totalPrice.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span>Shipping:</span>
            <span>FREE</span>
          </div>
          <div className="border-t pt-2 flex justify-between font-bold text-lg">
            <span>Total:</span>
            <span className="text-blue-600">${totalPrice.toFixed(2)}</span>
          </div>
        </div>

        <Link
          href="/checkout"
          className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700 font-semibold block text-center"
        >
          Proceed to Checkout
        </Link>

        <Link
          href="/products"
          className="w-full border border-blue-600 text-blue-600 py-3 rounded hover:bg-blue-50 font-semibold block text-center mt-2"
        >
          Continue Shopping
        </Link>
      </div>
    </div>
  );
}
