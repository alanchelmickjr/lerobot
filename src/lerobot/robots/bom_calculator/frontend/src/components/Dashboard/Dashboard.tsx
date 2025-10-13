import React from 'react';
import { Grid, Box, Container, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import AssemblyCapacityCard from './AssemblyCapacityCard';
import InventorySummaryCard from './InventorySummaryCard';
import RecentActivityCard from './RecentActivityCard';
import { styled } from '@mui/material/styles';

interface DashboardProps {
  data?: {
    robots: any[];
    inventory: any[];
    activities: any[];
  };
}

const DashboardContainer = styled(Container)(({ theme }) => ({
  paddingTop: theme.spacing(4),
  paddingBottom: theme.spacing(4),
  minHeight: '100vh',
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(180deg, #121212 0%, #1e1e1e 100%)'
    : 'linear-gradient(180deg, #f5f5f5 0%, #e0e0e0 100%)',
}));

const HeaderSection = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(4),
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, rgba(0,0,0,0.02) 0%, rgba(0,0,0,0.05) 100%)',
  backdropFilter: 'blur(10px)',
  border: `1px solid ${theme.palette.divider}`,
}));

const StyledGrid = styled(Grid)(({ theme }) => ({
  marginBottom: theme.spacing(3),
}));

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  const currentTime = new Date().toLocaleString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <DashboardContainer maxWidth="xl">
      <motion.div
        initial="hidden"
        animate="show"
        variants={container}
      >
        <HeaderSection>
          <motion.div variants={item}>
            <Typography
              variant="h3"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                marginBottom: 1,
              }}
            >
              Robot Assembly Dashboard
            </Typography>
            <Typography
              variant="subtitle1"
              color="textSecondary"
              sx={{ fontWeight: 500 }}
            >
              {currentTime}
            </Typography>
          </motion.div>
        </HeaderSection>

        <StyledGrid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <motion.div variants={item}>
              <AssemblyCapacityCard robots={data?.robots} />
            </motion.div>
          </Grid>
          
          <Grid item xs={12} lg={6}>
            <motion.div variants={item}>
              <InventorySummaryCard inventory={data?.inventory} />
            </motion.div>
          </Grid>

          <Grid item xs={12}>
            <motion.div variants={item}>
              <RecentActivityCard activities={data?.activities} />
            </motion.div>
          </Grid>
        </StyledGrid>
      </motion.div>
    </DashboardContainer>
  );
};

export default Dashboard;