import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Inventory2,
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  InfoOutlined,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  Legend,
} from 'recharts';

interface InventoryItem {
  id: string;
  category: string;
  totalParts: number;
  inStock: number;
  lowStock: number;
  outOfStock: number;
  value: number;
}

interface InventorySummaryCardProps {
  inventory?: InventoryItem[];
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

const StatBox = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  textAlign: 'center',
  transition: 'all 0.2s ease',
  cursor: 'pointer',
  '&:hover': {
    background: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.04)',
    borderColor: theme.palette.primary.main,
    transform: 'translateY(-2px)',
  },
}));

const CategoryChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  borderRadius: theme.spacing(1),
  fontWeight: 600,
  '&:hover': {
    transform: 'scale(1.05)',
  },
}));

const mockInventory: InventoryItem[] = [
  {
    id: '1',
    category: 'Motors',
    totalParts: 45,
    inStock: 38,
    lowStock: 5,
    outOfStock: 2,
    value: 4500,
  },
  {
    id: '2',
    category: 'Sensors',
    totalParts: 30,
    inStock: 25,
    lowStock: 4,
    outOfStock: 1,
    value: 2800,
  },
  {
    id: '3',
    category: 'Controllers',
    totalParts: 20,
    inStock: 18,
    lowStock: 2,
    outOfStock: 0,
    value: 6000,
  },
  {
    id: '4',
    category: 'Structural',
    totalParts: 60,
    inStock: 55,
    lowStock: 3,
    outOfStock: 2,
    value: 1500,
  },
];

const InventorySummaryCard: React.FC<InventorySummaryCardProps> = ({ inventory = mockInventory }) => {
  const totalParts = inventory.reduce((sum, item) => sum + item.totalParts, 0);
  const totalInStock = inventory.reduce((sum, item) => sum + item.inStock, 0);
  const totalLowStock = inventory.reduce((sum, item) => sum + item.lowStock, 0);
  const totalOutOfStock = inventory.reduce((sum, item) => sum + item.outOfStock, 0);
  const totalValue = inventory.reduce((sum, item) => sum + item.value, 0);

  const pieData = [
    { name: 'In Stock', value: totalInStock, color: '#4caf50' },
    { name: 'Low Stock', value: totalLowStock, color: '#ff9800' },
    { name: 'Out of Stock', value: totalOutOfStock, color: '#f44336' },
  ];

  const healthScore = Math.round((totalInStock / totalParts) * 100);

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getHealthIcon = (score: number) => {
    if (score >= 80) return <CheckCircle sx={{ color: '#4caf50' }} />;
    if (score >= 60) return <Warning sx={{ color: '#ff9800' }} />;
    return <Warning sx={{ color: '#f44336' }} />;
  };

  return (
    <StyledCard elevation={0}>
      <CardContent sx={{ p: 3 }}>
        <HeaderBox>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Inventory2 sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Inventory Summary
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total value: ${totalValue.toLocaleString()}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {getHealthIcon(healthScore)}
            <Typography variant="h6" color={`${getHealthColor(healthScore)}.main`} sx={{ fontWeight: 700 }}>
              {healthScore}%
            </Typography>
            <Tooltip title="View detailed inventory">
              <IconButton size="small">
                <InfoOutlined />
              </IconButton>
            </Tooltip>
          </Box>
        </HeaderBox>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6} md={3}>
            <StatBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              whileHover={{ scale: 1.02 }}
            >
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                {totalParts}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Total Parts
              </Typography>
            </StatBox>
          </Grid>
          <Grid item xs={6} md={3}>
            <StatBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              whileHover={{ scale: 1.02 }}
            >
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
                {totalInStock}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                In Stock
              </Typography>
            </StatBox>
          </Grid>
          <Grid item xs={6} md={3}>
            <StatBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              whileHover={{ scale: 1.02 }}
            >
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                {totalLowStock}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Low Stock
              </Typography>
            </StatBox>
          </Grid>
          <Grid item xs={6} md={3}>
            <StatBox
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              whileHover={{ scale: 1.02 }}
            >
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'error.main' }}>
                {totalOutOfStock}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Out of Stock
              </Typography>
            </StatBox>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Categories
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
              {inventory.map((item) => (
                <CategoryChip
                  key={item.id}
                  label={`${item.category} (${item.totalParts})`}
                  color={item.outOfStock > 0 ? 'error' : item.lowStock > 3 ? 'warning' : 'success'}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
          
          <Box sx={{ width: 180, height: 180 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="textSecondary">
            Last updated: 2 minutes ago
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <TrendingUp sx={{ fontSize: 16, color: '#4caf50' }} />
              <Typography variant="caption" sx={{ color: '#4caf50' }}>
                +5% this week
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default InventorySummaryCard;