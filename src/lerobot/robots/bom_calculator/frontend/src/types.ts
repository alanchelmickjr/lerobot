// Part and Inventory Types
export interface Part {
  id: string;
  name: string;
  category: 'actuator' | 'sensor' | 'structural' | 'electronic' | 'cable' | 'fastener' | 'other';
  unitCost: number;
  supplier?: string;
  leadTime?: number;
  description?: string;
  specifications?: Record<string, any>;
  image?: string;
}

export interface InventoryItem {
  partId: string;
  part: Part;
  quantity: number;
  reorderPoint: number;
  reorderQuantity: number;
  location?: string;
  lastUpdated: Date;
  reserved?: number;
}

// Robot Model Types
export interface BOMItem {
  partId: string;
  quantity: number;
  notes?: string;
  optional?: boolean;
}

export interface RobotModel {
  id: string;
  name: string;
  description: string;
  category: 'arm' | 'mobile' | 'humanoid' | 'custom';
  bom: BOMItem[];
  assembly_time?: number;
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  image?: string;
  documentation?: string;
}

// Assembly and Build Types
export interface BuildableResult {
  robotModelId: string;
  maxBuildable: number;
  limitingParts: string[];
  expandedBOM: ExpandedBOMItem[];
  totalCost: number;
  missingParts: MissingPart[];
}

export interface ExpandedBOMItem {
  partId: string;
  partName: string;
  required: number;
  available: number;
  unitCost: number;
  totalCost: number;
  shortage: number;
}

export interface MissingPart {
  partId: string;
  partName: string;
  required: number;
  available: number;
  shortage: number;
}

export interface Assembly {
  id: string;
  robotModelId: string;
  robotModel: RobotModel;
  quantity: number;
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  startDate?: Date;
  completionDate?: Date;
  notes?: string;
  reservedParts: Map<string, number>;
}

// Order Types
export interface OrderItem {
  partId: string;
  partName: string;
  quantity: number;
  unitCost: number;
  totalCost: number;
  supplier?: string;
  leadTime?: number;
}

export interface Order {
  id: string;
  date: Date;
  status: 'draft' | 'submitted' | 'approved' | 'ordered' | 'received';
  items: OrderItem[];
  groupedItems?: Map<string, OrderItem[]>;
  totals: {
    subtotal: number;
    shipping: number;
    tax: number;
    total: number;
  };
  notes?: string;
  robotModelId?: string;
  targetQuantity?: number;
}

export interface OrderGenerationParams {
  modelId: string;
  quantity: number;
  priority: 'standard' | 'rush' | 'economy';
  includeSpares: boolean;
  sparesPercentage?: number;
}

// UI State Types
export interface NotificationMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  duration?: number;
}

export interface FilterOptions {
  category?: string;
  searchTerm?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  showLowStock?: boolean;
  showOutOfStock?: boolean;
}

export interface TabConfig {
  id: string;
  label: string;
  icon?: string;
  badge?: number;
  disabled?: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface BulkUpdateResult {
  successCount: number;
  failureCount: number;
  failures: Array<{
    id: string;
    error: string;
  }>;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'inventory_update' | 'assembly_update' | 'order_update' | 'notification';
  payload: any;
  timestamp: Date;
}

export interface InventoryUpdateMessage {
  partId: string;
  oldQuantity: number;
  newQuantity: number;
  userId?: string;
}

// Touch and Gesture Types
export interface TouchState {
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
  deltaX: number;
  deltaY: number;
  velocity: number;
  direction: 'left' | 'right' | 'up' | 'down' | null;
}

export interface SwipeAction {
  threshold: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}

// Chart Data Types
export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }>;
}

export interface InventoryStats {
  totalParts: number;
  totalValue: number;
  lowStockCount: number;
  outOfStockCount: number;
  categories: Map<string, number>;
}

// Theme Types
export interface ThemeMode {
  mode: 'light' | 'dark';
  primary: string;
  secondary: string;
  background: string;
  surface: string;
  error: string;
  warning: string;
  info: string;
  success: string;
}

// User Preferences
export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  defaultView: 'grid' | 'list';
  itemsPerPage: number;
  showNotifications: boolean;
  soundEnabled: boolean;
  hapticEnabled: boolean;
  autoSave: boolean;
  compactMode: boolean;
}

// Export Types
export interface ExportOptions {
  format: 'csv' | 'excel' | 'pdf' | 'json';
  includeHeaders: boolean;
  dateRange?: {
    start: Date;
    end: Date;
  };
  fields?: string[];
}