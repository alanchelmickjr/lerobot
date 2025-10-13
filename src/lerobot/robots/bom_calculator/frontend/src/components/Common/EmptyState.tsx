import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';
import { 
  Inventory2Outlined, 
  PrecisionManufacturingOutlined,
  ShoppingCartOutlined,
  SearchOff,
  AddCircleOutline
} from '@mui/icons-material';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: 'inventory' | 'assembly' | 'orders' | 'search' | 'add' | React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  fullHeight?: boolean;
}

const EmptyStateContainer = styled(Paper, {
  shouldForwardProp: (prop) => prop !== 'fullHeight',
})<{ fullHeight?: boolean }>(({ theme, fullHeight }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(6),
  textAlign: 'center',
  background: theme.palette.mode === 'dark' 
    ? 'linear-gradient(135deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.05) 100%)'
    : 'linear-gradient(135deg, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0.05) 100%)',
  borderRadius: theme.spacing(2),
  border: `2px dashed ${theme.palette.divider}`,
  minHeight: fullHeight ? '60vh' : 300,
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: -100,
    right: -100,
    width: 200,
    height: 200,
    borderRadius: '50%',
    background: theme.palette.primary.main,
    opacity: 0.05,
  },
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: -50,
    left: -50,
    width: 150,
    height: 150,
    borderRadius: '50%',
    background: theme.palette.secondary.main,
    opacity: 0.05,
  },
}));

const IconWrapper = styled(motion.div)(({ theme }) => ({
  width: 120,
  height: 120,
  borderRadius: '50%',
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)'
    : 'linear-gradient(135deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.02) 100%)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginBottom: theme.spacing(3),
  position: 'relative',
  '& svg': {
    fontSize: 60,
    color: theme.palette.text.secondary,
  },
}));

const getIcon = (icon: EmptyStateProps['icon']) => {
  if (React.isValidElement(icon)) return icon;
  
  switch (icon) {
    case 'inventory':
      return <Inventory2Outlined />;
    case 'assembly':
      return <PrecisionManufacturingOutlined />;
    case 'orders':
      return <ShoppingCartOutlined />;
    case 'search':
      return <SearchOff />;
    case 'add':
      return <AddCircleOutline />;
    default:
      return <Inventory2Outlined />;
  }
};

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon = 'inventory',
  action,
  fullHeight = false,
}) => {
  return (
    <EmptyStateContainer fullHeight={fullHeight} elevation={0}>
      <IconWrapper
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{
          type: 'spring',
          stiffness: 200,
          damping: 20,
        }}
        whileHover={{ scale: 1.1, rotate: 5 }}
      >
        {getIcon(icon)}
      </IconWrapper>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Typography 
          variant="h5" 
          gutterBottom
          sx={{ 
            fontWeight: 600,
            color: 'text.primary',
            mb: 2,
          }}
        >
          {title}
        </Typography>
      </motion.div>

      {description && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Typography 
            variant="body1" 
            color="textSecondary"
            sx={{ 
              maxWidth: 400,
              mb: 4,
              lineHeight: 1.6,
            }}
          >
            {description}
          </Typography>
        </motion.div>
      )}

      {action && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Button
            variant="contained"
            size="large"
            onClick={action.onClick}
            startIcon={action.icon}
            sx={{
              px: 4,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1rem',
              fontWeight: 500,
              boxShadow: 2,
              '&:hover': {
                boxShadow: 4,
              },
            }}
          >
            {action.label}
          </Button>
        </motion.div>
      )}
    </EmptyStateContainer>
  );
};

export default EmptyState;