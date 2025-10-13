import React from 'react';
import { Container } from '@mui/material';
import Dashboard from '../components/Dashboard/Dashboard';

const HomePage: React.FC = () => {
  return (
    <Container maxWidth={false} sx={{ p: 0 }}>
      <Dashboard />
    </Container>
  );
};

export default HomePage;