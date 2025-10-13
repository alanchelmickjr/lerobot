# BOM Calculator Frontend

A beautiful, modern, tablet-optimized React/TypeScript frontend for the Robot Assembly BOM Calculator application.

## Features

- 📱 **Tablet-Optimized**: Designed for 10-inch tablets (768px - 1366px)
- 🎨 **Material Design 3**: Modern UI with beautiful animations
- 🌓 **Dark/Light Mode**: Automatic theme switching
- 🔄 **Real-time Updates**: WebSocket integration for live data
- 📴 **Offline Support**: Works offline with service worker
- 👆 **Touch-Optimized**: Large touch targets and gesture support
- ♿ **Accessible**: WCAG 2.1 AA compliant
- 🚀 **Fast**: Optimized with Vite and code splitting

## Tech Stack

- **React 18**: UI framework
- **TypeScript**: Type-safe development
- **Material-UI v5**: Component library
- **Zustand**: State management
- **React Query**: Data fetching and caching
- **Socket.io**: Real-time communication
- **Vite**: Build tool
- **PWA**: Progressive Web App support

## Project Structure

```
frontend/
├── src/
│   ├── api/            # API layer
│   │   ├── client.ts   # Axios client with offline support
│   │   ├── endpoints.ts # API endpoint definitions
│   │   └── websocket.ts # WebSocket manager
│   ├── components/     # Reusable components
│   │   ├── Common/     # Shared components
│   │   ├── Dashboard/  # Dashboard components
│   │   ├── Inventory/  # Inventory management
│   │   ├── Assembly/   # Assembly calculator
│   │   └── Orders/     # Order generation
│   ├── pages/          # Page components
│   ├── store/          # State management
│   │   ├── useStore.ts # Main app store
│   │   └── useTheme.ts # Theme management
│   ├── styles/         # Global styles
│   ├── theme/          # Material-UI theme
│   ├── types.ts        # TypeScript types
│   ├── App.tsx         # Main app component
│   └── main.tsx        # Entry point
├── public/             # Static assets
├── index.html          # HTML template
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
└── vite.config.ts      # Vite configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

## Key Features Implementation

### State Management

The app uses Zustand for state management with the following stores:

- **useStore**: Main application state (inventory, orders, assemblies)
- **useTheme**: Theme management (light/dark/auto mode)

### API Integration

- **Axios Client**: Handles all HTTP requests with offline queue
- **WebSocket**: Real-time updates for inventory changes
- **React Query**: Caching and synchronization

### Material Design 3

- Custom theme with dynamic colors
- Elevated surfaces with layered depth
- Rounded corners and fluid animations
- Touch-optimized components

### Offline Support

- Service worker for caching assets
- Request queue for offline API calls
- Local storage persistence
- Automatic sync when back online

## Development Guide

### Adding a New Component

1. Create component file in appropriate directory
2. Use TypeScript interfaces for props
3. Implement touch gestures if needed
4. Add to component index

### API Endpoints

All API endpoints are defined in `src/api/endpoints.ts`:

```typescript
// Example usage
import { inventoryAPI } from '@api/endpoints';

const inventory = await inventoryAPI.getAll();
```

### State Management

```typescript
// Using the store
import { useStore } from '@store/useStore';

const Component = () => {
  const inventory = useStore(state => state.inventory);
  const updateInventory = useStore(state => state.updateInventoryItem);
  
  // Update inventory
  updateInventory(partId, newQuantity);
};
```

### Theme Customization

```typescript
// Using theme mode
import { useThemeStore } from '@store/useTheme';

const Component = () => {
  const { mode, toggleMode } = useThemeStore();
  
  return (
    <Button onClick={toggleMode}>
      Current theme: {mode}
    </Button>
  );
};
```

## Touch Optimization

### Minimum Touch Targets

All interactive elements have minimum 48px touch targets:

```css
button, a, input {
  min-height: 48px;
  min-width: 48px;
}
```

### Gesture Support

- Swipe left/right for navigation
- Pull to refresh
- Long press for context menus
- Pinch to zoom on charts

## Accessibility

- Keyboard navigation support
- Screen reader announcements
- High contrast mode support
- Focus indicators
- ARIA labels and roles

## Performance Optimization

- Code splitting by route
- Lazy loading components
- Virtual scrolling for large lists
- Image optimization
- Service worker caching

## Testing

```bash
# Run unit tests
npm test

# Run e2e tests
npm run test:e2e

# Run accessibility audit
npm run test:a11y
```

## Deployment

### Production Build

```bash
# Build the app
npm run build

# The build output will be in dist/
# Deploy the dist folder to your server
```

### Docker

```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Browser Support

- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- Chrome Android 90+
- Safari iOS 14+

## Contributing

1. Follow the TypeScript style guide
2. Write tests for new features
3. Ensure accessibility compliance
4. Test on tablet devices
5. Update documentation

## License

MIT

## Support

For issues or questions, please open an issue in the GitHub repository.