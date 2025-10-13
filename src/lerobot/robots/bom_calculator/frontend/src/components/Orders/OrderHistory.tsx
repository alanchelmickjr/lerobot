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
  TablePagination,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  Tooltip,
} from '@mui/material';
import {
  History,
  Search,
  FilterList,
  MoreVert,
  Visibility,
  Download,
  Email,
  CheckCircle,
  HourglassEmpty,
  LocalShipping,
  Cancel,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface Order {
  id: string;
  poNumber: string;
  date: Date;
  supplier: string;
  itemCount: number;
  totalAmount: number;
  status: 'pending' | 'confirmed' | 'shipped' | 'delivered' | 'cancelled';
  leadTime: number;
}

interface OrderHistoryProps {
  orders?: Order[];
  onViewOrder?: (orderId: string) => void;
  onExportOrder?: (orderId: string) => void;
}

const HistoryContainer = styled(Paper)(({ theme }) => ({
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  overflow: 'hidden',
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  borderBottom: `1px solid ${theme.palette.divider}`,
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
}));

const SearchField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(2),
    backgroundColor: theme.palette.background.paper,
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const StatusChip = styled(Chip)(({ theme }) => ({
  fontWeight: 600,
  borderRadius: theme.spacing(1),
}));

const mockOrders: Order[] = [
  {
    id: '1',
    poNumber: 'PO-2024-001',
    date: new Date('2024-01-15'),
    supplier: 'Robotis',
    itemCount: 3,
    totalAmount: 547.31,
    status: 'delivered',
    leadTime: 5,
  },
  {
    id: '2',
    poNumber: 'PO-2024-002',
    date: new Date('2024-01-20'),
    supplier: 'Custom Parts Co',
    itemCount: 2,
    totalAmount: 789.83,
    status: 'shipped',
    leadTime: 10,
  },
  {
    id: '3',
    poNumber: 'PO-2024-003',
    date: new Date('2024-01-25'),
    supplier: 'Tech Supplier Inc',
    itemCount: 5,
    totalAmount: 1234.56,
    status: 'confirmed',
    leadTime: 7,
  },
  {
    id: '4',
    poNumber: 'PO-2024-004',
    date: new Date('2024-01-28'),
    supplier: 'Robotis',
    itemCount: 4,
    totalAmount: 890.12,
    status: 'pending',
    leadTime: 5,
  },
  {
    id: '5',
    poNumber: 'PO-2024-005',
    date: new Date('2024-01-10'),
    supplier: 'Direct Factory',
    itemCount: 1,
    totalAmount: 234.56,
    status: 'cancelled',
    leadTime: 3,
  },
];

const OrderHistory: React.FC<OrderHistoryProps> = ({
  orders = mockOrders,
  onViewOrder,
  onExportOrder,
}) => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedOrder, setSelectedOrder] = useState<string | null>(null);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, orderId: string) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
    setSelectedOrder(orderId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedOrder(null);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <HourglassEmpty sx={{ fontSize: 16 }} />;
      case 'confirmed':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'shipped':
        return <LocalShipping sx={{ fontSize: 16 }} />;
      case 'delivered':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'cancelled':
        return <Cancel sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string): any => {
    switch (status) {
      case 'pending':
        return 'warning';
      case 'confirmed':
        return 'info';
      case 'shipped':
        return 'primary';
      case 'delivered':
        return 'success';
      case 'cancelled':
        return 'error';
      default:
        return 'default';
    }
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.poNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          order.supplier.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || order.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const paginatedOrders = filteredOrders.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <HistoryContainer elevation={0}>
      <HeaderBox>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <History sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Order History
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Track and manage all purchase orders
              </Typography>
            </Box>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <SearchField
            placeholder="Search orders..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            size="small"
            sx={{ flex: 1, minWidth: 200 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <StatusChip
              label="All"
              variant={filterStatus === 'all' ? 'filled' : 'outlined'}
              onClick={() => setFilterStatus('all')}
              size="small"
            />
            <StatusChip
              label="Pending"
              icon={<HourglassEmpty />}
              color="warning"
              variant={filterStatus === 'pending' ? 'filled' : 'outlined'}
              onClick={() => setFilterStatus('pending')}
              size="small"
            />
            <StatusChip
              label="Shipped"
              icon={<LocalShipping />}
              color="primary"
              variant={filterStatus === 'shipped' ? 'filled' : 'outlined'}
              onClick={() => setFilterStatus('shipped')}
              size="small"
            />
            <StatusChip
              label="Delivered"
              icon={<CheckCircle />}
              color="success"
              variant={filterStatus === 'delivered' ? 'filled' : 'outlined'}
              onClick={() => setFilterStatus('delivered')}
              size="small"
            />
          </Box>
        </Box>
      </HeaderBox>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order Number</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Supplier</TableCell>
              <TableCell align="center">Items</TableCell>
              <TableCell align="right">Total Amount</TableCell>
              <TableCell align="center">Lead Time</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedOrders.map((order, index) => (
              <StyledTableRow
                key={order.id}
                component={motion.tr}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => onViewOrder && onViewOrder(order.id)}
              >
                <TableCell>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {order.poNumber}
                  </Typography>
                </TableCell>
                <TableCell>{order.date.toLocaleDateString()}</TableCell>
                <TableCell>{order.supplier}</TableCell>
                <TableCell align="center">
                  <Chip label={order.itemCount} size="small" variant="outlined" />
                </TableCell>
                <TableCell align="right">
                  <Typography sx={{ fontWeight: 600 }}>
                    ${order.totalAmount.toFixed(2)}
                  </Typography>
                </TableCell>
                <TableCell align="center">{order.leadTime} days</TableCell>
                <TableCell align="center">
                  <StatusChip
                    icon={getStatusIcon(order.status)}
                    label={order.status}
                    color={getStatusColor(order.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    onClick={(e) => handleMenuOpen(e, order.id)}
                  >
                    <MoreVert />
                  </IconButton>
                </TableCell>
              </StyledTableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={filteredOrders.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[5, 10, 25]}
      />

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => {
          if (selectedOrder && onViewOrder) {
            onViewOrder(selectedOrder);
          }
          handleMenuClose();
        }}>
          <Visibility sx={{ mr: 1, fontSize: 20 }} /> View Details
        </MenuItem>
        <MenuItem onClick={() => {
          if (selectedOrder && onExportOrder) {
            onExportOrder(selectedOrder);
          }
          handleMenuClose();
        }}>
          <Download sx={{ mr: 1, fontSize: 20 }} /> Download PDF
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Email sx={{ mr: 1, fontSize: 20 }} /> Email Supplier
        </MenuItem>
      </Menu>
    </HistoryContainer>
  );
};

export default OrderHistory;