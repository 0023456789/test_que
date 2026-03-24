'use client';

import React, { useEffect, useState } from 'react';
import { SagaState, Order } from '@/types';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';

interface SagaTrackerProps {
  order?: Order;
  sagaState?: SagaState;
  loading?: boolean;
}

export default function SagaTracker({ order, sagaState, loading }: SagaTrackerProps) {
  const steps = [
    { id: 1, label: 'Order Created', key: 'pending' },
    { id: 2, label: 'Payment Reserved', key: 'payment_reserved' },
    { id: 3, label: 'Payment Confirmed', key: 'payment_confirmed' },
    { id: 4, label: 'Shipping Arranged', key: 'shipping_arranged' },
    { id: 5, label: 'Order Completed', key: 'completed' },
  ];

  const getStepStatus = (stepKey: string) => {
    if (!sagaState && !order) return 'pending';

    const statusSequence = [
      'pending',
      'payment_reserved',
      'payment_confirmed',
      'shipping_arranged',
      'completed',
    ];

    const currentStatus = sagaState?.status || order?.status || 'pending';
    const currentIndex = statusSequence.indexOf(currentStatus as any);
    const stepIndex = statusSequence.indexOf(stepKey as any);

    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return 'active';
    return 'pending';
  };

  const isErrorStatus = sagaState?.status === 'failed';

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold mb-6">Order Processing Status</h3>

      {isErrorStatus && (
        <div className="bg-red-50 border border-red-200 rounded p-4 mb-6 flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" />
          <div>
            <p className="font-semibold text-red-900">Processing Failed</p>
            <p className="text-red-700 text-sm">{sagaState?.error}</p>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {steps.map((step, index) => {
          const status = getStepStatus(step.key);

          return (
            <div key={step.id}>
              <div className="flex items-center gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center">
                  {status === 'completed' ? (
                    <CheckCircle className="w-8 h-8 text-green-500" />
                  ) : status === 'active' ? (
                    <Clock className="w-8 h-8 text-blue-500 animate-spin" />
                  ) : (
                    <div className="w-8 h-8 rounded-full border-2 border-gray-300"></div>
                  )}
                </div>
                <div className="flex-1">
                  <p className={`font-semibold ${status === 'active' ? 'text-blue-600' : status === 'completed' ? 'text-green-600' : 'text-gray-400'}`}>
                    {step.label}
                  </p>
                  {status === 'active' && (
                    <p className="text-sm text-blue-600">In progress...</p>
                  )}
                </div>
              </div>
              {index < steps.length - 1 && (
                <div className={`ml-5 h-8 border-l-2 ${status === 'completed' ? 'border-green-500' : 'border-gray-300'}`}></div>
              )}
            </div>
          );
        })}
      </div>

      {loading && (
        <div className="mt-4 text-center text-sm text-gray-600">
          <div className="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500 mr-2"></div>
          Updating order status...
        </div>
      )}
    </div>
  );
}
