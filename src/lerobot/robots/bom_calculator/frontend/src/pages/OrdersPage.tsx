import React, { useState } from 'react';
import { Box, Container, Grid } from '@mui/material';
import OrderGenerator from '../components/Orders/OrderGenerator';
import OrderPreview from '../components/Orders/OrderPreview';
import SupplierGrouping from '../components/Orders/SupplierGrouping';
import OrderHistory from '../components/Orders/OrderHistory';

const OrdersPage: React.FC = () => {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);

  return (
    <Container maxWidth={false}>
      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <OrderGenerator 
            onGenerate={(order) => {
              setSelectedOrder(order);
              setPreviewOpen(true);
            }}
          />
        </Grid>
        
        <Grid item xs={12} lg={6}>
          <SupplierGrouping />
        </Grid>
        
        <Grid item xs={12}>
          <OrderHistory 
            onViewOrder={(orderId) => {
              // Fetch order details and open preview
              setPreviewOpen(true);
            }}
          />
        </Grid>
      </Grid>
      
      <OrderPreview
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        order={selectedOrder}
        onConfirm={() => {
          // Handle order confirmation
          setPreviewOpen(false);
        }}
      />
    </Container>
  );
};

export default OrdersPage;