import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Checkbox,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ShoppingCart,
  Add,
  Remove,
  CheckCircle,
  NavigateNext,
  NavigateBefore,
  Send,
  Edit,
  Delete,
  LocalShipping,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface OrderItem {
  partId: string;
  partName: string;
  quantity: number;
  unitPrice: number;
  supplier: string;
  leadTime: number;
}

interface OrderGeneratorProps {
  items?: OrderItem[];
  onGenerate?: (order: any) => void;
}

const GeneratorContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
}));

const StepCard = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(2),
}));

const ItemCard = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  background: theme.palette.background.paper,
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(1),
  transition: 'all 0.2s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    boxShadow: theme.shadows[2],
  },
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  padding: theme.spacing(1.5, 3),
  textTransform: 'none',
  fontWeight: 600,
}));

const mockItems: OrderItem[] = [
  {
    partId: 'XL320',
    partName: 'Servo Motor XL320',
    quantity: 15,
    unitPrice: 24.99,
    supplier: 'Robotis',
    leadTime: 5,
  },
  {
    partId: 'U2D2',
    partName: 'USB to Dynamixel',
    quantity: 2,
    unitPrice: 49.99,
    supplier: 'Robotis',
    leadTime: 5,
  },
  {
    partId: 'GRP-01',
    partName: 'Gripper Assembly',
    quantity: 7,
    unitPrice: 89.99,
    supplier: 'Custom Parts Co',
    leadTime: 10,
  },
];

const steps = ['Select Items', 'Configure Order', 'Review & Submit'];

