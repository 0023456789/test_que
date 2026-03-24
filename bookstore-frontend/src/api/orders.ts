import axiosInstance from '@/lib/axios';
import { Order, OrderStatus, Address, SagaState } from '@/types';

export interface CreateOrderPayload {
  items: Array<{ book_id: string; quantity: number }>;
  shipping_address: Address;
}

export const ordersAPI = {
  createOrder: async (payload: CreateOrderPayload): Promise<Order> => {
    const response = await axiosInstance.post('/api/orders/', payload);
    return response.data;
  },

  getOrders: async (): Promise<Order[]> => {
    const response = await axiosInstance.get('/api/orders/');
    return response.data.results || response.data;
  },

  getOrder: async (orderId: string): Promise<Order> => {
    const response = await axiosInstance.get(`/api/orders/${orderId}/`);
    return response.data;
  },

  getOrderStatus: async (orderId: string): Promise<{ status: OrderStatus; saga_state: SagaState }> => {
    const response = await axiosInstance.get(`/api/orders/${orderId}/status/`);
    return response.data;
  },

  cancelOrder: async (orderId: string): Promise<void> => {
    await axiosInstance.post(`/api/orders/${orderId}/cancel/`);
  },
};
