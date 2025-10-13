import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Divider,
  IconButton,
} from '@mui/material';
import {
  Close,
  Print,
  Email,
  Download,
  CheckCircle,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface OrderPreviewProps {
  open: boolean;
  onClose: () => void;
  order: any;
  onConfirm?: () => void;
  onPrint?: () => void;
  onEmail?: () => void;
  onDownload?: () => void;
}

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    borderRadius: theme.spacing(2),
    maxWidth: 800,
    width: '100%',
  },
}));

const PreviewHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  background: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
}));

const InfoSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  marginBottom: theme.spacing(2),
}));

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  textTransform: 'none',
  fontWeight: 600,
}));

const mockOrder = {
  poNumber: 'PO-2024-001',
  date: new Date(),
  supplier: 'Robotis',
  items: [
    {
      partId: 'XL320',
      partName: 'Servo Motor XL320',
      quantity: 15,
      unitPrice: 24.99,
      total: 374.85,
    },
    {
      partId: 'U2D2',
      partName: 'USB to Dynamixel',
      quantity: 2,
      unitPrice: 49.99,
      total: 99.98,
    },
  ],
  subtotal: 474.83,
  tax: 47.48,
  shipping: 25.00,
  total: 547.31,
  status: 'pending',
  priority: 'high',
  shippingMethod: 'express',
  estimatedDelivery: '2-3 business days',
  notes: 'Please ensure proper packaging for servo motors',
};

const OrderPreview: React.FC<OrderPreviewProps> = ({
  open,
  onClose,
  order = mockOrder,
  onConfirm,
  onPrint,
  onEmail,
  onDownload,
}) => {
  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      TransitionComponent={motion.div}
      TransitionProps={{
        initial: { opacity: 0, scale: 0.9 },
        animate: { opacity: 1, scale: 1 },
        exit: { opacity: 0, scale: 0.9 },
      }}
    >
      <PreviewHeader>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Purchase Order Preview
            </Typography>
            <Typography variant="body2" sx={{ opacity: 0.9 }}>
              {order.poNumber}
            </Typography>
          </Box>
          <IconButton onClick={onClose} sx={{ color: 'inherit' }}>
            <Close />
          </IconButton>
        </Box>
      </PreviewHeader>

      <DialogContent sx={{ p: 3 }}>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 3 }}>
          <InfoSection>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Order Information
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                Date: <strong>{order.date.toLocaleDateString()}</strong>
              </Typography>
              <Typography variant="body2">
                Status: <Chip label={order.status} size="small" color="warning" />
              </Typography>
              <Typography variant="body2">
                Priority: <Chip label={order.priority} size="small" color="error" />
              </Typography>
            </Box>
          </InfoSection>

          <InfoSection>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Supplier Details
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Typography variant="body2">
                Supplier: <strong>{order.supplier}</strong>
              </Typography>
              <Typography variant="body2">
                Shipping: <strong>{order.shippingMethod}</strong>
              </Typography>
              <Typography variant="body2">
                Est. Delivery: <strong>{order.estimatedDelivery}</strong>
              </Typography>
            </Box>
          </InfoSection>
        </Box>

        <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
          Order Items
        </Typography>
        
        <TableContainer component={Paper} variant="outlined" sx={{ mb: 3 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Part Number</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="center">Quantity</TableCell>
                <TableCell align="right">Unit Price</TableCell>
                <TableCell align="right">Total</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {order.items.map((item: any) => (
                <TableRow key={item.partId}>
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

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3 }}>
          <Box sx={{ width: 300 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Subtotal:</Typography>
              <Typography variant="body2">${order.subtotal.toFixed(2)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Tax (10%):</Typography>
              <Typography variant="body2">${order.tax.toFixed(2)}</Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2">Shipping:</Typography>
              <Typography variant="body2">${order.shipping.toFixed(2)}</Typography>
            </Box>
            <Divider sx={{ my: 1 }} />
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="h6">Total:</Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
                ${order.total.toFixed(2)}
              </Typography>
            </Box>
          </Box>
        </Box>

        {order.notes && (
          <InfoSection>
            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Order Notes
            </Typography>
            <Typography variant="body2">{order.notes}</Typography>
          </InfoSection>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, gap: 1 }}>
        <ActionButton
          variant="outlined"
          onClick={onPrint}
          startIcon={<Print />}
        >
          Print
        </ActionButton>
        <ActionButton
          variant="outlined"
          onClick={onEmail}
          startIcon={<Email />}
        >
          Email
        </ActionButton>
        <ActionButton
          variant="outlined"
          onClick={onDownload}
          startIcon={<Download />}
        >
          Download PDF
        </ActionButton>
        <Box sx={{ flex: 1 }} />
        <ActionButton
          variant="outlined"
          onClick={onClose}
          color="inherit"
        >
          Cancel
        </ActionButton>
        <ActionButton
          variant="contained"
          onClick={onConfirm}
          startIcon={<CheckCircle />}
        >
          Confirm Order
        </ActionButton>
      </DialogActions>
    </StyledDialog>
  );
};

export default OrderPreview;