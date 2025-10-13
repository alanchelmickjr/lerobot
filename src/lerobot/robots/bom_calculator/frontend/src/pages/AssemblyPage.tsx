import React, { useState } from 'react';
import { Box, Container, Tab, Tabs, Paper } from '@mui/material';
import AssemblyCalculator from '../components/Assembly/AssemblyCalculator';
import BottleneckChart from '../components/Assembly/BottleneckChart';
import AssemblyOptimizer from '../components/Assembly/AssemblyOptimizer';
import PartRequirements from '../components/Assembly/PartRequirements';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const AssemblyPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Container maxWidth={false}>
      <Paper sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Tab label="Assembly Calculator" />
          <Tab label="Bottleneck Analysis" />
          <Tab label="Optimizer" />
          <Tab label="Part Requirements" />
        </Tabs>
        
        <TabPanel value={tabValue} index={0}>
          <AssemblyCalculator />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <BottleneckChart />
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <AssemblyOptimizer />
        </TabPanel>
        
        <TabPanel value={tabValue} index={3}>
          <PartRequirements />
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default AssemblyPage;