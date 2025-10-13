import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Badge,
  Tooltip,
  Avatar,
  Menu,
  MenuItem,
  Switch,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications,
  DarkMode,
  LightMode,
  AccountCircle,
  Sync,
  FullscreenExit,
  Fullscreen,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useTheme } from '../store/useTheme';

interface TopBarProps {
  onMenuClick: () => void;
  drawerOpen?: boolean;
}

const StyledAppBar = styled(AppBar, {
  shouldForwardProp: (prop) => prop !== 'open',
})<{ open?: boolean }>(({ theme, open }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(90deg, #1e1e1e 0%, #2d2d2d 100%)'
    : 'linear-gradient(90deg, #ffffff 0%, #f5f5f5 100%)',
  boxShadow: theme.shadows[2],
  borderBottom: `1px solid ${theme.palette.divider}`,
  [theme.breakpoints.up('md')]: {
    marginLeft: open ? 280 : 0,
    width: open ? `calc(100% - 280px)` : '100%',
  },
}));

const ToolbarContent = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  width: '100%',
}));

const ActionButtons = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

const TopBar: React.FC<TopBarProps> = ({ onMenuClick, drawerOpen = false }) => {
  const { isDarkMode, toggleTheme } = useTheme();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [isFullscreen, setIsFullscreen] = React.useState(false);
  const [lastSync, setLastSync] = React.useState(new Date());

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSync = () => {
    setLastSync(new Date());
    // Trigger data sync
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const formatLastSync = () => {
    const minutes = Math.floor((Date.now() - lastSync.getTime()) / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes === 1) return '1 minute ago';
    if (minutes < 60) return `${minutes} minutes ago`;
    return `${Math.floor(minutes / 60)} hours ago`;
  };

  return (
    <StyledAppBar position="fixed" open={drawerOpen}>
      <Toolbar>
        <ToolbarContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              onClick={onMenuClick}
              edge="start"
            >
              <MenuIcon />
            </IconButton>
            
            <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600 }}>
              Robot Assembly BOM Calculator
            </Typography>
          </Box>

          <ActionButtons>
            <Tooltip title={`Last sync: ${formatLastSync()}`}>
              <IconButton color="inherit" onClick={handleSync}>
                <Badge variant="dot" color="success">
                  <Sync />
                </Badge>
              </IconButton>
            </Tooltip>

            <Tooltip title="Toggle fullscreen">
              <IconButton color="inherit" onClick={toggleFullscreen}>
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
            </Tooltip>

            <Tooltip title="Notifications">
              <IconButton color="inherit">
                <Badge badgeContent={3} color="error">
                  <Notifications />
                </Badge>
              </IconButton>
            </Tooltip>

            <Tooltip title={isDarkMode ? 'Light mode' : 'Dark mode'}>
              <IconButton color="inherit" onClick={toggleTheme}>
                {isDarkMode ? <LightMode /> : <DarkMode />}
              </IconButton>
            </Tooltip>

            <Tooltip title="Account">
              <IconButton
                onClick={handleProfileMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                  U
                </Avatar>
              </IconButton>
            </Tooltip>
          </ActionButtons>
        </ToolbarContent>
      </Toolbar>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={handleMenuClose}>Profile</MenuItem>
        <MenuItem onClick={handleMenuClose}>My account</MenuItem>
        <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
      </Menu>
    </StyledAppBar>
  );
};

export default TopBar;