import { ThemeOptions, alpha } from '@mui/material/styles';
import { Shadows } from '@mui/material/styles/shadows';

// Material Design 3 Color Tokens
const colorTokens = {
  light: {
    primary: {
      main: '#6750A4',
      light: '#B69DF8',
      dark: '#4A3D7B',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#625B71',
      light: '#CCC2DC',
      dark: '#4A4458',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#BA1A1A',
      light: '#F2B8B5',
      dark: '#8C1D18',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#FFA726',
      light: '#FFB74D',
      dark: '#F57C00',
      contrastText: '#000000',
    },
    info: {
      main: '#0DCAF0',
      light: '#CFF4FC',
      dark: '#0AA2C0',
      contrastText: '#000000',
    },
    success: {
      main: '#198754',
      light: '#7FDB8A',
      dark: '#146C43',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FEF7FF',
      paper: '#FFFFFF',
    },
    surface: {
      default: '#FFFFFF',
      variant: '#E7E0EC',
      inverse: '#313033',
      tint: '#6750A4',
    },
    text: {
      primary: '#1C1B1F',
      secondary: '#49454F',
      disabled: 'rgba(28, 27, 31, 0.38)',
    },
    divider: 'rgba(28, 27, 31, 0.12)',
  },
  dark: {
    primary: {
      main: '#D0BCFF',
      light: '#E8DEF8',
      dark: '#B69DF8',
      contrastText: '#381E72',
    },
    secondary: {
      main: '#CCC2DC',
      light: '#E8DEF8',
      dark: '#958DA5',
      contrastText: '#332D41',
    },
    error: {
      main: '#F2B8B5',
      light: '#F9DEDC',
      dark: '#DC3545',
      contrastText: '#601410',
    },
    warning: {
      main: '#FFB74D',
      light: '#FFD54F',
      dark: '#FFA726',
      contrastText: '#000000',
    },
    info: {
      main: '#CFF4FC',
      light: '#E7F9FF',
      dark: '#0DCAF0',
      contrastText: '#003640',
    },
    success: {
      main: '#7FDB8A',
      light: '#A5E9B0',
      dark: '#198754',
      contrastText: '#003910',
    },
    background: {
      default: '#1C1B1F',
      paper: '#2B2930',
    },
    surface: {
      default: '#1C1B1F',
      variant: '#49454F',
      inverse: '#E6E1E5',
      tint: '#D0BCFF',
    },
    text: {
      primary: '#E6E1E5',
      secondary: '#CAC4D0',
      disabled: 'rgba(230, 225, 229, 0.38)',
    },
    divider: 'rgba(230, 225, 229, 0.12)',
  },
};

// Create custom shadows for Material Design 3 elevation
const createElevation = (mode: 'light' | 'dark'): Shadows => {
  const shadowColor = mode === 'light' ? '0, 0, 0' : '0, 0, 0';
  const elevations: Shadows = [
    'none',
    `0px 1px 2px rgba(${shadowColor}, 0.05)`,
    `0px 2px 4px rgba(${shadowColor}, 0.08)`,
    `0px 4px 8px rgba(${shadowColor}, 0.10)`,
    `0px 6px 12px rgba(${shadowColor}, 0.12)`,
    `0px 8px 16px rgba(${shadowColor}, 0.15)`,
    // ... continue for all 25 levels
    ...Array(19).fill('').map((_, i) => 
      `0px ${8 + i * 2}px ${16 + i * 4}px rgba(${shadowColor}, ${0.15 + i * 0.01})`
    ),
  ] as Shadows;
  return elevations;
};

