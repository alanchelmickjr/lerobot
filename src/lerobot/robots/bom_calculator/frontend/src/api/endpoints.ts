import apiClient from './client';
import {
  InventoryItem,
  RobotModel,
  BuildableResult,
  Order,
  Assembly,
  Part,
  OrderGenerationParams,
  BulkUpdateResult,
  PaginatedResponse,
  ApiResponse,
} from '@/types';

// Inventory API
export const inventoryAPI = {
  // Get all inventory items
  getAll: async (params?: { 
    category?: string; 
    search?: string; 
    lowStock?: boolean 
  }): Promise<InventoryItem[]> => {
    const response = await apiClient.get<InventoryItem[]>('/inventory', { params });
    return response.data || [];
  },

  // Get single inventory item
  getById: async (partId: string): Promise<InventoryItem> => {
    const response = await apiClient.get<InventoryItem>(`/inventory/${partId}`);
    return response.data!;
  },

  // Update inventory quantity
  updateQuantity: async (partId: string, quantity: number): Promise<InventoryItem> => {
    const response = await apiClient.put<InventoryItem>(`/inventory/${partId}`, { quantity });
    return response.data!;
  },

  // Bulk update inventory
  bulkUpdate: async (updates: Array<{ partId: string; quantity: number }>): Promise<BulkUpdateResult> => {
    const response = await apiClient.post<BulkUpdateResult>('/inventory/bulk-update', { updates });
    return response.data!;
  },

  // Add new inventory item
  create: async (item: Omit<InventoryItem, 'lastUpdated'>): Promise<InventoryItem> => {
    const response = await apiClient.post<InventoryItem>('/inventory', item);
    return response.data!;
  },

  // Delete inventory item
  delete: async (partId: string): Promise<void> => {
    await apiClient.delete(`/inventory/${partId}`);
  },

  // Get inventory history
  getHistory: async (partId: string, days: number = 30): Promise<any[]> => {
    const response = await apiClient.get<any[]>(`/inventory/${partId}/history`, {
      params: { days },
    });
    return response.data || [];
  },

  // Export inventory
  export: async (format: 'csv' | 'excel' | 'pdf' = 'csv'): Promise<Blob> => {
    const response = await apiClient.get(`/inventory/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data as any;
  },
};

// Parts API
export const partsAPI = {
  // Get all parts
  getAll: async (params?: { category?: string; search?: string }): Promise<Part[]> => {
    const response = await apiClient.get<Part[]>('/parts', { params });
    return response.data || [];
  },

  // Get single part
  getById: async (partId: string): Promise<Part> => {
    const response = await apiClient.get<Part>(`/parts/${partId}`);
    return response.data!;
  },

  // Create new part
  create: async (part: Omit<Part, 'id'>): Promise<Part> => {
    const response = await apiClient.post<Part>('/parts', part);
    return response.data!;
  },

  // Update part
  update: async (partId: string, part: Partial<Part>): Promise<Part> => {
    const response = await apiClient.put<Part>(`/parts/${partId}`, part);
    return response.data!;
  },

  // Delete part
  delete: async (partId: string): Promise<void> => {
    await apiClient.delete(`/parts/${partId}`);
  },
};

// Robot Models API
export const robotModelsAPI = {
  // Get all robot models
  getAll: async (): Promise<RobotModel[]> => {
    const response = await apiClient.get<RobotModel[]>('/robots');
    return response.data || [];
  },

  // Get single robot model
  getById: async (modelId: string): Promise<RobotModel> => {
    const response = await apiClient.get<RobotModel>(`/robots/${modelId}`);
    return response.data!;
  },

  // Create new robot model
  create: async (model: Omit<RobotModel, 'id'>): Promise<RobotModel> => {
    const response = await apiClient.post<RobotModel>('/robots', model);
    return response.data!;
  },

  // Update robot model
  update: async (modelId: string, model: Partial<RobotModel>): Promise<RobotModel> => {
    const response = await apiClient.put<RobotModel>(`/robots/${modelId}`, model);
    return response.data!;
  },

  // Delete robot model
  delete: async (modelId: string): Promise<void> => {
    await apiClient.delete(`/robots/${modelId}`);
  },

  // Get BOM for robot model
  getBOM: async (modelId: string): Promise<any> => {
    const response = await apiClient.get<any>(`/robots/${modelId}/bom`);
    return response.data;
  },

  // Import BOM for robot model
  importBOM: async (modelId: string, bomData: any): Promise<void> => {
    await apiClient.post(`/robots/${modelId}/bom/import`, bomData);
  },
};

// Assembly API
export const assemblyAPI = {
  // Calculate buildable quantity
  calculateBuildable: async (modelId: string): Promise<BuildableResult> => {
    const response = await apiClient.get<BuildableResult>(`/assembly/calculate/${modelId}`);
    return response.data!;
  },

  // Calculate all buildable quantities
  calculateAllBuildable: async (): Promise<Map<string, BuildableResult>> => {
    const response = await apiClient.get<Record<string, BuildableResult>>('/assembly/calculate');
    return new Map(Object.entries(response.data || {}));
  },

  // Get all assemblies
  getAll: async (params?: { 
    status?: Assembly['status']; 
    robotModelId?: string 
  }): Promise<Assembly[]> => {
    const response = await apiClient.get<Assembly[]>('/assembly', { params });
    return response.data || [];
  },

  // Get single assembly
  getById: async (assemblyId: string): Promise<Assembly> => {
    const response = await apiClient.get<Assembly>(`/assembly/${assemblyId}`);
    return response.data!;
  },

  // Create new assembly
  create: async (assembly: {
    robotModelId: string;
    quantity: number;
    notes?: string;
  }): Promise<Assembly> => {
    const response = await apiClient.post<Assembly>('/assembly', assembly);
    return response.data!;
  },

  // Update assembly status
  updateStatus: async (assemblyId: string, status: Assembly['status']): Promise<Assembly> => {
    const response = await apiClient.patch<Assembly>(`/assembly/${assemblyId}/status`, { status });
    return response.data!;
  },

  // Reserve parts for assembly
  reserveParts: async (assemblyId: string): Promise<void> => {
    await apiClient.post(`/assembly/${assemblyId}/reserve`);
  },

  // Release reserved parts
  releaseParts: async (assemblyId: string): Promise<void> => {
    await apiClient.post(`/assembly/${assemblyId}/release`);
  },

  // Complete assembly
  complete: async (assemblyId: string): Promise<Assembly> => {
    const response = await apiClient.post<Assembly>(`/assembly/${assemblyId}/complete`);
    return response.data!;
  },

  // Cancel assembly
  cancel: async (assemblyId: string): Promise<void> => {
    await apiClient.post(`/assembly/${assemblyId}/cancel`);
  },
};

// Orders API
export const ordersAPI = {
  // Get all orders
  getAll: async (params?: {
    status?: Order['status'];
    startDate?: string;
    endDate?: string;
    page?: number;
    pageSize?: number;
  }): Promise<PaginatedResponse<Order>> => {
    const response = await apiClient.get<PaginatedResponse<Order>>('/orders', { params });
    return response.data!;
  },

  // Get single order
  getById: async (orderId: string): Promise<Order> => {
    const response = await apiClient.get<Order>(`/orders/${orderId}`);
    return response.data!;
  },

  // Generate order sheet
  generate: async (params: OrderGenerationParams): Promise<Order> => {
    const response = await apiClient.post<Order>('/orders/generate', params);
    return response.data!;
  },

  // Create order
  create: async (order: Omit<Order, 'id' | 'date'>): Promise<Order> => {
    const response = await apiClient.post<Order>('/orders', order);
    return response.data!;
  },

  // Update order
  update: async (orderId: string, order: Partial<Order>): Promise<Order> => {
    const response = await apiClient.put<Order>(`/orders/${orderId}`, order);
    return response.data!;
  },

  // Update order status
  updateStatus: async (orderId: string, status: Order['status']): Promise<Order> => {
    const response = await apiClient.patch<Order>(`/orders/${orderId}/status`, { status });
    return response.data!;
  },

  // Delete order
  delete: async (orderId: string): Promise<void> => {
    await apiClient.delete(`/orders/${orderId}`);
  },

  // Export order
  export: async (orderId: string, format: 'csv' | 'excel' | 'pdf' = 'pdf'): Promise<Blob> => {
    const response = await apiClient.get(`/orders/${orderId}/export`, {
      params: { format },
      responseType: 'blob',
    });
    return response.data as any;
  },

  // Export all orders
  exportAll: async (format: 'csv' | 'excel' = 'csv'): Promise<Blob> => {
    const response = await apiClient.get('/orders/export', {
      params: { format },
      responseType: 'blob',
    });
    return response.data as any;
  },

  // Submit order to supplier
  submit: async (orderId: string): Promise<Order> => {
    const response = await apiClient.post<Order>(`/orders/${orderId}/submit`);
    return response.data!;
  },

  // Duplicate order
  duplicate: async (orderId: string): Promise<Order> => {
    const response = await apiClient.post<Order>(`/orders/${orderId}/duplicate`);
    return response.data!;
  },
};

// Dashboard API
export const dashboardAPI = {
  // Get dashboard stats
  getStats: async (): Promise<{
    totalParts: number;
    totalValue: number;
    lowStockCount: number;
    outOfStockCount: number;
    pendingOrders: number;
    activeAssemblies: number;
    robotModels: number;
    recentActivity: any[];
  }> => {
    const response = await apiClient.get('/dashboard/stats');
    return response.data as any;
  },

  // Get inventory trends
  getInventoryTrends: async (days: number = 30): Promise<any> => {
    const response = await apiClient.get('/dashboard/inventory-trends', {
      params: { days },
    });
    return response.data;
  },

  // Get assembly metrics
  getAssemblyMetrics: async (): Promise<any> => {
    const response = await apiClient.get('/dashboard/assembly-metrics');
    return response.data;
  },

  // Get order history
  getOrderHistory: async (days: number = 30): Promise<any> => {
    const response = await apiClient.get('/dashboard/order-history', {
      params: { days },
    });
    return response.data;
  },
};

// Settings API
export const settingsAPI = {
  // Get all settings
  getAll: async (): Promise<Record<string, any>> => {
    const response = await apiClient.get<Record<string, any>>('/settings');
    return response.data || {};
  },

  // Update settings
  update: async (settings: Record<string, any>): Promise<void> => {
    await apiClient.put('/settings', settings);
  },

  // Reset to defaults
  reset: async (): Promise<void> => {
    await apiClient.post('/settings/reset');
  },

  // Export configuration
  exportConfig: async (): Promise<Blob> => {
    const response = await apiClient.get('/settings/export', {
      responseType: 'blob',
    });
    return response.data as any;
  },

  // Import configuration
  importConfig: async (config: File): Promise<void> => {
    const formData = new FormData();
    formData.append('config', config);
    
    await apiClient.post('/settings/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Auth API (if needed)
export const authAPI = {
  // Login
  login: async (credentials: { username: string; password: string }): Promise<{
    access_token: string;
    refresh_token: string;
    user: any;
  }> => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data as any;
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },

  // Refresh token
  refresh: async (refreshToken: string): Promise<{
    access_token: string;
    refresh_token?: string;
  }> => {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data as any;
  },

  // Get current user
  getCurrentUser: async (): Promise<any> => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },
};