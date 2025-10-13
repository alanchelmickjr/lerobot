import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Divider,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  Build,
  Calculate,
  TrendingUp,
  Warning,
  CheckCircle,
  Info,
  Add,
  Remove,
  Refresh,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';
import TouchNumberInput from '../Common/TouchNumberInput';

interface Robot {
  id: string;
  name: string;
  model: string;
  bom: { partId: string; quantity: number }[];
}

interface AssemblyCalculation {
  robotId: string;
  robotName: string;
  targetQuantity: number;
  feasibleQuantity: number;
  bottleneckParts: string[];
  totalCost: number;
  buildTime: number;
  requiredParts: { partId: string; required: number; available: number }[];
}

interface AssemblyCalculatorProps {
  robots?: Robot[];
  inventory?: any[];
  onCalculate?: (calculation: AssemblyCalculation) => void;
}

const CalculatorContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
}));

const ResultCard = styled(Card)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  border: `1px solid ${theme.palette.divider}`,
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const StatBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.03)',
  textAlign: 'center',
}));

const PartRequirementChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  borderRadius: theme.spacing(1),
  fontWeight: 500,
}));

const mockRobots: Robot[] = [
  {
    id: '1',
    name: 'Koch v1.1',
    model: 'koch_v1_1',
    bom: [
      { partId: 'XL320', quantity: 6 },
      { partId: 'U2D2', quantity: 1 },
      { partId: 'Frame-01', quantity: 4 },
    ],
  },
  {
    id: '2',
    name: 'SO-100',
    model: 'so100',
    bom: [
      { partId: 'XL430', quantity: 4 },
      { partId: 'Controller-01', quantity: 1 },
      { partId: 'Gripper-01', quantity: 1 },
    ],
  },
];

