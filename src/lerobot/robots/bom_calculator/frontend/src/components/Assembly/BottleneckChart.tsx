import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Tooltip,
  IconButton,
  LinearProgress,
} from '@mui/material';
import {
  Warning,
  CheckCircle,
  Error,
  InfoOutlined,
  TrendingDown,
  TrendingUp,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  LabelList,
} from 'recharts';

interface BottleneckData {
  partId: string;
  partName: string;
  required: number;
  available: number;
  shortage: number;
  impactLevel: 'critical' | 'high' | 'medium' | 'low';
  affectedRobots: string[];
}

interface BottleneckChartProps {
  data?: BottleneckData[];
  onPartClick?: (partId: string) => void;
}

const ChartContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(3),
  paddingBottom: theme.spacing(2),
  borderBottom: `2px solid ${theme.palette.divider}`,
}));

const BottleneckItem = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1.5),
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    transform: 'translateX(4px)',
    borderColor: theme.palette.primary.main,
    boxShadow: theme.shadows[2],
  },
}));

const ImpactChip = styled(Chip)(({ theme }) => ({
  fontWeight: 600,
  borderRadius: theme.spacing(1),
}));

const ProgressBar = styled(LinearProgress)(({ theme }) => ({
  height: 8,
  borderRadius: 4,
  backgroundColor: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.1)'
    : 'rgba(0, 0, 0, 0.1)',
}));

const mockData: BottleneckData[] = [
  {
    partId: 'XL320',
    partName: 'Servo Motor XL320',
    required: 60,
    available: 45,
    shortage: 15,
    impactLevel: 'critical',
    affectedRobots: ['Koch v1.1', 'Koch v1.2'],
  },
  {
    partId: 'CTRL-01',
    partName: 'Control Board',
    required: 20,
    available: 8,
    shortage: 12,
    impactLevel: 'high',
    affectedRobots: ['SO-100'],
  },
  {
    partId: 'GRP-01',
    partName: 'Gripper Assembly',
    required: 10,
    available: 3,
    shortage: 7,
    impactLevel: 'medium',
    affectedRobots: ['ViperX'],
  },
  {
    partId: 'FRAME-01',
    partName: 'Frame Component',
    required: 30,
    available: 25,
    shortage: 5,
    impactLevel: 'low',
    affectedRobots: ['Koch v1.1'],
  },
];

const BottleneckChart: React.FC<BottleneckChartProps> = ({ 
  data = mockData,
  onPartClick,
}) => {
  const getImpactColor = (level: string) => {
    switch (level) {
      case 'critical':
        return '#f44336';
      case 'high':
        return '#ff9800';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  const getImpactIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <Error sx={{ fontSize: 16 }} />;
      case 'high':
        return <Warning sx={{ fontSize: 16 }} />;
      case 'medium':
        return <TrendingDown sx={{ fontSize: 16 }} />;
      case 'low':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const chartData = data.map(item => ({
    name: item.partName.length > 15 ? `${item.partName.substring(0, 15)}...` : item.partName,
    fullName: item.partName,
    available: item.available,
    required: item.required,
    shortage: item.shortage,
    fillColor: getImpactColor(item.impactLevel),
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper
          sx={{
            p: 2,
            borderRadius: 1,
            boxShadow: 3,
            border: 1,
            borderColor: 'divider',
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
            {data.fullName}
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
            <Typography variant="caption">
              Available: <strong>{data.available}</strong>
            </Typography>
            <Typography variant="caption">
              Required: <strong>{data.required}</strong>
            </Typography>
            <Typography variant="caption" color="error">
              Shortage: <strong>{data.shortage}</strong>
            </Typography>
          </Box>
        </Paper>
      );
    }
    return null;
  };

  return (
    <ChartContainer elevation={0}>
      <HeaderBox>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Warning sx={{ fontSize: 32, color: 'warning.main' }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Bottleneck Analysis
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Parts limiting assembly capacity
            </Typography>
          </Box>
        </Box>
        <Tooltip title="View detailed bottleneck report">
          <IconButton size="small">
            <InfoOutlined />
          </IconButton>
        </Tooltip>
      </HeaderBox>

      <Box sx={{ height: 300, mb: 4 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis 
              dataKey="name" 
              angle={-45}
              textAnchor="end"
              height={80}
              interval={0}
              tick={{ fontSize: 12 }}
            />
            <YAxis 
              label={{ value: 'Quantity', angle: -90, position: 'insideLeft' }}
              tick={{ fontSize: 12 }}
            />
            <RechartsTooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="available" fill="#4caf50" name="Available" />
            <Bar dataKey="required" fill="#2196f3" name="Required">
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fillColor} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>

      <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
        Critical Bottlenecks
      </Typography>

      <Box>
        {data.map((item, index) => (
          <BottleneckItem
            key={item.partId}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onPartClick && onPartClick(item.partId)}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1.5 }}>
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    {item.partName}
                  </Typography>
                  <ImpactChip
                    icon={getImpactIcon(item.impactLevel)}
                    label={item.impactLevel.toUpperCase()}
                    size="small"
                    sx={{
                      backgroundColor: getImpactColor(item.impactLevel),
                      color: 'white',
                    }}
                  />
                </Box>
                <Typography variant="caption" color="textSecondary">
                  Part #{item.partId}
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'right' }}>
                <Typography variant="h6" color="error" sx={{ fontWeight: 700 }}>
                  -{item.shortage}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  shortage
                </Typography>
              </Box>
            </Box>

            <Box sx={{ mb: 1.5 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="caption" color="textSecondary">
                  Availability
                </Typography>
                <Typography variant="caption" sx={{ fontWeight: 600 }}>
                  {item.available} / {item.required} units
                </Typography>
              </Box>
              <ProgressBar
                variant="determinate"
                value={(item.available / item.required) * 100}
                sx={{
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getImpactColor(item.impactLevel),
                  },
                }}
              />
            </Box>

            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
              <Typography variant="caption" color="textSecondary">
                Affects:
              </Typography>
              {item.affectedRobots.map((robot) => (
                <Chip
                  key={robot}
                  label={robot}
                  size="small"
                  variant="outlined"
                  sx={{ height: 20, fontSize: 11 }}
                />
              ))}
            </Box>
          </BottleneckItem>
        ))}
      </Box>
    </ChartContainer>
  );
};

export default BottleneckChart;