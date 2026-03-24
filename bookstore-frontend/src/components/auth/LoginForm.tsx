'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { authAPI } from '@/api/auth';
import { useDispatch } from 'react-redux';
import { setUser, setError, setLoading } from '@/store/authSlice';
import { ErrorMessage, LoadingSpinner } from '@/components/common/UI';

export default function LoginForm() {
  const router = useRouter();
  const dispatch = useDispatch();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoadingLocal] = useState(false);
  const [error, setErrorLocal] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingLocal(true);
    setErrorLocal(null);

    try {
      const response = await authAPI.login({ email, password });
      dispatch(setUser(response.user));
      router.push('/');
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || err.message || 'Login failed';
      setErrorLocal(errorMsg);
      dispatch(setError(errorMsg));
    } finally {
      setLoadingLocal(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div className="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md mt-10">
      <h1 className="text-2xl font-bold mb-6 text-center">Login</h1>

      {error && <ErrorMessage message={error} />}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 font-semibold"
        >
          Sign In
        </button>
      </form>

      <p className="mt-4 text-center text-gray-600">
        Don't have an account?{' '}
        <Link href="/auth/register" className="text-blue-600 hover:underline">
          Register
        </Link>
      </p>

      {/* Demo Credentials */}
      <div className="mt-6 p-4 bg-blue-50 rounded">
        <p className="text-xs font-semibold text-blue-900 mb-2">Demo Credentials:</p>
        <p className="text-xs text-blue-800">Email: admin@bookstore.com</p>
        <p className="text-xs text-blue-800">Password: Admin123!</p>
      </div>
    </div>
  );
}
