import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  InventoryItem,
  RobotModel,
  BuildableResult,
  Order,
  Assembly,
  FilterOptions,
  NotificationMessage,
  UserPreferences,
} from '@/types';

interface AppState {
  // Inventory State
  inventory: Map<string, InventoryItem>;
  inventoryFilter: FilterOptions;
  inventoryLoading: boolean;
  
  // Robot Models State
  robotModels: RobotModel[];
  selectedRobotModel: string | null;
  
  // Assembly State
  buildableResults: Map<string, BuildableResult>;
  assemblies: Assembly[];
  activeAssembly: string | null;
  
  // Orders State
  orders: Order[];
  selectedOrder: string | null;
  draftOrder: Partial<Order> | null;
  
  // UI State
  notifications: NotificationMessage[];
  isOnline: boolean;
  lastSync: Date | null;
  selectedTab: string;
  
  // User Preferences
  preferences: UserPreferences;
  
  // Actions - Inventory
  setInventory: (inventory: Map<string, InventoryItem>) => void;
  updateInventoryItem: (partId: string, quantity: number) => void;
  bulkUpdateInventory: (updates: Array<{ partId: string; quantity: number }>) => void;
  setInventoryFilter: (filter: Partial<FilterOptions>) => void;
  
  // Actions - Robot Models
  setRobotModels: (models: RobotModel[]) => void;
  selectRobotModel: (modelId: string | null) => void;
  
  // Actions - Assembly
  setBuildableResults: (results: Map<string, BuildableResult>) => void;
  updateBuildableResult: (modelId: string, result: BuildableResult) => void;
  addAssembly: (assembly: Assembly) => void;
  updateAssemblyStatus: (assemblyId: string, status: Assembly['status']) => void;
  
  // Actions - Orders
  setOrders: (orders: Order[]) => void;
  addOrder: (order: Order) => void;
  updateOrderStatus: (orderId: string, status: Order['status']) => void;
  selectOrder: (orderId: string | null) => void;
  setDraftOrder: (order: Partial<Order> | null) => void;
  