const OrderGenerator: React.FC<OrderGeneratorProps> = ({
  items = mockItems,
  onGenerate,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [orderItems, setOrderItems] = useState<OrderItem[]>(items);
  const [orderConfig, setOrderConfig] = useState({
    priority: 'normal',
    shippingMethod: 'standard',
    notes: '',
    poNumber: `PO-${Date.now()}`,
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setSelectedItems([]);
    setOrderConfig({
      priority: 'normal',
      shippingMethod: 'standard',
      notes: '',
      poNumber: `PO-${Date.now()}`,
    });
  };

  const handleItemToggle = (partId: string) => {
    setSelectedItems((prev) =>
      prev.includes(partId)
        ? prev.filter((id) => id !== partId)
        : [...prev, partId]
    );
  };

  const handleQuantityChange = (partId: string, delta: number) => {
    setOrderItems((prev) =>
      prev.map((item) =>
        item.partId === partId
          ? { ...item, quantity: Math.max(1, item.quantity + delta) }
          : item
      )
    );
  };

  const calculateTotal = () => {
    return orderItems
      .filter((item) => selectedItems.includes(item.partId))
      .reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
  };

  const handleSubmit = () => {
    const order = {
      items: orderItems.filter((item) => selectedItems.includes(item.partId)),
      config: orderConfig,
      total: calculateTotal(),
      timestamp: new Date(),
    };
    
    if (onGenerate) {
      onGenerate(order);
    }
    
    handleNext();
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <StepCard>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Select items to order
            </Typography>
            <List>
              {orderItems.map((item, index) => (
                <ItemCard
                  key={item.partId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Checkbox
                      checked={selectedItems.includes(item.partId)}
                      onChange={() => handleItemToggle(item.partId)}
                    />
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {item.partName}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                        <Chip
                          label={`$${item.unitPrice}`}
                          size="small"
                          color="success"
                          variant="outlined"
                        />
                        <Chip
                          label={item.supplier}
                          size="small"
                          variant="outlined"
                        />
                        <Chip
                          label={`${item.leadTime} days`}
                          size="small"
                          icon={<LocalShipping />}
                          variant="outlined"
                        />
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(item.partId, -1)}
                        disabled={item.quantity <= 1}
                      >
                        <Remove />
                      </IconButton>
                      <Typography
                        sx={{
                          minWidth: 40,
                          textAlign: 'center',
                          fontWeight: 600,
                        }}
                      >
                        {item.quantity}
                      </Typography>
                      <IconButton
                        size="small"
                        onClick={() => handleQuantityChange(item.partId, 1)}
                      >
                        <Add />
                      </IconButton>
                    </Box>
                  </Box>
                </ItemCard>
              ))}
            </List>
          </StepCard>
        );

      case 1:
        return (
          <StepCard>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Configure order details
            </Typography>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                fullWidth
                label="Purchase Order Number"
                value={orderConfig.poNumber}
                onChange={(e) =>
                  setOrderConfig({ ...orderConfig, poNumber: e.target.value })
                }
                variant="outlined"
              />
              
              <FormControl fullWidth variant="outlined">
                <InputLabel>Priority</InputLabel>
                <Select
                  value={orderConfig.priority}
                  onChange={(e) =>
                    setOrderConfig({ ...orderConfig, priority: e.target.value })
                  }
                  label="Priority"
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="normal">Normal</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
              
              <FormControl fullWidth variant="outlined">
                <InputLabel>Shipping Method</InputLabel>
                <Select
                  value={orderConfig.shippingMethod}
                  onChange={(e) =>
                    setOrderConfig({ ...orderConfig, shippingMethod: e.target.value })
                  }
                  label="Shipping Method"
                >
                  <MenuItem value="standard">Standard (5-7 days)</MenuItem>
                  <MenuItem value="express">Express (2-3 days)</MenuItem>
                  <MenuItem value="overnight">Overnight (1 day)</MenuItem>
                </Select>
              </FormControl>
              
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Order Notes"
                value={orderConfig.notes}
                onChange={(e) =>
                  setOrderConfig({ ...orderConfig, notes: e.target.value })
                }
                variant="outlined"
                placeholder="Add any special instructions or notes..."
              />
            </Box>
          </StepCard>
        );

      case 2:
        return (
          <StepCard>
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Review your order
            </Typography>
            
            <Alert severity="info" sx={{ mb: 2 }}>
              Please review your order details before submitting
            </Alert>
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Order Items
              </Typography>
              {orderItems
                .filter((item) => selectedItems.includes(item.partId))
                .map((item) => (
                  <Box
                    key={item.partId}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      py: 1,
                      borderBottom: 1,
                      borderColor: 'divider',
                    }}
                  >
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {item.partName}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {item.quantity} × ${item.unitPrice} = $
                        {(item.quantity * item.unitPrice).toFixed(2)}
                      </Typography>
                    </Box>
                    <Chip
                      label={item.supplier}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                ))}
            </Box>
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Order Configuration
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2">
                  PO Number: <strong>{orderConfig.poNumber}</strong>
                </Typography>
                <Typography variant="body2">
                  Priority: <strong>{orderConfig.priority}</strong>
                </Typography>
                <Typography variant="body2">
                  Shipping: <strong>{orderConfig.shippingMethod}</strong>
                </Typography>
                {orderConfig.notes && (
                  <Typography variant="body2">
                    Notes: <strong>{orderConfig.notes}</strong>
                  </Typography>
                )}
              </Box>
            </Box>
            
            <Divider sx={{ my: 2 }} />
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="h6">Total Amount</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
                ${calculateTotal().toFixed(2)}
              </Typography>
            </Box>
          </StepCard>
        );

      case 3:
        return (
          <StepCard>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CheckCircle sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
              <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                Order Generated Successfully!
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                Your purchase order has been created and is ready to send to suppliers.
              </Typography>
              <ActionButton
                variant="contained"
                onClick={handleReset}
                startIcon={<Add />}
              >
                Create Another Order
              </ActionButton>
            </Box>
          </StepCard>
        );

      default:
        return null;
    }
  };

  return (
    <GeneratorContainer elevation={0}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <ShoppingCart sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Order Generator
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Create purchase orders for missing parts
          </Typography>
        </Box>
      </Box>

      <Stepper activeStep={activeStep} orientation="vertical">
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
            <StepContent>
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeStep}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  {renderStepContent(activeStep)}
                </motion.div>
              </AnimatePresence>
              
              {activeStep < 3 && (
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <ActionButton
                    variant="contained"
                    onClick={activeStep === 2 ? handleSubmit : handleNext}
                    disabled={activeStep === 0 && selectedItems.length === 0}
                    startIcon={activeStep === 2 ? <Send /> : <NavigateNext />}
                  >
                    {activeStep === 2 ? 'Submit Order' : 'Continue'}
                  </ActionButton>
                  <ActionButton
                    variant="outlined"
                    onClick={handleBack}
                    disabled={activeStep === 0}
                    startIcon={<NavigateBefore />}
                  >
                    Back
                  </ActionButton>
                </Box>
              )}
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </GeneratorContainer>
  );
};

export default OrderGenerator;