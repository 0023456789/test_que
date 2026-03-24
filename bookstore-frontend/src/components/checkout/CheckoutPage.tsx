'use client';

import React, { useState } from 'react';
import { useCart } from '@/hooks';
import { useAuth } from '@/hooks';
import { ordersAPI } from '@/api/orders';
import { booksAPI } from '@/api/books';
import Link from 'next/link';
import { ErrorMessage, LoadingSpinner } from '@/components/common/UI';
import { Book, Address } from '@/types';

export interface CheckoutPageProps {
  onOrderCreated?: (orderId: string) => void;
}

export default function CheckoutPage({ onOrderCreated }: CheckoutPageProps) {
  const { items, totalPrice } = useCart();
  const { user, isAuthenticated } = useAuth();

  const [books, setBooks] = useState<Map<string, Book>>(new Map());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'cart' | 'shipping' | 'review' | 'processing'>(
    items.length > 0 ? 'cart' : 'shipping'
  );

  const [address, setAddress] = useState<Address>({
    street: '',
    city: '',
    state: '',
    postal_code: '',
    country: '',
  });

  React.useEffect(() => {
    loadBooks();
  }, []);

  const loadBooks = async () => {
    try {
      const allBooks = await booksAPI.getBooks();
      const booksMap = new Map(allBooks.map((b) => [b.id, b]));
      setBooks(booksMap);
    } catch (err: any) {
      console.error('Error loading books:', err);
    }
  };

  const handleAddressChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setAddress({ ...address, [name]: value });
  };

  const handleCreateOrder = async () => {
    if (!user) {
      setError('You must be logged in to create an order');
      return;
    }

    if (!address.street || !address.city || !address.postal_code) {
      setError('Please fill in all address fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      setStep('processing');

      const orderPayload = {
        items: items.map((item) => ({
          book_id: item.book_id,
          quantity: item.quantity,
        })),
        shipping_address: address,
      };

      const order = await ordersAPI.createOrder(orderPayload);
      onOrderCreated?.(order.id);

      // Redirect to order details after 2 seconds
      setTimeout(() => {
        window.location.href = `/orders/${order.id}`;
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to create order');
      setStep('review');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <p className="text-lg mb-4">Please log in to proceed with checkout</p>
        <Link
          href="/auth/login"
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Go to Login
        </Link>
      </div>
    );
  }

  if (items.length === 0 && step === 'cart') {
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
    <div className="max-w-4xl mx-auto">
      {/* Step Indicator */}
      <div className="mb-8 flex justify-between">
        {['cart', 'shipping', 'review', 'processing'].map((s) => (
          <div
            key={s}
            className={`flex-1 py-2 px-4 text-center border-b-2 ${
              step === s
                ? 'border-blue-600 text-blue-600 font-bold'
                : step > s
                ? 'border-green-600 text-green-600'
                : 'border-gray-300 text-gray-400'
            }`}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </div>
        ))}
      </div>

      {error && <ErrorMessage message={error} />}

      {loading && step === 'processing' && (
        <div className="text-center">
          <LoadingSpinner />
          <p className="text-lg font-semibold mt-4">Processing your order...</p>
        </div>
      )}

      {!loading && (
        <>
          {/* Cart Review */}
          {step === 'cart' && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold mb-6">Order Summary</h2>
              <div className="space-y-4">
                {items.map((item) => {
                  const book = books.get(item.book_id);
                  return (
                    <div
                      key={item.book_id}
                      className="flex justify-between items-center border-b pb-4"
                    >
                      <div>
                        <p className="font-semibold">{book?.title || 'Loading...'}</p>
                        <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">${((book?.price || 0) * item.quantity).toFixed(2)}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="mt-6 border-t pt-4 flex justify-between items-center">
                <span className="text-lg font-bold">Total:</span>
                <span className="text-2xl font-bold text-blue-600">
                  ${totalPrice.toFixed(2)}
                </span>
              </div>
              <button
                onClick={() => setStep('shipping')}
                className="w-full mt-6 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-semibold"
              >
                Continue to Shipping
              </button>
            </div>
          )}

          {/* Shipping Address */}
          {step === 'shipping' && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold mb-6">Shipping Address</h2>
              <div className="space-y-4">
                <input
                  type="text"
                  name="street"
                  placeholder="Street Address"
                  value={address.street}
                  onChange={handleAddressChange}
                  className="w-full border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    name="city"
                    placeholder="City"
                    value={address.city}
                    onChange={handleAddressChange}
                    className="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    name="state"
                    placeholder="State"
                    value={address.state}
                    onChange={handleAddressChange}
                    className="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    name="postal_code"
                    placeholder="Postal Code"
                    value={address.postal_code}
                    onChange={handleAddressChange}
                    className="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="text"
                    name="country"
                    placeholder="Country"
                    value={address.country}
                    onChange={handleAddressChange}
                    className="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => setStep('cart')}
                  className="flex-1 bg-gray-300 text-gray-800 py-2 rounded hover:bg-gray-400 font-semibold"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep('review')}
                  className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-semibold"
                >
                  Review Order
                </button>
              </div>
            </div>
          )}

          {/* Order Review */}
          {step === 'review' && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-2xl font-bold mb-6">Review Your Order</h2>

              <div className="space-y-6">
                <div>
                  <h3 className="font-bold mb-4">Items</h3>
                  <div className="space-y-2">
                    {items.map((item) => {
                      const book = books.get(item.book_id);
                      return (
                        <div key={item.book_id} className="flex justify-between text-sm">
                          <span>{book?.title} x {item.quantity}</span>
                          <span>${((book?.price || 0) * item.quantity).toFixed(2)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <h3 className="font-bold mb-4">Shipping Address</h3>
                  <p className="text-sm">{address.street}</p>
                  <p className="text-sm">{address.city}, {address.state} {address.postal_code}</p>
                  <p className="text-sm">{address.country}</p>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between font-bold">
                    <span>Total:</span>
                    <span className="text-lg text-blue-600">${totalPrice.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => setStep('shipping')}
                  className="flex-1 bg-gray-300 text-gray-800 py-2 rounded hover:bg-gray-400 font-semibold"
                >
                  Back
                </button>
                <button
                  onClick={handleCreateOrder}
                  disabled={loading}
                  className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700 font-semibold disabled:opacity-50"
                >
                  Place Order
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
