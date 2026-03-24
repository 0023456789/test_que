'use client';

import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '@/store';

export const useAuth = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { user, isAuthenticated, loading, error } = useSelector(
    (state: RootState) => state.auth
  );

  return { user, isAuthenticated, loading, error, dispatch };
};

export const useCart = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items, totalPrice, loading, error } = useSelector(
    (state: RootState) => state.cart
  );

  return { items, totalPrice, loading, error, dispatch };
};
