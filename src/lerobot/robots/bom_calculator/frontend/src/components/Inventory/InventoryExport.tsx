import React, { useState } from 'react';
import {
  Button,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  FormGroup,
  Typography,
  Box,
  Chip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  GetApp,
  Description,
  TableChart,
  Code,
  CloudDownload,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface InventoryExportProps {
  data: any[];
  onExport?: (format: string, options: ExportOptions) => void;
}

interface ExportOptions {
  format: 'csv' | 'excel' | 'json' | 'pdf';
  includeFields: string[];
  dateRange?: { start: Date; end: Date };
  filterEmpty?: boolean;
}

const ExportButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  textTransform: 'none',
  fontWeight: 600,
  padding: theme.spacing(1, 2),
}));

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    borderRadius: theme.spacing(2),
    maxWidth: 500,
    width: '100%',
  },
}));

const FormatOption = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  border: `1px solid ${theme.palette.divider}`,
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.hover,
  },
  '&.selected': {
    borderColor: theme.palette.primary.main,
    backgroundColor: theme.palette.action.selected,
    borderWidth: 2,
  },
}));

const InventoryExport: React.FC<InventoryExportProps> = ({ data, onExport }) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [exportFormat, setExportFormat] = useState<'csv' | 'excel' | 'json' | 'pdf'>('csv');
  const [selectedFields, setSelectedFields] = useState<string[]>([
    'partNumber',
    'name',
    'category',
    'quantity',
    'unitPrice',
    'supplier',
    'location',
    'status',
  ]);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  const availableFields = [
    { key: 'partNumber', label: 'Part Number' },
    { key: 'name', label: 'Name' },
    { key: 'category', label: 'Category' },
    { key: 'quantity', label: 'Quantity' },
    { key: 'minStock', label: 'Min Stock' },
    { key: 'maxStock', label: 'Max Stock' },
    { key: 'unitPrice', label: 'Unit Price' },
    { key: 'supplier', label: 'Supplier' },
    { key: 'location', label: 'Location' },
    { key: 'status', label: 'Status' },
    { key: 'lastUpdated', label: 'Last Updated' },
  ];

  const handleExportClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleQuickExport = (format: 'csv' | 'excel' | 'json') => {
    handleClose();
    performExport(format, selectedFields);
  };

  const handleAdvancedExport = () => {
    handleClose();
    setDialogOpen(true);
  };

  const handleFieldToggle = (field: string) => {
    setSelectedFields((prev) =>
      prev.includes(field)
        ? prev.filter((f) => f !== field)
        : [...prev, field]
    );
  };

  const performExport = async (format: 'csv' | 'excel' | 'json' | 'pdf', fields: string[]) => {
    setExporting(true);
    
    // Simulate export process
    setTimeout(() => {
      const options: ExportOptions = {
        format,
        includeFields: fields,
        filterEmpty: true,
      };

      if (format === 'csv') {
        exportToCSV(data, fields);
      } else if (format === 'json') {
        exportToJSON(data, fields);
      } else if (onExport) {
        onExport(format, options);
      }

      setExporting(false);
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 3000);
    }, 1500);
  };

  const exportToCSV = (items: any[], fields: string[]) => {
    const headers = fields.join(',');
    const rows = items.map((item) =>
      fields.map((field) => {
        const value = item[field];
        return typeof value === 'string' && value.includes(',')
          ? `"${value}"`
          : value;
      }).join(',')
    );
    
    const csv = [headers, ...rows].join('\n');
    downloadFile(csv, 'inventory-export.csv', 'text/csv');
  };

  const exportToJSON = (items: any[], fields: string[]) => {
    const filtered = items.map((item) => {
      const obj: any = {};
      fields.forEach((field) => {
        obj[field] = item[field];
      });
      return obj;
    });
    
    const json = JSON.stringify(filtered, null, 2);
    downloadFile(json, 'inventory-export.json', 'application/json');
  };

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'csv':
        return <TableChart />;
      case 'excel':
        return <Description />;
      case 'json':
        return <Code />;
      case 'pdf':
        return <Description />;
      default:
        return <GetApp />;
    }
  };

  return (
    <>
      <ExportButton
        variant="outlined"
        startIcon={exporting ? null : <GetApp />}
        onClick={handleExportClick}
        disabled={exporting || !data || data.length === 0}
      >
        {exporting ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <LinearProgress sx={{ width: 80 }} />
            <Typography variant="caption">Exporting...</Typography>
          </Box>
        ) : exportSuccess ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircle sx={{ color: 'success.main', fontSize: 20 }} />
            <Typography>Exported!</Typography>
          </Box>
        ) : (
          'Export'
        )}
      </ExportButton>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            borderRadius: 2,
            minWidth: 200,
          },
        }}
      >
        <MenuItem onClick={() => handleQuickExport('csv')}>
          <ListItemIcon>
            <TableChart />
          </ListItemIcon>
          <ListItemText primary="Export as CSV" />
        </MenuItem>
        <MenuItem onClick={() => handleQuickExport('excel')}>
          <ListItemIcon>
            <Description />
          </ListItemIcon>
          <ListItemText primary="Export as Excel" />
        </MenuItem>
        <MenuItem onClick={() => handleQuickExport('json')}>
          <ListItemIcon>
            <Code />
          </ListItemIcon>
          <ListItemText primary="Export as JSON" />
        </MenuItem>
        <MenuItem onClick={handleAdvancedExport}>
          <ListItemIcon>
            <CloudDownload />
          </ListItemIcon>
          <ListItemText primary="Advanced Export..." />
        </MenuItem>
      </Menu>

      <StyledDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CloudDownload sx={{ color: 'primary.main' }} />
            <Typography variant="h6">Advanced Export Options</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <FormControl component="fieldset" sx={{ width: '100%' }}>
              <FormLabel component="legend" sx={{ mb: 2 }}>
                Export Format
              </FormLabel>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
                {(['csv', 'excel', 'json', 'pdf'] as const).map((format) => (
                  <FormatOption
                    key={format}
                    className={exportFormat === format ? 'selected' : ''}
                    onClick={() => setExportFormat(format)}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getFormatIcon(format)}
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {format.toUpperCase()}
                      </Typography>
                    </Box>
                  </FormatOption>
                ))}
              </Box>
            </FormControl>

            <FormControl component="fieldset" sx={{ width: '100%', mt: 3 }}>
              <FormLabel component="legend" sx={{ mb: 2 }}>
                Fields to Include
              </FormLabel>
              <FormGroup>
                {availableFields.map((field) => (
                  <FormControlLabel
                    key={field.key}
                    control={
                      <Checkbox
                        checked={selectedFields.includes(field.key)}
                        onChange={() => handleFieldToggle(field.key)}
                      />
                    }
                    label={field.label}
                  />
                ))}
              </FormGroup>
            </FormControl>

            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="caption">
                {data.length} items will be exported with {selectedFields.length} fields
              </Typography>
            </Alert>
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 3, gap: 2 }}>
          <Button
            onClick={() => setDialogOpen(false)}
            variant="outlined"
            color="inherit"
          >
            Cancel
          </Button>
          <Button
            onClick={() => {
              performExport(exportFormat, selectedFields);
              setDialogOpen(false);
            }}
            variant="contained"
            startIcon={<GetApp />}
            disabled={selectedFields.length === 0}
          >
            Export {data.length} Items
          </Button>
        </DialogActions>
      </StyledDialog>
    </>
  );
};

export default InventoryExport;