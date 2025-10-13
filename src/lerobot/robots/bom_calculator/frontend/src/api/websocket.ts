import { io, Socket } from 'socket.io-client';
import { useStore } from '@store/useStore';
import { WebSocketMessage, InventoryUpdateMessage } from '@/types';

class WebSocketManager {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isIntentionalDisconnect = false;
  private pingInterval: NodeJS.Timeout | null = null;
  private subscriptions: Map<string, Set<Function>> = new Map();

  constructor() {
    // Auto-connect when online
    if (typeof window !== 'undefined') {
      window.addEventListener('online', () => {
        if (!this.socket?.connected) {
          this.connect();
        }
      });

      window.addEventListener('offline', () => {
        this.disconnect();
      });

      // Connect on page visibility change
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && !this.socket?.connected) {
          this.connect();
        }
      });
    }
  }

  public connect(token?: string): void {
    if (this.socket?.connected) {
      console.log('[WebSocket] Already connected');
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
      auth: token ? { token } : undefined,
      query: {
        clientId: this.generateClientId(),
        timestamp: Date.now(),
      },
    });

    this.setupEventHandlers();
    this.isIntentionalDisconnect = false;
  }

  private setupEventHandlers(): void {
    if (!this.socket) return;

    // Connection events
    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected');
      this.reconnectAttempts = 0;
      
      useStore.getState().addNotification({
        message: 'Real-time updates connected',
        type: 'success',
        duration: 2000,
      });

      // Start ping interval to keep connection alive
      this.startPingInterval();
      
      // Subscribe to channels
      this.subscribeToChannels();
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
      
      this.stopPingInterval();
      
      if (!this.isIntentionalDisconnect) {
        useStore.getState().addNotification({
          message: 'Real-time updates disconnected',
          type: 'warning',
          duration: 3000,
        });
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        useStore.getState().addNotification({
          message: 'Failed to connect to real-time updates',
          type: 'error',
          duration: 5000,
        });
      }
    });

    // Business events
    this.socket.on('inventory_update', (data: InventoryUpdateMessage) => {
      this.handleInventoryUpdate(data);
    });

    this.socket.on('assembly_update', (data: any) => {
      this.handleAssemblyUpdate(data);
    });

    this.socket.on('order_update', (data: any) => {
      this.handleOrderUpdate(data);
    });

    this.socket.on('notification', (data: any) => {
      this.handleNotification(data);
    });

    this.socket.on('bulk_update', (data: any) => {
      this.handleBulkUpdate(data);
    });

    // Ping/Pong for keeping connection alive
    this.socket.on('pong', () => {
      // Connection is alive
      console.log('[WebSocket] Pong received');
    });

    // Error handling
    this.socket.on('error', (error) => {
      console.error('[WebSocket] Error:', error);
      
      useStore.getState().addNotification({
        message: 'WebSocket error occurred',
        type: 'error',
        duration: 3000,
      });
    });
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    
    this.pingInterval = setInterval(() => {
      if (this.socket?.connected) {
        this.socket.emit('ping');
      }
    }, 30000); // Ping every 30 seconds
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private subscribeToChannels(): void {
    if (!this.socket) return;

    // Subscribe to relevant channels based on current state
    const state = useStore.getState();
    
    // Subscribe to inventory updates
    this.socket.emit('subscribe', {
      channel: 'inventory',
      filters: state.inventoryFilter,
    });

    // Subscribe to robot model updates if viewing assembly
    if (state.selectedRobotModel) {
      this.socket.emit('subscribe', {
        channel: 'assembly',
        modelId: state.selectedRobotModel,
      });
    }

    // Subscribe to order updates
    if (state.selectedOrder) {
      this.socket.emit('subscribe', {
        channel: 'order',
        orderId: state.selectedOrder,
      });
    }
  }

  private handleInventoryUpdate(data: InventoryUpdateMessage): void {
    console.log('[WebSocket] Inventory update:', data);
    
    // Update local store
    useStore.getState().updateInventoryItem(data.partId, data.newQuantity);
    
    // Notify subscribers
    this.notifySubscribers('inventory_update', data);
    
    // Show notification if significant change
    if (Math.abs(data.newQuantity - data.oldQuantity) > 10) {
      useStore.getState().addNotification({
        message: `Inventory updated: Part ${data.partId}`,
        type: 'info',
        duration: 3000,
      });
    }
  }

  private handleAssemblyUpdate(data: any): void {
    console.log('[WebSocket] Assembly update:', data);
    
    // Update buildable results if affected
    if (data.modelId) {
      // Trigger recalculation
      this.notifySubscribers('assembly_update', data);
    }
  }

  private handleOrderUpdate(data: any): void {
    console.log('[WebSocket] Order update:', data);
    
    // Update order in store
    if (data.orderId && data.status) {
      useStore.getState().updateOrderStatus(data.orderId, data.status);
    }
    
    this.notifySubscribers('order_update', data);
  }

  private handleNotification(data: any): void {
    console.log('[WebSocket] Notification:', data);
    
    // Show notification to user
    useStore.getState().addNotification({
      message: data.message,
      type: data.type || 'info',
      duration: data.duration || 4000,
    });
  }

  private handleBulkUpdate(data: any): void {
    console.log('[WebSocket] Bulk update:', data);
    
    // Handle bulk inventory updates
    if (data.updates && Array.isArray(data.updates)) {
      useStore.getState().bulkUpdateInventory(data.updates);
    }
    
    this.notifySubscribers('bulk_update', data);
  }

  // Public methods for managing subscriptions
  public subscribe(event: string, callback: Function): () => void {
    if (!this.subscriptions.has(event)) {
      this.subscriptions.set(event, new Set());
    }
    
    this.subscriptions.get(event)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      this.subscriptions.get(event)?.delete(callback);
    };
  }

  private notifySubscribers(event: string, data: any): void {
    const subscribers = this.subscriptions.get(event);
    if (subscribers) {
      subscribers.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`[WebSocket] Error in subscriber callback for ${event}:`, error);
        }
      });
    }
  }

  // Public methods for sending messages
  public emit(event: string, data: any): void {
    if (!this.socket?.connected) {
      console.warn('[WebSocket] Cannot emit, not connected');
      return;
    }
    
    this.socket.emit(event, data);
  }

  public updateInventory(partId: string, quantity: number): void {
    this.emit('inventory_update', {
      partId,
      quantity,
      timestamp: Date.now(),
    });
  }

  public startAssembly(assemblyId: string): void {
    this.emit('assembly_start', {
      assemblyId,
      timestamp: Date.now(),
    });
  }

  public completeAssembly(assemblyId: string): void {
    this.emit('assembly_complete', {
      assemblyId,
      timestamp: Date.now(),
    });
  }

  public updateOrderStatus(orderId: string, status: string): void {
    this.emit('order_status_update', {
      orderId,
      status,
      timestamp: Date.now(),
    });
  }

  // Utility methods
  private generateClientId(): string {
    const stored = localStorage.getItem('ws_client_id');
    if (stored) return stored;
    
    const id = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('ws_client_id', id);
    return id;
  }

  public disconnect(): void {
    this.isIntentionalDisconnect = true;
    this.stopPingInterval();
    
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  public isConnected(): boolean {
    return this.socket?.connected || false;
  }

  public getSocket(): Socket | null {
    return this.socket;
  }

  // Room management
  public joinRoom(room: string): void {
    if (this.socket?.connected) {
      this.socket.emit('join_room', room);
    }
  }

  public leaveRoom(room: string): void {
    if (this.socket?.connected) {
      this.socket.emit('leave_room', room);
    }
  }

  // Broadcast to room
  public broadcast(room: string, event: string, data: any): void {
    if (this.socket?.connected) {
      this.socket.emit('broadcast', {
        room,
        event,
        data,
      });
    }
  }
}

// Create singleton instance
const wsManager = new WebSocketManager();

// Export functions for easy use
export const initializeWebSocket = (token?: string) => {
  wsManager.connect(token);
};

export const disconnectWebSocket = () => {
  wsManager.disconnect();
};

export const subscribeToWebSocket = (event: string, callback: Function) => {
  return wsManager.subscribe(event, callback);
};

export const emitWebSocketMessage = (event: string, data: any) => {
  wsManager.emit(event, data);
};

export const isWebSocketConnected = () => {
  return wsManager.isConnected();
};

export default wsManager;