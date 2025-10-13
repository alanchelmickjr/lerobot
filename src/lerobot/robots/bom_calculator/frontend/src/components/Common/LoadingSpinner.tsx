import React from 'react';
import { Box, CircularProgress, Typography, Fade } from '@mui/material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
  fullScreen?: boolean;
  overlay?: boolean;
}

const SpinnerContainer = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'fullScreen' && prop !== 'overlay',
})<{ fullScreen?: boolean; overlay?: boolean }>(({ theme, fullScreen, overlay }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: theme.spacing(3),
  padding: theme.spacing(4),
  ...(fullScreen && {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: theme.zIndex.modal,
  }),
  ...(overlay && {
    backgroundColor: theme.palette.mode === 'dark' 
      ? 'rgba(0, 0, 0, 0.7)' 
      : 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(4px)',
  }),
}));

const RobotIcon = styled(motion.div)(({ theme }) => ({
  width: 64,
  height: 64,
  borderRadius: '50%',
  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '2rem',
  color: theme.palette.primary.contrastText,
  marginBottom: theme.spacing(2),
}));

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 48,
  fullScreen = false,
  overlay = false,
}) => {
  return (
    <Fade in={true} timeout={300}>
      <SpinnerContainer fullScreen={fullScreen} overlay={overlay}>
        <Box sx={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <RobotIcon
            animate={{
              rotate: [0, 360],
              scale: [1, 1.1, 1],
            }}
            transition={{
              rotate: {
                duration: 2,
                repeat: Infinity,
                ease: 'linear',
              },
              scale: {
                duration: 1.5,
                repeat: Infinity,
                ease: 'easeInOut',
              },
            }}
          >
            🤖
          </RobotIcon>
          <CircularProgress
            size={size}
            thickness={4}
            sx={{
              color: (theme) => theme.palette.primary.main,
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              },
            }}
          />
        </Box>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Typography 
              variant="body1" 
              color="textSecondary"
              sx={{ 
                fontWeight: 500,
                letterSpacing: 0.5,
              }}
            >
              {message}
            </Typography>
          </motion.div>
        )}
      </SpinnerContainer>
    </Fade>
  );
};

export default LoadingSpinner;