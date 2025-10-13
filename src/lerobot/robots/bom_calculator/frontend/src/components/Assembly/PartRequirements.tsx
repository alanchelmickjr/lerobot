import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Tooltip,
  Button,
  Collapse,
  Alert,
  Badge,
} from '@mui/material';
import {
  Extension,
  ExpandMore,
  ExpandLess,
  CheckCircle,
  Warning,
  Error,
  ShoppingCart,
  InfoOutlined,
  FilterList,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface PartRequirement {
  partId: string;
  partName: string;
  category: string;
  requiredQuantity: number;
  availableQuantity: number;
  shortageQuantity: number;
  unitPrice: number;
  totalCost: number;
  status: 'available' | 'partial' | 'shortage';
  robots: { name: string; quantity: number }[];
}

interface PartRequirementsProps {
  requirements?: PartRequirement[];
  onOrderParts?: (partIds: string[]) => void;
}

const RequirementsContainer = styled(Paper)(({ theme }) => ({
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  overflow: 'hidden',
}));

const StyledTableContainer = styled(TableContainer)(({ theme }) => ({
  '& .MuiTable-root': {
    borderCollapse: 'separate',
    borderSpacing: 0,
  },
  '& .MuiTableHead-root': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.03)',
    '& .MuiTableCell-head': {
      fontWeight: 600,
      borderBottom: `2px solid ${theme.palette.primary.main}`,
    },
  },
  '& .MuiTableBody-root .MuiTableRow-root': {
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
  },
}));

const StatusChip = styled(Chip)(({ theme }) => ({
  fontWeight: 600,
  borderRadius: theme.spacing(1),
}));

const ExpandableRow = styled(TableRow)(({ theme }) => ({
  '& > *': {
    borderBottom: 'unset',
  },
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const DetailBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.02)'
    : 'rgba(0, 0, 0, 0.01)',
  borderRadius: theme.spacing(1),
}));

const mockRequirements: PartRequirement[] = [
  {
    partId: 'XL320',
    partName: 'Servo Motor XL320',
    category: 'Motors',
    requiredQuantity: 60,
    availableQuantity: 45,
    shortageQuantity: 15,
    unitPrice: 24.99,
    totalCost: 1499.40,
    status: 'partial',
    robots: [
      { name: 'Koch v1.1', quantity: 30 },
      { name: 'Koch v1.2', quantity: 30 },
    ],
  },
  {
    partId: 'U2D2',
    partName: 'USB to Dynamixel',
    category: 'Controllers',
    requiredQuantity: 10,
    availableQuantity: 8,
    shortageQuantity: 2,
    unitPrice: 49.99,
    totalCost: 499.90,
    status: 'partial',
    robots: [
      { name: 'Koch v1.1', quantity: 5 },
      { name: 'Koch v1.2', quantity: 5 },
    ],
  },
  {
    partId: 'FRAME-01',
    partName: 'Frame Component',
    category: 'Structural',
    requiredQuantity: 20,
    availableQuantity: 25,
    shortageQuantity: 0,
    unitPrice: 15.99,
    totalCost: 319.80,
    status: 'available',
    robots: [
      { name: 'Koch v1.1', quantity: 20 },
    ],
  },
];