const AssemblyCalculator: React.FC<AssemblyCalculatorProps> = ({
  robots = mockRobots,
  inventory = [],
  onCalculate,
}) => {
  const [selectedRobot, setSelectedRobot] = useState<string>('');
  const [targetQuantity, setTargetQuantity] = useState<number>(1);
  const [calculation, setCalculation] = useState<AssemblyCalculation | null>(null);
  const [calculating, setCalculating] = useState(false);
  const [buildScenarios, setBuildScenarios] = useState<any[]>([]);

  const handleCalculate = () => {
    if (!selectedRobot) return;

    setCalculating(true);
    
    // Simulate calculation
    setTimeout(() => {
      const robot = robots.find(r => r.id === selectedRobot);
      if (!robot) return;

      // Mock calculation result
      const result: AssemblyCalculation = {
        robotId: robot.id,
        robotName: robot.name,
        targetQuantity,
        feasibleQuantity: Math.min(targetQuantity, Math.floor(Math.random() * 10) + 1),
        bottleneckParts: ['XL320', 'Controller-01'],
        totalCost: targetQuantity * 450.99,
        buildTime: targetQuantity * 2.5,
        requiredParts: robot.bom.map(part => ({
          partId: part.partId,
          required: part.quantity * targetQuantity,
          available: Math.floor(Math.random() * 50) + 10,
        })),
      };

      setCalculation(result);
      
      // Generate build scenarios
      const scenarios = [
        { quantity: 1, time: 2.5, cost: 450.99, feasible: true },
        { quantity: 5, time: 12.5, cost: 2254.95, feasible: true },
        { quantity: 10, time: 25, cost: 4509.90, feasible: false },
      ];
      setBuildScenarios(scenarios);

      if (onCalculate) {
        onCalculate(result);
      }

      setCalculating(false);
    }, 1500);
  };

  const getStatusColor = (feasible: number, target: number) => {
    const ratio = feasible / target;
    if (ratio >= 1) return 'success';
    if (ratio >= 0.5) return 'warning';
    return 'error';
  };

  const getStatusIcon = (feasible: number, target: number) => {
    const ratio = feasible / target;
    if (ratio >= 1) return <CheckCircle sx={{ color: 'success.main' }} />;
    if (ratio >= 0.5) return <Warning sx={{ color: 'warning.main' }} />;
    return <Warning sx={{ color: 'error.main' }} />;
  };

  return (
    <CalculatorContainer elevation={0}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Build sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Assembly Calculator
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Calculate robot assembly feasibility and requirements
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth variant="outlined" sx={{ mb: 3 }}>
            <InputLabel>Select Robot Model</InputLabel>
            <Select
              value={selectedRobot}
              onChange={(e) => setSelectedRobot(e.target.value)}
              label="Select Robot Model"
            >
              <MenuItem value="">
                <em>None</em>
              </MenuItem>
              {robots.map((robot) => (
                <MenuItem key={robot.id} value={robot.id}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography>{robot.name}</Typography>
                    <Chip label={robot.model} size="small" variant="outlined" />
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Target Quantity
            </Typography>
            <TouchNumberInput
              value={targetQuantity}
              onChange={setTargetQuantity}
              min={1}
              max={100}
              step={1}
              size="medium"
              showSlider
              quickValues={[1, 5, 10, 25]}
            />
          </Box>

          <Button
            fullWidth
            variant="contained"
            size="large"
            startIcon={calculating ? null : <Calculate />}
            onClick={handleCalculate}
            disabled={!selectedRobot || calculating}
            sx={{
              py: 2,
              borderRadius: 2,
              fontSize: '1.1rem',
              fontWeight: 600,
            }}
          >
            {calculating ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <LinearProgress sx={{ width: 100 }} />
                Calculating...
              </Box>
            ) : (
              'Calculate Assembly'
            )}
          </Button>
        </Grid>

        <Grid item xs={12} md={6}>
          {calculation && (
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <ResultCard elevation={0}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        Assembly Result
                      </Typography>
                      {getStatusIcon(calculation.feasibleQuantity, calculation.targetQuantity)}
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <StatBox>
                          <Typography variant="h4" color="primary" sx={{ fontWeight: 700 }}>
                            {calculation.feasibleQuantity}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Feasible Units
                          </Typography>
                        </StatBox>
                      </Grid>
                      <Grid item xs={6}>
                        <StatBox>
                          <Typography variant="h4" sx={{ fontWeight: 700 }}>
                            {calculation.targetQuantity}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Target Units
                          </Typography>
                        </StatBox>
                      </Grid>
                    </Grid>

                    <Divider sx={{ my: 2 }} />

                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                        Bottleneck Parts
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                        {calculation.bottleneckParts.map((part) => (
                          <PartRequirementChip
                            key={part}
                            label={part}
                            color="error"
                            size="small"
                            icon={<Warning />}
                          />
                        ))}
                      </Box>
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Total Cost
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600, color: 'success.main' }}>
                          ${calculation.totalCost.toFixed(2)}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Build Time
                        </Typography>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {calculation.buildTime} hrs
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </ResultCard>

                {buildScenarios.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                      Build Scenarios
                    </Typography>
                    {buildScenarios.map((scenario, index) => (
                      <Box
                        key={index}
                        sx={{
                          p: 2,
                          mb: 1,
                          borderRadius: 1,
                          border: 1,
                          borderColor: scenario.feasible ? 'success.main' : 'error.main',
                          backgroundColor: scenario.feasible 
                            ? 'rgba(76, 175, 80, 0.1)' 
                            : 'rgba(244, 67, 54, 0.1)',
                        }}
                      >
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle2">
                            {scenario.quantity} units
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 2 }}>
                            <Chip
                              label={`$${scenario.cost.toFixed(2)}`}
                              size="small"
                              color={scenario.feasible ? 'success' : 'default'}
                            />
                            <Chip
                              label={`${scenario.time} hrs`}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                )}
              </motion.div>
            </AnimatePresence>
          )}

          {!calculation && !calculating && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Info sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
              <Typography variant="body1" color="textSecondary">
                Select a robot model and quantity to calculate assembly feasibility
              </Typography>
            </Box>
          )}
        </Grid>
      </Grid>
    </CalculatorContainer>
  );
};

export default AssemblyCalculator;