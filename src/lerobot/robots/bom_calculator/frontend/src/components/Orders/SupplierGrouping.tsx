import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Badge,
  Tooltip,
  Checkbox,
} from '@mui/material';
import {
  ExpandMore,
  Business,
  ShoppingCart,
  LocalShipping,
  AttachMoney,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface SupplierGroup {
  supplier: string;
  items: {
    partId: string;
    partName: string;
    quantity: number;
    unitPrice: number;
    total: number;
  }[];
  totalAmount: number;
  itemCount: number;
  leadTime: number;
}

interface SupplierGroupingProps {
  groups?: SupplierGroup[];
  onGenerateOrder?: (supplier: string, items: any[]) => void;
}

const GroupingContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
}));

const StyledAccordion = styled(Accordion)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  marginBottom: theme.spacing(2),
  border: `1px solid ${theme.palette.divider}`,
  '&:before': {
    display: 'none',
  },
  '&.Mui-expanded': {
    margin: theme.spacing(2, 0),
  },
}));

const SupplierHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  width: '100%',
}));

const StatBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(1),
  borderRadius: theme.spacing(1),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.03)',
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  textTransform: 'none',
  fontWeight: 600,
}));

const mockGroups: SupplierGroup[] = [
  {
    supplier: 'Robotis',
    items: [
      { partId: 'XL320', partName: 'Servo Motor XL320', quantity: 15, unitPrice: 24.99, total: 374.85 },
      { partId: 'U2D2', partName: 'USB to Dynamixel', quantity: 2, unitPrice: 49.99, total: 99.98 },
      { partId: 'XL430', partName: 'Servo Motor XL430', quantity: 4, unitPrice: 89.99, total: 359.96 },
    ],
    totalAmount: 834.79,
    itemCount: 21,
    leadTime: 5,
  },
  {
    supplier: 'Custom Parts Co',
    items: [
      { partId: 'GRP-01', partName: 'Gripper Assembly', quantity: 7, unitPrice: 89.99, total: 629.93 },
      { partId: 'FRAME-01', partName: 'Frame Component', quantity: 10, unitPrice: 15.99, total: 159.90 },
    ],
    totalAmount: 789.83,
    itemCount: 17,
    leadTime: 10,
  },
  {
    supplier: 'Tech Supplier Inc',
    items: [
      { partId: 'CTRL-01', partName: 'Control Board', quantity: 5, unitPrice: 149.99, total: 749.95 },
      { partId: 'SENS-01', partName: 'Sensor Package', quantity: 8, unitPrice: 34.99, total: 279.92 },
    ],
    totalAmount: 1029.87,
    itemCount: 13,
    leadTime: 7,
  },
];

