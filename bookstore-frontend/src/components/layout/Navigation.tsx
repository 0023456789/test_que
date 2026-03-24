'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks';
import { ShoppingCart, User, LogOut, Menu } from 'lucide-react';
import { useState } from 'react';

export default function Navigation() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    router.push('/auth/login');
  };

  const isAdmin = user?.role === 'admin' || user?.role === 'manager' || user?.role === 'staff';

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-blue-600">
          Bookstore
        </Link>

        {/* Mobile menu button */}
        <button
          className="md:hidden"
          onClick={() => setIsOpen(!isOpen)}
        >
          <Menu size={24} />
        </button>

        {/* Desktop menu */}
        <div className="hidden md:flex gap-6 items-center">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <Link href="/products" className="hover:text-blue-600">
            Catalog
          </Link>

          {isAuthenticated ? (
            <>
              <Link href="/cart" className="hover:text-blue-600 flex items-center gap-2">
                <ShoppingCart size={20} />
                Cart
              </Link>
              <Link href="/orders" className="hover:text-blue-600">
                My Orders
              </Link>

              {isAdmin && (
                <Link href="/dashboard" className="hover:text-blue-600 text-orange-600 font-semibold">
                  Dashboard
                </Link>
              )}

              <div className="flex items-center gap-2">
                <User size={20} />
                <span className="text-sm">{user?.first_name || user?.email}</span>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center gap-2 bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
              >
                <LogOut size={20} />
                Logout
              </button>
            </>
          ) : (
            <>
              <Link
                href="/auth/login"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Login
              </Link>
              <Link
                href="/auth/register"
                className="border border-blue-600 text-blue-600 px-4 py-2 rounded hover:bg-blue-50"
              >
                Register
              </Link>
            </>
          )}
        </div>

        {/* Mobile menu */}
        {isOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-white shadow-md p-4 flex flex-col gap-4">
            <Link href="/" className="hover:text-blue-600">
              Home
            </Link>
            <Link href="/products" className="hover:text-blue-600">
              Catalog
            </Link>

            {isAuthenticated ? (
              <>
                <Link href="/cart" className="hover:text-blue-600">
                  Cart
                </Link>
                <Link href="/orders" className="hover:text-blue-600">
                  My Orders
                </Link>
                {isAdmin && (
                  <Link href="/dashboard" className="hover:text-blue-600 text-orange-600 font-semibold">
                    Dashboard
                  </Link>
                )}
                <button
                  onClick={handleLogout}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 text-left"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/auth/login" className="bg-blue-600 text-white px-4 py-2 rounded">
                  Login
                </Link>
                <Link href="/auth/register" className="border border-blue-600 text-blue-600 px-4 py-2 rounded">
                  Register
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  );
}
