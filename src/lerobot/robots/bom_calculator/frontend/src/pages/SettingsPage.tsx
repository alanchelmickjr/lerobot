import React, { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
} from '@mui/material';
import { Save, RestartAlt, CloudUpload } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const SettingsContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(2),
  marginBottom: theme.spacing(3),
}));

const SectionTitle = styled(Typography)(({ theme }) => ({
  fontWeight: 600,
  marginBottom: theme.spacing(2),
  color: theme.palette.primary.main,
}));

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState({
    companyName: 'LeRobot Inc.',
    email: 'admin@lerobot.com',
    currency: 'USD',
    taxRate: 10,
    defaultLeadTime: 7,
    lowStockThreshold: 10,
    autoSync: true,
    darkMode: false,
    notifications: true,
    emailAlerts: true,
    exportFormat: 'csv',
    apiEndpoint: 'http://localhost:8000',
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    // Save settings to backend
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleReset = () => {
    // Reset to default settings
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Configure your BOM Calculator preferences
        </Typography>
      </Box>

      {saved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">Company Information</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Company Name"
              value={settings.companyName}
              onChange={(e) => setSettings({ ...settings, companyName: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={settings.email}
              onChange={(e) => setSettings({ ...settings, email: e.target.value })}
            />
          </Grid>
        </Grid>
      </SettingsContainer>

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">System Configuration</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Currency</InputLabel>
              <Select
                value={settings.currency}
                onChange={(e) => setSettings({ ...settings, currency: e.target.value })}
                label="Currency"
              >
                <MenuItem value="USD">USD ($)</MenuItem>
                <MenuItem value="EUR">EUR (€)</MenuItem>
                <MenuItem value="GBP">GBP (£)</MenuItem>
                <MenuItem value="JPY">JPY (¥)</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Tax Rate (%)"
              type="number"
              value={settings.taxRate}
              onChange={(e) => setSettings({ ...settings, taxRate: Number(e.target.value) })}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Default Lead Time (days)"
              type="number"
              value={settings.defaultLeadTime}
              onChange={(e) => setSettings({ ...settings, defaultLeadTime: Number(e.target.value) })}
            />
          </Grid>
        </Grid>
      </SettingsContainer>

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">Inventory Settings</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Typography gutterBottom>
              Low Stock Threshold: {settings.lowStockThreshold} units
            </Typography>
            <Slider
              value={settings.lowStockThreshold}
              onChange={(e, value) => setSettings({ ...settings, lowStockThreshold: value as number })}
              min={1}
              max={50}
              valueLabelDisplay="auto"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.autoSync}
                  onChange={(e) => setSettings({ ...settings, autoSync: e.target.checked })}
                />
              }
              label="Auto-sync inventory data"
            />
          </Grid>
        </Grid>
      </SettingsContainer>

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">Notifications</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={(e) => setSettings({ ...settings, notifications: e.target.checked })}
                />
              }
              label="Enable in-app notifications"
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.emailAlerts}
                  onChange={(e) => setSettings({ ...settings, emailAlerts: e.target.checked })}
                />
              }
              label="Enable email alerts"
            />
          </Grid>
        </Grid>
      </SettingsContainer>

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">Export Settings</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Default Export Format</InputLabel>
              <Select
                value={settings.exportFormat}
                onChange={(e) => setSettings({ ...settings, exportFormat: e.target.value })}
                label="Default Export Format"
              >
                <MenuItem value="csv">CSV</MenuItem>
                <MenuItem value="excel">Excel</MenuItem>
                <MenuItem value="json">JSON</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </SettingsContainer>

      <SettingsContainer elevation={0}>
        <SectionTitle variant="h6">API Configuration</SectionTitle>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="API Endpoint"
              value={settings.apiEndpoint}
              onChange={(e) => setSettings({ ...settings, apiEndpoint: e.target.value })}
              helperText="Backend API URL for data synchronization"
            />
          </Grid>
        </Grid>
      </SettingsContainer>

      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          startIcon={<RestartAlt />}
          onClick={handleReset}
        >
          Reset to Default
        </Button>
        <Button
          variant="contained"
          startIcon={<Save />}
          onClick={handleSave}
        >
          Save Settings
        </Button>
      </Box>
    </Container>
  );
};

export default SettingsPage;