const SupplierGrouping: React.FC<SupplierGroupingProps> = ({
  groups = mockGroups,
  onGenerateOrder,
}) => {
  const [expandedPanels, setExpandedPanels] = useState<string[]>([]);
  const [selectedItems, setSelectedItems] = useState<{ [key: string]: string[] }>({});

  const handlePanelChange = (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedPanels(isExpanded 
      ? [...expandedPanels, panel]
      : expandedPanels.filter(p => p !== panel)
    );
  };

  const handleItemToggle = (supplier: string, partId: string) => {
    setSelectedItems(prev => ({
      ...prev,
      [supplier]: prev[supplier]?.includes(partId)
        ? prev[supplier].filter(id => id !== partId)
        : [...(prev[supplier] || []), partId],
    }));
  };

  const handleGenerateOrder = (supplier: string) => {
    const group = groups.find(g => g.supplier === supplier);
    if (group && onGenerateOrder) {
      const itemsToOrder = selectedItems[supplier]?.length > 0
        ? group.items.filter(item => selectedItems[supplier].includes(item.partId))
        : group.items;
      onGenerateOrder(supplier, itemsToOrder);
    }
  };

  const getTotalSelected = (supplier: string) => {
    const group = groups.find(g => g.supplier === supplier);
    if (!group || !selectedItems[supplier]?.length) return 0;
    
    return group.items
      .filter(item => selectedItems[supplier].includes(item.partId))
      .reduce((sum, item) => sum + item.total, 0);
  };

  return (
    <GroupingContainer elevation={0}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Business sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Supplier Grouping
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Group orders by supplier for efficient purchasing
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 2, mb: 3 }}>
        <StatBox>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
            {groups.length}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Suppliers
          </Typography>
        </StatBox>
        <StatBox>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'success.main' }}>
            {groups.reduce((sum, g) => sum + g.itemCount, 0)}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Total Items
          </Typography>
        </StatBox>
        <StatBox>
          <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
            ${groups.reduce((sum, g) => sum + g.totalAmount, 0).toFixed(0)}
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Total Value
          </Typography>
        </StatBox>
        <StatBox>
          <Typography variant="h4" sx={{ fontWeight: 700 }}>
            {Math.max(...groups.map(g => g.leadTime))}d
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Max Lead Time
          </Typography>
        </StatBox>
      </Box>

      {groups.map((group, index) => (
        <motion.div
          key={group.supplier}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
        >
          <StyledAccordion
            expanded={expandedPanels.includes(group.supplier)}
            onChange={handlePanelChange(group.supplier)}
          >
            <AccordionSummary expandIcon={<ExpandMore />}>
              <SupplierHeader>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Business sx={{ color: 'primary.main' }} />
                  <Box>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {group.supplier}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                      <Chip
                        label={`${group.itemCount} items`}
                        size="small"
                        variant="outlined"
                      />
                      <Chip
                        label={`${group.leadTime} days`}
                        size="small"
                        icon={<LocalShipping />}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mr: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    ${group.totalAmount.toFixed(2)}
                  </Typography>
                  <Badge
                    badgeContent={selectedItems[group.supplier]?.length || 0}
                    color="primary"
                  >
                    <ShoppingCart />
                  </Badge>
                </Box>
              </SupplierHeader>
            </AccordionSummary>
            
            <AccordionDetails>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell padding="checkbox"></TableCell>
                      <TableCell>Part Number</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="center">Quantity</TableCell>
                      <TableCell align="right">Unit Price</TableCell>
                      <TableCell align="right">Total</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {group.items.map((item) => (
                      <TableRow
                        key={item.partId}
                        sx={{
                          backgroundColor: selectedItems[group.supplier]?.includes(item.partId)
                            ? 'action.selected'
                            : 'transparent',
                        }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={selectedItems[group.supplier]?.includes(item.partId) || false}
                            onChange={() => handleItemToggle(group.supplier, item.partId)}
                          />
                        </TableCell>
                        <TableCell>{item.partId}</TableCell>
                        <TableCell>{item.partName}</TableCell>
                        <TableCell align="center">{item.quantity}</TableCell>
                        <TableCell align="right">${item.unitPrice.toFixed(2)}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600 }}>
                          ${item.total.toFixed(2)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Box>
                  {selectedItems[group.supplier]?.length > 0 && (
                    <Typography variant="body2" color="textSecondary">
                      Selected: ${getTotalSelected(group.supplier).toFixed(2)}
                    </Typography>
                  )}
                </Box>
                <ActionButton
                  variant="contained"
                  startIcon={<ShoppingCart />}
                  onClick={() => handleGenerateOrder(group.supplier)}
                >
                  Generate Order
                  {selectedItems[group.supplier]?.length > 0 && 
                    ` (${selectedItems[group.supplier].length})`
                  }
                </ActionButton>
              </Box>
            </AccordionDetails>
          </StyledAccordion>
        </motion.div>
      ))}

      <Box sx={{ mt: 3, p: 2, borderRadius: 1, bgcolor: 'background.default' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Info sx={{ color: 'info.main', fontSize: 20 }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            Supplier Optimization Tips
          </Typography>
        </Box>
        <Typography variant="caption" color="textSecondary">
          • Combine orders from the same supplier to reduce shipping costs
          <br />
          • Consider lead times when planning assembly schedules
          <br />
          • Check for bulk discounts on larger quantities
        </Typography>
      </Box>
    </GroupingContainer>
  );
};

export default SupplierGrouping;