  // Actions - Notifications
  addNotification: (message: Omit<NotificationMessage, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
  
  // Actions - UI
  setOnlineStatus: (isOnline: boolean) => void;
  setLastSync: (date: Date) => void;
  setSelectedTab: (tab: string) => void;
  
  // Actions - Preferences
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  
  // Computed values
  getLowStockItems: () => InventoryItem[];
  getOutOfStockItems: () => InventoryItem[];
  getTotalInventoryValue: () => number;
  getInventoryStats: () => {
    totalParts: number;
    totalValue: number;
    lowStockCount: number;
    outOfStockCount: number;
  };
}

const defaultPreferences: UserPreferences = {
  theme: 'light',
  language: 'en',
  defaultView: 'grid',
  itemsPerPage: 20,
  showNotifications: true,
  soundEnabled: false,
  hapticEnabled: true,
  autoSave: true,
  compactMode: false,
};

export const useStore = create<AppState>()(
  devtools(
    persist(
      subscribeWithSelector(
        immer((set, get) => ({
          // Initial State
          inventory: new Map(),
          inventoryFilter: {},
          inventoryLoading: false,
          robotModels: [],
          selectedRobotModel: null,
          buildableResults: new Map(),
          assemblies: [],
          activeAssembly: null,
          orders: [],
          selectedOrder: null,
          draftOrder: null,
          notifications: [],
          isOnline: navigator.onLine,
          lastSync: null,
          selectedTab: 'dashboard',
          preferences: defaultPreferences,
          
          // Inventory Actions
          setInventory: (inventory) =>
            set((state) => {
              state.inventory = inventory;
              state.inventoryLoading = false;
            }),
          
          updateInventoryItem: (partId, quantity) =>
            set((state) => {
              const item = state.inventory.get(partId);
              if (item) {
                item.quantity = quantity;
                item.lastUpdated = new Date();
                state.inventory.set(partId, item);
              }
            }),
          
          bulkUpdateInventory: (updates) =>
            set((state) => {
              updates.forEach(({ partId, quantity }) => {
                const item = state.inventory.get(partId);
                if (item) {
                  item.quantity = quantity;
                  item.lastUpdated = new Date();
                  state.inventory.set(partId, item);
                }
              });
            }),
          
          setInventoryFilter: (filter) =>
            set((state) => {
              state.inventoryFilter = { ...state.inventoryFilter, ...filter };
            }),
          
          // Robot Model Actions
          setRobotModels: (models) =>
            set((state) => {
              state.robotModels = models;
            }),
          
          selectRobotModel: (modelId) =>
            set((state) => {
              state.selectedRobotModel = modelId;
            }),
          
          // Assembly Actions
          setBuildableResults: (results) =>
            set((state) => {
              state.buildableResults = results;
            }),
          
          updateBuildableResult: (modelId, result) =>
            set((state) => {
              state.buildableResults.set(modelId, result);
            }),
          
          addAssembly: (assembly) =>
            set((state) => {
              state.assemblies.push(assembly);
            }),
          
          updateAssemblyStatus: (assemblyId, status) =>
            set((state) => {
              const assembly = state.assemblies.find((a) => a.id === assemblyId);
              if (assembly) {
                assembly.status = status;
                if (status === 'completed') {
                  assembly.completionDate = new Date();
                }
              }
            }),
          
          // Order Actions
          setOrders: (orders) =>
            set((state) => {
              state.orders = orders;
            }),
          
          addOrder: (order) =>
            set((state) => {
              state.orders.push(order);
            }),
          
          updateOrderStatus: (orderId, status) =>
            set((state) => {
              const order = state.orders.find((o) => o.id === orderId);
              if (order) {
                order.status = status;
              }
            }),
          
          selectOrder: (orderId) =>
            set((state) => {
              state.selectedOrder = orderId;
            }),
          
          setDraftOrder: (order) =>
            set((state) => {
              state.draftOrder = order;
            }),
          
          // Notification Actions
          addNotification: (message) =>
            set((state) => {
              const notification: NotificationMessage = {
                ...message,
                id: `notification-${Date.now()}-${Math.random()}`,
                timestamp: new Date(),
              };
              state.notifications.push(notification);
              
              // Auto-remove after duration
              if (message.duration) {
                setTimeout(() => {
                  get().removeNotification(notification.id);
                }, message.duration);
              }
            }),
          
          removeNotification: (id) =>
            set((state) => {
              state.notifications = state.notifications.filter((n) => n.id !== id);
            }),
          
          clearNotifications: () =>
            set((state) => {
              state.notifications = [];
            }),
          
          // UI Actions
          setOnlineStatus: (isOnline) =>
            set((state) => {
              state.isOnline = isOnline;
            }),
          
          setLastSync: (date) =>
            set((state) => {
              state.lastSync = date;
            }),
          
          setSelectedTab: (tab) =>
            set((state) => {
              state.selectedTab = tab;
            }),
          
          // Preference Actions
          updatePreferences: (preferences) =>
            set((state) => {
              state.preferences = { ...state.preferences, ...preferences };
            }),
          
          // Computed Values
          getLowStockItems: () => {
            const inventory = get().inventory;
            return Array.from(inventory.values()).filter(
              (item) => item.quantity <= item.reorderPoint && item.quantity > 0
            );
          },
          
          getOutOfStockItems: () => {
            const inventory = get().inventory;
            return Array.from(inventory.values()).filter((item) => item.quantity === 0);
          },
          
          getTotalInventoryValue: () => {
            const inventory = get().inventory;
            return Array.from(inventory.values()).reduce(
              (total, item) => total + item.quantity * item.part.unitCost,
              0
            );
          },
          
          getInventoryStats: () => {
            const inventory = get().inventory;
            const items = Array.from(inventory.values());
            
            return {
              totalParts: items.length,
              totalValue: items.reduce(
                (total, item) => total + item.quantity * item.part.unitCost,
                0
              ),
              lowStockCount: items.filter(
                (item) => item.quantity <= item.reorderPoint && item.quantity > 0
              ).length,
              outOfStockCount: items.filter((item) => item.quantity === 0).length,
            };
          },
        }))
      ),
      {
        name: 'bom-calculator-store',
        partialize: (state) => ({
          preferences: state.preferences,
          selectedTab: state.selectedTab,
          inventoryFilter: state.inventoryFilter,
        }),
      }
    ),
    {
      name: 'BOM Calculator Store',
    }
  )
);

// Selectors for common use cases
export const useInventory = () => useStore((state) => state.inventory);
export const useRobotModels = () => useStore((state) => state.robotModels);
export const useBuildableResults = () => useStore((state) => state.buildableResults);
export const useOrders = () => useStore((state) => state.orders);
export const useNotifications = () => useStore((state) => state.notifications);
export const usePreferences = () => useStore((state) => state.preferences);

// Subscribe to online/offline events
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    useStore.getState().setOnlineStatus(true);
    useStore.getState().addNotification({
      message: 'Connection restored',
      type: 'success',
      duration: 3000,
    });
  });
  
  window.addEventListener('offline', () => {
    useStore.getState().setOnlineStatus(false);
    useStore.getState().addNotification({
      message: 'Connection lost. Working offline.',
      type: 'warning',
      duration: 5000,
    });
  });
}