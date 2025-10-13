import React, { useState } from 'react';
import { Box, Container } from '@mui/material';
import InventoryGrid from '../components/Inventory/InventoryGrid';
import InventoryFilters from '../components/Inventory/InventoryFilters';
import BulkUpdateDialog from '../components/Inventory/BulkUpdateDialog';
import InventoryExport from '../components/Inventory/InventoryExport';

const InventoryPage: React.FC = () => {
  const [filters, setFilters] = useState({});
  const [bulkUpdateOpen, setBulkUpdateOpen] = useState(false);
  const [selectedItems, setSelectedItems] = useState<any[]>([]);

  return (
    <Container maxWidth={false}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
          <InventoryExport data={[]} />
        </Box>
        
        <InventoryFilters onFilterChange={setFilters} />
        
        <InventoryGrid
          data={[]}
          onUpdate={() => {}}
          onDelete={() => {}}
          onBulkUpdate={(ids, updates) => {
            setBulkUpdateOpen(true);
            setSelectedItems(ids);
          }}
        />
        
        <BulkUpdateDialog
          open={bulkUpdateOpen}
          onClose={() => setBulkUpdateOpen(false)}
          selectedItems={selectedItems}
          onUpdate={() => setBulkUpdateOpen(false)}
        />
      </Box>
    </Container>
  );
};

export default InventoryPage;