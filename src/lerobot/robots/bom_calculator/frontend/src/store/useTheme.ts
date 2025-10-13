import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type ThemeMode = 'light' | 'dark' | 'auto';

interface ThemeState {
  mode: ThemeMode;
  primary: string;
  secondary: string;
  actualMode: 'light' | 'dark'; // Resolved mode when 'auto' is selected
  
  // Actions
  setMode: (mode: ThemeMode) => void;
  setPrimary: (color: string) => void;
  setSecondary: (color: string) => void;
  toggleMode: () => void;
  resetTheme: () => void;
  
  // Computed
  getResolvedMode: () => 'light' | 'dark';
}

const defaultPrimary = '#6750A4';
const defaultSecondary = '#625B71';

// Detect system theme preference
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: 'auto',
      primary: defaultPrimary,
      secondary: defaultSecondary,
      actualMode: getSystemTheme(),
      
      setMode: (mode) =>
        set((state) => ({
          mode,
          actualMode: mode === 'auto' ? getSystemTheme() : mode,
        })),
      
      setPrimary: (color) =>
        set({
          primary: color,
        }),
      
      setSecondary: (color) =>
        set({
          secondary: color,
        }),
      
      toggleMode: () =>
        set((state) => {
          const modes: ThemeMode[] = ['light', 'dark', 'auto'];
          const currentIndex = modes.indexOf(state.mode);
          const nextMode = modes[(currentIndex + 1) % modes.length];
          
          return {
            mode: nextMode,
            actualMode: nextMode === 'auto' ? getSystemTheme() : nextMode,
          };
        }),
      
      resetTheme: () =>
        set({
          mode: 'auto',
          primary: defaultPrimary,
          secondary: defaultSecondary,
          actualMode: getSystemTheme(),
        }),
      
      getResolvedMode: () => {
        const state = get();
        return state.mode === 'auto' ? getSystemTheme() : state.mode;
      },
    }),
    {
      name: 'theme-preferences',
    }
  )
);

// Listen for system theme changes
if (typeof window !== 'undefined') {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  mediaQuery.addEventListener('change', (e) => {
    const state = useThemeStore.getState();
    if (state.mode === 'auto') {
      useThemeStore.setState({
        actualMode: e.matches ? 'dark' : 'light',
      });
    }
  });
}

// Export hooks for common use cases
export const useThemeMode = () => useThemeStore((state) => state.getResolvedMode());
export const useThemeColors = () =>
  useThemeStore((state) => ({
    primary: state.primary,
    secondary: state.secondary,
  }));