const PartRequirements: React.FC<PartRequirementsProps> = ({
  requirements = mockRequirements,
  onOrderParts,
}) => {
  const [expandedRows, setExpandedRows] = useState<string[]>([]);
  const [selectedParts, setSelectedParts] = useState<string[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const handleRowExpand = (partId: string) => {
    setExpandedRows((prev) =>
      prev.includes(partId)
        ? prev.filter((id) => id !== partId)
        : [...prev, partId]
    );
  };

  const handleSelectPart = (partId: string) => {
    setSelectedParts((prev) =>
      prev.includes(partId)
        ? prev.filter((id) => id !== partId)
        : [...prev, partId]
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'partial':
        return <Warning sx={{ fontSize: 16 }} />;
      case 'shortage':
        return <Error sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string): any => {
    switch (status) {
      case 'available':
        return 'success';
      case 'partial':
        return 'warning';
      case 'shortage':
        return 'error';
      default:
        return 'default';
    }
  };

  const filteredRequirements = requirements.filter((req) =>
    filterStatus === 'all' || req.status === filterStatus
  );

  const totalShortage = requirements.reduce((sum, req) => sum + req.shortageQuantity, 0);
  const totalCost = requirements.reduce((sum, req) => sum + req.totalCost, 0);

  return (
    <RequirementsContainer elevation={0}>
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Extension sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Part Requirements
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Detailed parts breakdown for assembly
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Badge badgeContent={totalShortage} color="error">
              <Tooltip title="Total shortage">
                <IconButton size="small">
                  <Warning />
                </IconButton>
              </Tooltip>
            </Badge>
            <Tooltip title="Filter requirements">
              <IconButton size="small">
                <FilterList />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <StatusChip
            label="All"
            variant={filterStatus === 'all' ? 'filled' : 'outlined'}
            onClick={() => setFilterStatus('all')}
            size="small"
          />
          <StatusChip
            label="Available"
            icon={<CheckCircle />}
            color="success"
            variant={filterStatus === 'available' ? 'filled' : 'outlined'}
            onClick={() => setFilterStatus('available')}
            size="small"
          />
          <StatusChip
            label="Partial"
            icon={<Warning />}
            color="warning"
            variant={filterStatus === 'partial' ? 'filled' : 'outlined'}
            onClick={() => setFilterStatus('partial')}
            size="small"
          />
          <StatusChip
            label="Shortage"
            icon={<Error />}
            color="error"
            variant={filterStatus === 'shortage' ? 'filled' : 'outlined'}
            onClick={() => setFilterStatus('shortage')}
            size="small"
          />
        </Box>
      </Box>

      <StyledTableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell width={40}></TableCell>
              <TableCell>Part Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell align="center">Required</TableCell>
              <TableCell align="center">Available</TableCell>
              <TableCell align="center">Shortage</TableCell>
              <TableCell align="right">Unit Price</TableCell>
              <TableCell align="right">Total Cost</TableCell>
              <TableCell align="center">Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredRequirements.map((req, index) => (
              <React.Fragment key={req.partId}>
                <ExpandableRow
                  onClick={() => handleRowExpand(req.partId)}
                  component={motion.tr}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <TableCell>
                    <IconButton size="small">
                      {expandedRows.includes(req.partId) ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {req.partName}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        #{req.partId}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip label={req.category} size="small" variant="outlined" />
                  </TableCell>
                  <TableCell align="center">
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {req.requiredQuantity}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Typography 
                      variant="body2"
                      color={req.availableQuantity >= req.requiredQuantity ? 'success.main' : 'text.primary'}
                    >
                      {req.availableQuantity}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {req.shortageQuantity > 0 && (
                      <Typography variant="body2" color="error" sx={{ fontWeight: 600 }}>
                        -{req.shortageQuantity}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${req.unitPrice.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      ${req.totalCost.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <StatusChip
                      icon={getStatusIcon(req.status)}
                      label={req.status}
                      color={getStatusColor(req.status)}
                      size="small"
                    />
                  </TableCell>
                </ExpandableRow>
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={9}>
                    <Collapse in={expandedRows.includes(req.partId)} timeout="auto" unmountOnExit>
                      <DetailBox sx={{ margin: 2 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2 }}>
                          Usage Breakdown
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
                          {req.robots.map((robot) => (
                            <Chip
                              key={robot.name}
                              label={`${robot.name}: ${robot.quantity} units`}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                        {req.shortageQuantity > 0 && (
                          <Alert severity="warning" sx={{ mt: 2 }}>
                            <Typography variant="body2">
                              Need to order {req.shortageQuantity} more units to meet requirements
                            </Typography>
                          </Alert>
                        )}
                      </DetailBox>
                    </Collapse>
                  </TableCell>
                </TableRow>
              </React.Fragment>
            ))}
          </TableBody>
        </Table>
      </StyledTableContainer>

      <Box sx={{ p: 3, borderTop: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="subtitle2" color="textSecondary">
            Total Cost
          </Typography>
          <Typography variant="h5" sx={{ fontWeight: 700, color: 'primary.main' }}>
            ${totalCost.toFixed(2)}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<ShoppingCart />}
          onClick={() => onOrderParts && onOrderParts(selectedParts)}
          disabled={totalShortage === 0}
          sx={{ borderRadius: 2 }}
        >
          Order Missing Parts ({totalShortage})
        </Button>
      </Box>
    </RequirementsContainer>
  );
};

export default PartRequirements;