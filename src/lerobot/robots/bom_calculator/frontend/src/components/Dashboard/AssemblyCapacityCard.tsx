import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  PrecisionManufacturing,
  InfoOutlined,
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from 'recharts';

interface RobotCapacity {
  id: string;
  name: string;
  model: string;
  buildableQuantity: number;
  maxCapacity: number;
  bottleneckPart?: string;
  utilizationRate: number;
}

interface AssemblyCapacityCardProps {
  robots?: RobotCapacity[];
}

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: theme.shadows[8],
    transform: 'translateY(-4px)',
  },
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(3),
  paddingBottom: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const RobotItem = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.2s ease',
  '&:hover': {
    background: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.04)',
    borderColor: theme.palette.primary.main,
  },
}));

const CapacityBar = styled(LinearProgress)(({ theme }) => ({
  height: 10,
  borderRadius: 5,
  backgroundColor: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.1)'
    : 'rgba(0, 0, 0, 0.1)',
  '& .MuiLinearProgress-bar': {
    borderRadius: 5,
    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
  },
}));

const mockData: RobotCapacity[] = [
  {
    id: '1',
    name: 'Koch v1.1',
    model: 'koch_v1_1',
    buildableQuantity: 8,
    maxCapacity: 10,
    bottleneckPart: 'Servo Motor XL320',
    utilizationRate: 80,
  },
  {
    id: '2',
    name: 'SO-100',
    model: 'so100',
    buildableQuantity: 5,
    maxCapacity: 12,
    bottleneckPart: 'Control Board',
    utilizationRate: 42,
  },
  {
    id: '3',
    name: 'ViperX',
    model: 'viperx',
    buildableQuantity: 3,
    maxCapacity: 8,
    bottleneckPart: 'Gripper Assembly',
    utilizationRate: 37,
  },
];

const AssemblyCapacityCard: React.FC<AssemblyCapacityCardProps> = ({ robots = mockData }) => {
  const totalCapacity = robots.reduce((sum, robot) => sum + robot.buildableQuantity, 0);
  const maxTotal = robots.reduce((sum, robot) => sum + robot.maxCapacity, 0);
  const averageUtilization = robots.reduce((sum, robot) => sum + robot.utilizationRate, 0) / robots.length;

  const chartData = robots.map(robot => ({
    name: robot.name,
    value: robot.utilizationRate,
    fill: robot.utilizationRate > 70 ? '#4caf50' : robot.utilizationRate > 40 ? '#ff9800' : '#f44336',
  }));

  const getTrendIcon = (rate: number) => {
    if (rate > 70) return <TrendingUp sx={{ color: '#4caf50' }} />;
    if (rate > 40) return null;
    return <TrendingDown sx={{ color: '#f44336' }} />;
  };

  const getStatusColor = (rate: number) => {
    if (rate > 70) return 'success';
    if (rate > 40) return 'warning';
    return 'error';
  };

  return (
    <StyledCard elevation={0}>
      <CardContent sx={{ p: 3 }}>
        <HeaderBox>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <PrecisionManufacturing sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Assembly Capacity
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total buildable: {totalCapacity} / {maxTotal} robots
              </Typography>
            </Box>
          </Box>
          <Tooltip title="View detailed assembly report">
            <IconButton size="small">
              <InfoOutlined />
            </IconButton>
          </Tooltip>
        </HeaderBox>

        <Box sx={{ display: 'flex', gap: 3 }}>
          <Box sx={{ flex: 1 }}>
            {robots.map((robot, index) => (
              <RobotItem
                key={robot.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {robot.name}
                    </Typography>
                    {getTrendIcon(robot.utilizationRate)}
                  </Box>
                  <Chip
                    label={`${robot.buildableQuantity} units`}
                    color={getStatusColor(robot.utilizationRate)}
                    size="small"
                    sx={{ fontWeight: 600 }}
                  />
                </Box>
                
                <Box sx={{ mb: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" color="textSecondary">
                      Capacity utilization
                    </Typography>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      {robot.utilizationRate}%
                    </Typography>
                  </Box>
                  <CapacityBar variant="determinate" value={robot.utilizationRate} />
                </Box>

                {robot.bottleneckPart && (
                  <Typography variant="caption" color="error" sx={{ display: 'block', mt: 1 }}>
                    ⚠️ Limited by: {robot.bottleneckPart}
                  </Typography>
                )}
              </RobotItem>
            ))}
          </Box>

          <Box sx={{ width: 200, height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="90%" data={chartData}>
                <PolarAngleAxis
                  type="number"
                  domain={[0, 100]}
                  angleAxisId={0}
                  tick={false}
                />
                <RadialBar
                  dataKey="value"
                  cornerRadius={10}
                  fill="#8884d8"
                />
                <RechartsTooltip />
              </RadialBarChart>
            </ResponsiveContainer>
            <Typography
              variant="h4"
              sx={{
                textAlign: 'center',
                fontWeight: 700,
                color: averageUtilization > 70 ? 'success.main' : averageUtilization > 40 ? 'warning.main' : 'error.main',
                mt: -10,
              }}
            >
              {Math.round(averageUtilization)}%
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'textSecondary' }}>
              Avg. Utilization
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default AssemblyCapacityCard;