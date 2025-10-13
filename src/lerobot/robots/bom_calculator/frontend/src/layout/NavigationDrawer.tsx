import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
  Divider,
  IconButton,
  useTheme,
} from '@mui/material';
import {
  Dashboard,
  Inventory2,
  Build,
  ShoppingCart,
  Settings,
  ChevronLeft,
  PrecisionManufacturing,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useNavigate, useLocation } from 'react-router-dom';

interface NavigationDrawerProps {
  open: boolean;
  onClose: () => void;
  variant?: 'permanent' | 'persistent' | 'temporary';
}

const DrawerHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2),
  ...theme.mixins.toolbar,
  justifyContent: 'space-between',
  background: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
}));

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: 280,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: 280,
    boxSizing: 'border-box',
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(180deg, #1e1e1e 0%, #2d2d2d 100%)'
      : 'linear-gradient(180deg, #ffffff 0%, #f5f5f5 100%)',
    borderRight: `1px solid ${theme.palette.divider}`,
  },
}));

const StyledListItemButton = styled(ListItemButton)(({ theme }) => ({
  margin: theme.spacing(0.5, 1),
  borderRadius: theme.spacing(1),
  transition: 'all 0.2s ease',
  '&.Mui-selected': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    '& .MuiListItemIcon-root': {
      color: theme.palette.primary.contrastText,
    },
    '&:hover': {
      backgroundColor: theme.palette.primary.dark,
    },
  },
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
    transform: 'translateX(4px)',
  },
}));

const LogoSection = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/' },
  { text: 'Inventory', icon: <Inventory2 />, path: '/inventory' },
  { text: 'Assembly', icon: <Build />, path: '/assembly' },
  { text: 'Orders', icon: <ShoppingCart />, path: '/orders' },
  { text: 'Settings', icon: <Settings />, path: '/settings' },
];

const NavigationDrawer: React.FC<NavigationDrawerProps> = ({
  open,
  onClose,
  variant = 'temporary',
}) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (variant === 'temporary') {
      onClose();
    }
  };

  return (
    <StyledDrawer
      variant={variant}
      anchor="left"
      open={open}
      onClose={onClose}
    >
      <DrawerHeader>
        <LogoSection>
          <PrecisionManufacturing sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              BOM Calculator
            </Typography>
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              Robot Assembly Manager
            </Typography>
          </Box>
        </LogoSection>
        {variant === 'persistent' && (
          <IconButton onClick={onClose} sx={{ color: 'inherit' }}>
            <ChevronLeft />
          </IconButton>
        )}
      </DrawerHeader>

      <Divider />

      <List sx={{ px: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <StyledListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{ 
                  fontWeight: location.pathname === item.path ? 600 : 400 
                }}
              />
            </StyledListItemButton>
          </ListItem>
        ))}
      </List>

      <Box sx={{ flexGrow: 1 }} />

      <Divider />

      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="textSecondary" display="block" gutterBottom>
          Version 1.0.0
        </Typography>
        <Typography variant="caption" color="textSecondary">
          © 2024 LeRobot BOM Calculator
        </Typography>
      </Box>
    </StyledDrawer>
  );
};

export default NavigationDrawer;