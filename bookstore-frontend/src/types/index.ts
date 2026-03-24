// User & Auth
export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: 'customer' | 'staff' | 'manager' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  password_confirm: string;
  role?: string;
}

// Book & Catalog
export interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  price: number;
  stock_quantity: number;
  description: string;
  image_url?: string;
  category: string;
  created_at: string;
  updated_at: string;
}

export interface BookFilter {
  category?: string;
  search?: string;
  price_min?: number;
  price_max?: number;
}

// Cart
export interface CartItem {
  book_id: string;
  quantity: number;
  book?: Book;
}

export interface Cart {
  id: string;
  customer_id: string;
  items: CartItem[];
  total_price: number;
  created_at: string;
  updated_at: string;
}

// Order & Checkout
export enum OrderStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  PAYMENT_RESERVED = 'payment_reserved',
  PAYMENT_CONFIRMED = 'payment_confirmed',
  SHIPPING_ARRANGED = 'shipping_arranged',
  SHIPPED = 'shipped',
  DELIVERED = 'delivered',
  CANCELLED = 'cancelled',
}

export interface OrderItem {
  id: string;
  book_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  id: string;
  customer_id: string;
  status: OrderStatus;
  total_amount: number;
  items: OrderItem[];
  shipping_address: Address;
  payment_status: string;
  tracking_number?: string;
  created_at: string;
  updated_at: string;
}

export interface Address {
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
}

export interface Payment {
  id: string;
  order_id: string;
  amount: number;
  status: 'reserved' | 'confirmed' | 'failed' | 'refunded';
  transaction_ref: string;
  created_at: string;
}

export interface Shipment {
  id: string;
  order_id: string;
  status: 'pending' | 'arranged' | 'shipped' | 'delivered';
  tracking_number: string;
  carrier: string;
  estimated_delivery: string;
  created_at: string;
}

// Rating & Comments
export interface ReviewItem {
  id: string;
  book_id: string;
  customer_id: string;
  rating: number;
  comment: string;
  created_at: string;
  author_name: string;
}

// Saga Orchestration State
export interface SagaState {
  status: 'processing' | 'payment_reserved' | 'payment_confirmed' | 'shipping_arranged' | 'completed' | 'failed';
  currentStep: number;
  totalSteps: number;
  error?: string;
  message: string;
}
