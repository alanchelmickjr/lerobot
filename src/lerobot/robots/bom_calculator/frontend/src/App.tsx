import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Typography } from '@mui/material';

const App: React.FC = () => {
  const theme = createTheme({
    palette: {
      mode: 'light',
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4">BOM Calculator</Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            Backend API: <a href="http://localhost:8000/api/docs">http://localhost:8000/api/docs</a>
          </Typography>
          <Routes>
            <Route path="/" element={<div>Home Page - Working!</div>} />
            <Route path="/inventory" element={<div>Inventory Page</div>} />
            <Route path="/assembly" element={<div>Assembly Page</div>} />
            <Route path="/orders" element={<div>Orders Page</div>} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App;