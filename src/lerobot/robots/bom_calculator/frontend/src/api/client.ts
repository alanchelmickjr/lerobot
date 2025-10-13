import axios, { AxiosInstance, AxiosRequestConfig, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { ApiResponse } from '@/types';
import { useStore } from '@store/useStore';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const API_TIMEOUT = 30000; // 30 seconds

// Request queue for offline support
interface QueuedRequest {
  id: string;
  config: AxiosRequestConfig;
  timestamp: number;
  retries: number;
}

class APIClient {
  private client: AxiosInstance;
  private requestQueue: QueuedRequest[] = [];
  private isOnline: boolean = navigator.onLine;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: API_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.setupOfflineHandling();
    this.loadQueueFromStorage();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Add auth token if available
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        // Add request ID for tracking
        config.headers['X-Request-ID'] = this.generateRequestId();

        // Log request in development
        if (import.meta.env.DEV) {
          console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }

        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // Log response in development
        if (import.meta.env.DEV) {
          console.log(`[API] Response:`, response.data);
        }

        // Update last sync time
        useStore.getState().setLastSync(new Date());

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Handle network errors
        if (!error.response) {
          if (!this.isOnline) {
            // Queue request for later
            this.queueRequest(originalRequest);
            return Promise.resolve({
              data: {
                success: false,
                queued: true,
                message: 'Request queued for when connection is restored',
              },
            });
          }
        }

        // Handle 401 Unauthorized
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await this.refreshToken();
            return this.client(originalRequest);
          } catch (refreshError) {
            // Redirect to login or handle auth failure
            this.handleAuthFailure();
            return Promise.reject(refreshError);
          }
        }

        // Handle 429 Too Many Requests
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          const delay = retryAfter ? parseInt(retryAfter) * 1000 : 5000;
          
          await this.delay(delay);
          return this.client(originalRequest);
        }

        // Handle 5xx Server Errors with retry
        if (error.response?.status && error.response.status >= 500) {
          if (!originalRequest._retry) {
            originalRequest._retry = true;
            await this.delay(2000); // Wait 2 seconds before retry
            return this.client(originalRequest);
          }
        }

        // Show error notification
        const message = error.response?.data?.message || error.message || 'An error occurred';
        useStore.getState().addNotification({
          message,
          type: 'error',
          duration: 5000,
        });

        return Promise.reject(error);
      }
    );
  }

  private setupOfflineHandling() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
    });
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private queueRequest(config: AxiosRequestConfig) {
    const queuedRequest: QueuedRequest = {
      id: this.generateRequestId(),
      config,
      timestamp: Date.now(),
      retries: 0,
    };

    this.requestQueue.push(queuedRequest);
    this.saveQueueToStorage();

    useStore.getState().addNotification({
      message: 'Request saved for when you\'re back online',
      type: 'info',
      duration: 3000,
    });
  }

  private async processQueue() {
    if (this.requestQueue.length === 0) return;

    useStore.getState().addNotification({
      message: `Processing ${this.requestQueue.length} queued requests...`,
      type: 'info',
      duration: 3000,
    });

    const queue = [...this.requestQueue];
    this.requestQueue = [];

    for (const request of queue) {
      try {
        await this.client(request.config);
      } catch (error) {
        if (request.retries < 3) {
          request.retries++;
          this.requestQueue.push(request);
        } else {
          console.error('Failed to process queued request after 3 retries:', error);
        }
      }
    }

    this.saveQueueToStorage();

    if (this.requestQueue.length === 0) {
      useStore.getState().addNotification({
        message: 'All queued requests processed successfully!',
        type: 'success',
        duration: 3000,
      });
    }
  }

  private saveQueueToStorage() {
    try {
      localStorage.setItem('api_request_queue', JSON.stringify(this.requestQueue));
    } catch (error) {
      console.error('Failed to save request queue to storage:', error);
    }
  }

  private loadQueueFromStorage() {
    try {
      const stored = localStorage.getItem('api_request_queue');
      if (stored) {
        this.requestQueue = JSON.parse(stored);
        if (this.isOnline && this.requestQueue.length > 0) {
          setTimeout(() => this.processQueue(), 1000);
        }
      }
    } catch (error) {
      console.error('Failed to load request queue from storage:', error);
    }
  }

  private async refreshToken(): Promise<void> {
    // Implement token refresh logic
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: refreshToken,
    });

    this.authToken = response.data.access_token;
    localStorage.setItem('access_token', this.authToken);
    
    if (response.data.refresh_token) {
      localStorage.setItem('refresh_token', response.data.refresh_token);
    }
  }

  private handleAuthFailure() {
    // Clear auth data
    this.authToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');

    // Redirect to login or show auth modal
    window.location.href = '/login';
  }

  // Public methods
  public setAuthToken(token: string) {
    this.authToken = token;
    localStorage.setItem('access_token', token);
  }

  public clearAuthToken() {
    this.authToken = null;
    localStorage.removeItem('access_token');
  }

  // HTTP Methods
  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.get<ApiResponse<T>>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.post<ApiResponse<T>>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.put<ApiResponse<T>>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.patch<ApiResponse<T>>(url, data, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.client.delete<ApiResponse<T>>(url, config);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.message;
      return new Error(message);
    }
    return error;
  }
}

// Create singleton instance
const apiClient = new APIClient();

export default apiClient;