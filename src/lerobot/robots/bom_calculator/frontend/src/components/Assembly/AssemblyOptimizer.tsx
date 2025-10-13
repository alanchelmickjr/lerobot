import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Slider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Grid,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  AutoFixHigh,
  TrendingUp,
  Speed,
  AttachMoney,
  Schedule,
  CheckCircle,
  InfoOutlined,
  Refresh,
  Settings,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface OptimizationResult {
  strategy: 'cost' | 'speed' | 'balanced';
  robots: {
    id: string;
    name: string;
    quantity: number;
    cost: number;
    time: number;
  }[];
  totalCost: number;
  totalTime: number;
  efficiency: number;
  constraints: string[];
}

interface AssemblyOptimizerProps {
  onOptimize?: (result: OptimizationResult) => void;
}

const OptimizerContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
}));

const StrategyCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  border: `2px solid transparent`,
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[8],
  },
  '&.selected': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.selected,
  },
}));

const MetricBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.03)',
  textAlign: 'center',
  border: `1px solid ${theme.palette.divider}`,
}));

const ResultCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(1),
}));

const AssemblyOptimizer: React.FC<AssemblyOptimizerProps> = ({ onOptimize }) => {
  const [strategy, setStrategy] = useState<'cost' | 'speed' | 'balanced'>('balanced');
  const [budget, setBudget] = useState(5000);
  const [timeLimit, setTimeLimit] = useState(24);
  const [optimizing, setOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);

  const handleOptimize = () => {
    setOptimizing(true);
    
    // Simulate optimization
    setTimeout(() => {
      const mockResult: OptimizationResult = {
        strategy,
        robots: [
          { id: '1', name: 'Koch v1.1', quantity: 5, cost: 1500, time: 10 },
          { id: '2', name: 'SO-100', quantity: 3, cost: 2000, time: 8 },
          { id: '3', name: 'ViperX', quantity: 2, cost: 1200, time: 6 },
        ],
        totalCost: 4700,
        totalTime: 24,
        efficiency: 85,
        constraints: ['Limited by XL320 motors', 'Budget constraint active'],
      };
      
      setResult(mockResult);
      if (onOptimize) {
        onOptimize(mockResult);
      }
      setOptimizing(false);
    }, 2000);
  };

  const radarData = result ? [
    { metric: 'Cost Efficiency', value: 75 },
    { metric: 'Time Efficiency', value: 85 },
    { metric: 'Resource Usage', value: 90 },
    { metric: 'Quality', value: 95 },
    { metric: 'Flexibility', value: 70 },
    { metric: 'Scalability', value: 80 },
  ] : [];

  const getStrategyIcon = (s: string) => {
    switch (s) {
      case 'cost':
        return <AttachMoney />;
      case 'speed':
        return <Speed />;
      case 'balanced':
        return <AutoFixHigh />;
      default:
        return <Settings />;
    }
  };

  const getStrategyColor = (s: string) => {
    switch (s) {
      case 'cost':
        return 'success';
      case 'speed':
        return 'warning';
      case 'balanced':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <OptimizerContainer elevation={0}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <AutoFixHigh sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box sx={{ flex: 1 }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Assembly Optimizer
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Find the optimal build mix for your constraints
          </Typography>
        </Box>
        <Tooltip title="Reset optimizer">
          <IconButton onClick={() => setResult(null)}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            Optimization Strategy
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {(['cost', 'speed', 'balanced'] as const).map((s) => (
              <Grid item xs={12} sm={4} key={s}>
                <StrategyCard
                  className={strategy === s ? 'selected' : ''}
                  onClick={() => setStrategy(s)}
                  elevation={0}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    {getStrategyIcon(s)}
                    <Typography variant="subtitle2" sx={{ mt: 1, fontWeight: 600 }}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      {s === 'cost' ? 'Minimize cost' : 
                       s === 'speed' ? 'Fastest build' : 
                       'Best overall'}
                    </Typography>
                  </CardContent>
                </StrategyCard>
              </Grid>
            ))}
          </Grid>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Budget Constraint: ${budget.toLocaleString()}
            </Typography>
            <Slider
              value={budget}
              onChange={(_, value) => setBudget(value as number)}
              min={1000}
              max={10000}
              step={100}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `$${value.toLocaleString()}`}
            />
          </Box>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Time Limit: {timeLimit} hours
            </Typography>
            <Slider
              value={timeLimit}
              onChange={(_, value) => setTimeLimit(value as number)}
              min={1}
              max={72}
              step={1}
              valueLabelDisplay="auto"
              valueLabelFormat={(value) => `${value}h`}
            />
          </Box>

          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={optimizing ? null : <TrendingUp />}
            onClick={handleOptimize}
            disabled={optimizing}
            sx={{
              py: 2,
              borderRadius: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
            }}
          >
            {optimizing ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <LinearProgress sx={{ width: 100 }} />
                Optimizing...
              </Box>
            ) : (
              'Optimize Assembly'
            )}
          </Button>
        </Grid>

        <Grid item xs={12} md={6}>
          {result && (
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Optimization Results
                </Typography>

                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={4}>
                    <MetricBox>
                      <Typography variant="h4" color="success.main" sx={{ fontWeight: 700 }}>
                        ${result.totalCost}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Total Cost
                      </Typography>
                    </MetricBox>
                  </Grid>
                  <Grid item xs={4}>
                    <MetricBox>
                      <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>
                        {result.totalTime}h
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Build Time
                      </Typography>
                    </MetricBox>
                  </Grid>
                  <Grid item xs={4}>
                    <MetricBox>
                      <Typography variant="h4" color="warning.main" sx={{ fontWeight: 700 }}>
                        {result.efficiency}%
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Efficiency
                      </Typography>
                    </MetricBox>
                  </Grid>
                </Grid>

                <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                  Optimal Build Mix
                </Typography>
                
                {result.robots.map((robot, index) => (
                  <ResultCard key={robot.id} elevation={0}>
                    <CardContent sx={{ py: 1.5 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                            {robot.name}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            {robot.quantity} units
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            label={`$${robot.cost}`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                          <Chip
                            label={`${robot.time}h`}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </Box>
                    </CardContent>
                  </ResultCard>
                ))}

                {result.constraints.length > 0 && (
                  <Alert severity="info" sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Constraints Applied
                    </Typography>
                    {result.constraints.map((constraint, index) => (
                      <Typography key={index} variant="caption" display="block">
                        • {constraint}
                      </Typography>
                    ))}
                  </Alert>
                )}
              </motion.div>
            </AnimatePresence>
          )}

          {!result && !optimizing && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <InfoOutlined sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                Configure optimization parameters and click optimize to see results
              </Typography>
            </Box>
          )}
        </Grid>
      </Grid>

      {result && radarData.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
            Performance Metrics
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData}>
                <PolarGrid strokeDasharray="3 3" />
                <PolarAngleAxis dataKey="metric" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
              </RadarChart>
            </ResponsiveContainer>
          </Box>
        </Box>
      )}
    </OptimizerContainer>
  );
};

export default AssemblyOptimizer;