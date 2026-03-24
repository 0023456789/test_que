import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Cart, CartItem } from '@/types';

interface CartState {
  items: CartItem[];
  totalPrice: number;
  loading: boolean;
  error: string | null;
}

const initialState: CartState = {
  items: [],
  totalPrice: 0,
  loading: false,
  error: null,
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    addToCart: (state, action: PayloadAction<CartItem>) => {
      const existingItem = state.items.find(
        (item) => item.book_id === action.payload.book_id
      );
      if (existingItem) {
        existingItem.quantity += action.payload.quantity;
      } else {
        state.items.push(action.payload);
      }
    },
    removeFromCart: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(
        (item) => item.book_id !== action.payload
      );
    },
    updateCartItem: (
      state,
      action: PayloadAction<{ bookId: string; quantity: number }>
    ) => {
      const item = state.items.find(
        (i) => i.book_id === action.payload.bookId
      );
      if (item) {
        item.quantity = action.payload.quantity;
      }
    },
    clearCart: (state) => {
      state.items = [];
      state.totalPrice = 0;
    },
    setTotalPrice: (state, action: PayloadAction<number>) => {
      state.totalPrice = action.payload;
    },
    hydrateCart: (state, action: PayloadAction<Cart | null>) => {
      if (action.payload) {
        state.items = action.payload.items;
        state.totalPrice = action.payload.total_price;
      }
    },
  },
});

export const {
  addToCart,
  removeFromCart,
  updateCartItem,
  clearCart,
  setTotalPrice,
  hydrateCart,
} = cartSlice.actions;
export default cartSlice.reducer;