export const getDesignTokens = (mode: 'light' | 'dark', primaryColor?: string): ThemeOptions => {
  const colors = colorTokens[mode];
  
  // Override primary color if provided
  if (primaryColor) {
    colors.primary.main = primaryColor;
  }

  return {
    palette: {
      mode,
      ...colors,
      action: {
        active: mode === 'light' ? alpha('#6750A4', 0.54) : alpha('#D0BCFF', 0.54),
        hover: mode === 'light' ? alpha('#6750A4', 0.08) : alpha('#D0BCFF', 0.08),
        selected: mode === 'light' ? alpha('#6750A4', 0.12) : alpha('#D0BCFF', 0.12),
        disabled: mode === 'light' ? alpha('#000000', 0.26) : alpha('#FFFFFF', 0.26),
        disabledBackground: mode === 'light' ? alpha('#000000', 0.12) : alpha('#FFFFFF', 0.12),
      },
    },
    typography: {
      fontFamily: '"Roboto Flex", "Roboto", "Helvetica", "Arial", sans-serif',
      // Display
      h1: {
        fontSize: '57px',
        lineHeight: '64px',
        fontWeight: 400,
        letterSpacing: '-0.25px',
      },
      h2: {
        fontSize: '45px',
        lineHeight: '52px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      h3: {
        fontSize: '36px',
        lineHeight: '44px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      // Headline
      h4: {
        fontSize: '32px',
        lineHeight: '40px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      h5: {
        fontSize: '28px',
        lineHeight: '36px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      h6: {
        fontSize: '24px',
        lineHeight: '32px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      // Title
      subtitle1: {
        fontSize: '22px',
        lineHeight: '28px',
        fontWeight: 400,
        letterSpacing: '0px',
      },
      subtitle2: {
        fontSize: '16px',
        lineHeight: '24px',
        fontWeight: 500,
        letterSpacing: '0.15px',
      },
      // Body
      body1: {
        fontSize: '16px',
        lineHeight: '24px',
        fontWeight: 400,
        letterSpacing: '0.5px',
      },
      body2: {
        fontSize: '14px',
        lineHeight: '20px',
        fontWeight: 400,
        letterSpacing: '0.25px',
      },
      // Label
      button: {
        fontSize: '14px',
        lineHeight: '20px',
        fontWeight: 500,
        letterSpacing: '0.1px',
        textTransform: 'none', // MD3 doesn't use uppercase for buttons
      },
      caption: {
        fontSize: '12px',
        lineHeight: '16px',
        fontWeight: 400,
        letterSpacing: '0.4px',
      },
      overline: {
        fontSize: '11px',
        lineHeight: '16px',
        fontWeight: 500,
        letterSpacing: '0.5px',
        textTransform: 'uppercase',
      },
    },
    shape: {
      borderRadius: 16, // MD3 uses larger border radius
    },
    shadows: createElevation(mode),
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          body: {
            scrollbarColor: mode === 'light' ? '#B69DF8 #F6EDFF' : '#625B71 #2B2930',
            '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
              width: '8px',
              height: '8px',
            },
            '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
              borderRadius: '4px',
              backgroundColor: mode === 'light' ? '#B69DF8' : '#625B71',
            },
            '&::-webkit-scrollbar-track, & *::-webkit-scrollbar-track': {
              backgroundColor: mode === 'light' ? '#F6EDFF' : '#2B2930',
            },
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: '20px',
            padding: '10px 24px',
            fontSize: '14px',
            fontWeight: 500,
            minHeight: '40px',
            textTransform: 'none',
            boxShadow: 'none',
            '&:hover': {
              boxShadow: `0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15)`,
            },
          },
          contained: {
            '&:hover': {
              boxShadow: `0px 2px 4px rgba(0, 0, 0, 0.3), 0px 4px 5px rgba(0, 0, 0, 0.15)`,
            },
          },
          text: {
            padding: '10px 12px',
          },
          sizeLarge: {
            minHeight: '56px',
            fontSize: '15px',
            padding: '16px 24px',
            borderRadius: '28px',
          },
          sizeSmall: {
            minHeight: '32px',
            fontSize: '13px',
            padding: '6px 16px',
            borderRadius: '16px',
          },
        },
      },
      MuiIconButton: {
        styleOverrides: {
          root: {
            padding: '12px',
            '&:hover': {
              backgroundColor: mode === 'light' 
                ? alpha('#6750A4', 0.08) 
                : alpha('#D0BCFF', 0.08),
            },
          },
          sizeLarge: {
            padding: '16px',
          },
          sizeSmall: {
            padding: '8px',
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: '24px',
            boxShadow: mode === 'light'
              ? '0px 2px 4px rgba(0, 0, 0, 0.08)'
              : '0px 2px 4px rgba(0, 0, 0, 0.2)',
            backgroundImage: 'none',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
          },
          rounded: {
            borderRadius: '16px',
          },
          elevation1: {
            boxShadow: mode === 'light'
              ? '0px 1px 2px rgba(0, 0, 0, 0.05)'
              : '0px 1px 2px rgba(0, 0, 0, 0.15)',
          },
          elevation2: {
            boxShadow: mode === 'light'
              ? '0px 2px 4px rgba(0, 0, 0, 0.08)'
              : '0px 2px 4px rgba(0, 0, 0, 0.2)',
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: '12px',
              '&.Mui-focused fieldset': {
                borderWidth: '2px',
              },
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: '8px',
            height: '32px',
            fontWeight: 500,
          },
          sizeSmall: {
            height: '24px',
            fontSize: '12px',
          },
          sizeMedium: {
            height: '32px',
            fontSize: '14px',
          },
        },
      },
      MuiTab: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            fontWeight: 500,
            fontSize: '14px',
            marginRight: '16px',
            minHeight: '48px',
            padding: '12px 16px',
            '&.Mui-selected': {
              fontWeight: 600,
            },
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          indicator: {
            height: '3px',
            borderRadius: '3px 3px 0 0',
          },
        },
      },
      MuiFab: {
        styleOverrides: {
          root: {
            borderRadius: '16px',
            boxShadow: mode === 'light'
              ? '0px 4px 8px rgba(0, 0, 0, 0.10)'
              : '0px 4px 8px rgba(0, 0, 0, 0.3)',
            '&:hover': {
              boxShadow: mode === 'light'
                ? '0px 6px 12px rgba(0, 0, 0, 0.12)'
                : '0px 6px 12px rgba(0, 0, 0, 0.4)',
            },
          },
          sizeLarge: {
            width: '96px',
            height: '96px',
            borderRadius: '28px',
          },
          sizeSmall: {
            width: '40px',
            height: '40px',
            borderRadius: '12px',
          },
        },
      },
      MuiSwitch: {
        styleOverrides: {
          root: {
            width: '52px',
            height: '32px',
            padding: '4px',
            '& .MuiSwitch-switchBase': {
              padding: '6px',
              '&.Mui-checked': {
                transform: 'translateX(20px)',
              },
            },
            '& .MuiSwitch-thumb': {
              width: '20px',
              height: '20px',
            },
            '& .MuiSwitch-track': {
              borderRadius: '16px',
            },
          },
        },
      },
    },
  };
};