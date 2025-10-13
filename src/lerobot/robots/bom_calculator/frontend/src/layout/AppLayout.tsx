import React, { useState } from 'react';
import { Box, useTheme, useMediaQuery } from '@mui/material';
import { styled } from '@mui/material/styles';
import TopBar from './TopBar';
import NavigationDrawer from './NavigationDrawer';
import { Outlet } from 'react-router-dom';

interface AppLayoutProps {
  children?: React.ReactNode;
}

const LayoutContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
  backgroundColor: theme.palette.background.default,
}));

const MainContent = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'open',
})<{ open?: boolean }>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginLeft: 0,
  [theme.breakpoints.up('md')]: {
    marginLeft: open ? 280 : 0,
  },
}));

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.up('md'));
  const [drawerOpen, setDrawerOpen] = useState(isTablet);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);

  const handleDrawerToggle = () => {
    if (isTablet) {
      setDrawerOpen(!drawerOpen);
    } else {
      setMobileDrawerOpen(!mobileDrawerOpen);
    }
  };

  return (
    <LayoutContainer>
      <TopBar 
        onMenuClick={handleDrawerToggle}
        drawerOpen={drawerOpen}
      />
      <NavigationDrawer
        open={isTablet ? drawerOpen : mobileDrawerOpen}
        onClose={() => setMobileDrawerOpen(false)}
        variant={isTablet ? 'persistent' : 'temporary'}
      />
      <MainContent open={isTablet && drawerOpen}>
        {children || <Outlet />}
      </MainContent>
    </LayoutContainer>
  );
};

export default AppLayout;