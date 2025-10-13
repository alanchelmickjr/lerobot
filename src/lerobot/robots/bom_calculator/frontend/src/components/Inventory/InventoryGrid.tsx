import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  IconButton,
  Tooltip,
  Chip,
  Typography,
  TextField,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  DataGrid,
  GridColDef,
  GridRenderCellParams,
  GridRenderEditCellParams,
  GridRowsProp,
  GridActionsCellItem,
  GridToolbar,
  GridRowModes,
  GridRowModesModel,
  GridEventListener,
  GridRowEditStopReasons,
  GridValueGetterParams,
} from '@mui/x-data-grid';
import {
  Edit,
  Delete,
  Save,
  Cancel,
  MoreVert,
  Warning,
  CheckCircle,
  Error,
  AddCircle,
  RemoveCircle,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface InventoryItem {
  id: string;
  partNumber: string;
  name: string;
  category: string;
  quantity: number;
  minStock: number;
  maxStock: number;
  unitPrice: number;
  supplier: string;
  location: string;
  status: 'in_stock' | 'low_stock' | 'out_of_stock';
  lastUpdated: Date;
}

interface InventoryGridProps {
  data?: InventoryItem[];
  onUpdate?: (item: InventoryItem) => void;
  onDelete?: (id: string) => void;
  onBulkUpdate?: (ids: string[], updates: Partial<InventoryItem>) => void;
}

const StyledDataGrid = styled(DataGrid)(({ theme }) => ({
  border: 'none',
  borderRadius: theme.spacing(2),
  '& .MuiDataGrid-cell': {
    borderBottom: `1px solid ${theme.palette.divider}`,
    fontSize: '0.95rem',
  },
  '& .MuiDataGrid-columnHeaders': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.03)',
    borderBottom: `2px solid ${theme.palette.primary.main}`,
    fontSize: '1rem',
    fontWeight: 600,
  },
  '& .MuiDataGrid-virtualScroller': {
    backgroundColor: theme.palette.background.paper,
  },
  '& .MuiDataGrid-footerContainer': {
    borderTop: `2px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.03)',
  },
  '& .MuiCheckbox-root': {
    color: theme.palette.primary.main,
  },
  '& .MuiDataGrid-row': {
    '&:hover': {
      backgroundColor: theme.palette.action.hover,
    },
    '&.Mui-selected': {
      backgroundColor: theme.palette.action.selected,
    },
  },
  '& .MuiDataGrid-cell--editing': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(0, 0, 0, 0.05)',
  },
  '& .status-in_stock': {
    color: theme.palette.success.main,
  },
  '& .status-low_stock': {
    color: theme.palette.warning.main,
  },
  '& .status-out_of_stock': {
    color: theme.palette.error.main,
  },
}));

const GridContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const mockInventoryData: InventoryItem[] = [
  {
    id: '1',
    partNumber: 'XL320',
    name: 'Servo Motor XL320',
    category: 'Motors',
    quantity: 45,
    minStock: 20,
    maxStock: 100,
    unitPrice: 24.99,
    supplier: 'Robotis',
    location: 'A1-B2',
    status: 'in_stock',
    lastUpdated: new Date(),
  },
  {
    id: '2',
    partNumber: 'U2D2',
    name: 'USB to Dynamixel',
    category: 'Controllers',
    quantity: 8,
    minStock: 10,
    maxStock: 50,
    unitPrice: 49.99,
    supplier: 'Robotis',
    location: 'A2-C1',
    status: 'low_stock',
    lastUpdated: new Date(),
  },
  {
    id: '3',
    partNumber: 'GRP-01',
    name: 'Gripper Assembly',
    category: 'End Effectors',
    quantity: 0,
    minStock: 5,
    maxStock: 25,
    unitPrice: 89.99,
    supplier: 'Custom Parts Co',
    location: 'B1-A3',
    status: 'out_of_stock',
    lastUpdated: new Date(),
  },
];

const InventoryGrid: React.FC<InventoryGridProps> = ({
  data = mockInventoryData,
  onUpdate,
  onDelete,
  onBulkUpdate,
}) => {
  const [rows, setRows] = useState<GridRowsProp>(data);
  const [rowModesModel, setRowModesModel] = useState<GridRowModesModel>({});
  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleRowEditStop: GridEventListener<'rowEditStop'> = (params, event) => {
    if (params.reason === GridRowEditStopReasons.rowFocusOut) {
      event.defaultMuiPrevented = true;
    }
  };

  const handleEditClick = (id: string) => () => {
    setRowModesModel({ ...rowModesModel, [id]: { mode: GridRowModes.Edit } });
  };

  const handleSaveClick = (id: string) => () => {
    setRowModesModel({ ...rowModesModel, [id]: { mode: GridRowModes.View } });
  };

  const handleDeleteClick = (id: string) => () => {
    setRows(rows.filter((row) => row.id !== id));
    if (onDelete) onDelete(id);
  };

  const handleCancelClick = (id: string) => () => {
    setRowModesModel({
      ...rowModesModel,
      [id]: { mode: GridRowModes.View, ignoreModifications: true },
    });
  };

  const processRowUpdate = (newRow: any) => {
    const updatedRow = { ...newRow, lastUpdated: new Date() };
    setRows(rows.map((row) => (row.id === newRow.id ? updatedRow : row)));
    if (onUpdate) onUpdate(updatedRow);
    return updatedRow;
  };

  const handleBulkAction = (action: string) => {
    if (selectedRows.length === 0) return;
    
    switch (action) {
      case 'delete':
        setRows(rows.filter((row) => !selectedRows.includes(row.id)));
        selectedRows.forEach((id) => {
          if (onDelete) onDelete(id);
        });
        break;
      case 'increase':
        setRows(rows.map((row) => 
          selectedRows.includes(row.id) 
            ? { ...row, quantity: row.quantity + 10 }
            : row
        ));
        break;
      case 'decrease':
        setRows(rows.map((row) => 
          selectedRows.includes(row.id) 
            ? { ...row, quantity: Math.max(0, row.quantity - 10) }
            : row
        ));
        break;
    }
    setSelectedRows([]);
    setAnchorEl(null);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'in_stock':
        return <CheckCircle sx={{ fontSize: 16 }} />;
      case 'low_stock':
        return <Warning sx={{ fontSize: 16 }} />;
      case 'out_of_stock':
        return <Error sx={{ fontSize: 16 }} />;
      default:
        return null;
    }
  };

  const columns: GridColDef[] = [
    {
      field: 'partNumber',
      headerName: 'Part #',
      width: 100,
      editable: true,
    },
    {
      field: 'name',
      headerName: 'Name',
      width: 200,
      editable: true,
      flex: 1,
    },
    {
      field: 'category',
      headerName: 'Category',
      width: 120,
      editable: true,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          label={params.value}
          size="small"
          variant="outlined"
          sx={{ fontWeight: 500 }}
        />
      ),
    },
    {
      field: 'quantity',
      headerName: 'Quantity',
      width: 120,
      editable: true,
      type: 'number',
      renderCell: (params: GridRenderCellParams) => (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            sx={{
              fontWeight: 600,
              color: params.row.quantity === 0 ? 'error.main' : 
                     params.row.quantity < params.row.minStock ? 'warning.main' : 
                     'text.primary',
            }}
          >
            {params.value}
          </Typography>
        </Box>
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      width: 130,
      renderCell: (params: GridRenderCellParams) => (
        <Chip
          icon={getStatusIcon(params.value)}
          label={params.value.replace('_', ' ').toUpperCase()}
          size="small"
          color={
            params.value === 'in_stock' ? 'success' :
            params.value === 'low_stock' ? 'warning' : 'error'
          }
          sx={{ fontWeight: 500 }}
        />
      ),
      valueGetter: (params: GridValueGetterParams) => {
        if (params.row.quantity === 0) return 'out_of_stock';
        if (params.row.quantity < params.row.minStock) return 'low_stock';
        return 'in_stock';
      },
    },
    {
      field: 'unitPrice',
      headerName: 'Unit Price',
      width: 110,
      editable: true,
      type: 'number',
      valueFormatter: (params) => `$${params.value?.toFixed(2)}`,
    },
    {
      field: 'supplier',
      headerName: 'Supplier',
      width: 150,
      editable: true,
    },
    {
      field: 'location',
      headerName: 'Location',
      width: 100,
      editable: true,
    },
    {
      field: 'actions',
      type: 'actions',
      headerName: 'Actions',
      width: 100,
      cellClassName: 'actions',
      getActions: ({ id }) => {
        const isInEditMode = rowModesModel[id]?.mode === GridRowModes.Edit;

        if (isInEditMode) {
          return [
            <GridActionsCellItem
              icon={<Save />}
              label="Save"
              sx={{ color: 'primary.main' }}
              onClick={handleSaveClick(id)}
            />,
            <GridActionsCellItem
              icon={<Cancel />}
              label="Cancel"
              color="inherit"
              onClick={handleCancelClick(id)}
            />,
          ];
        }

        return [
          <GridActionsCellItem
            icon={<Edit />}
            label="Edit"
            className="textPrimary"
            onClick={handleEditClick(id)}
            color="inherit"
          />,
          <GridActionsCellItem
            icon={<Delete />}
            label="Delete"
            onClick={handleDeleteClick(id)}
            color="inherit"
          />,
        ];
      },
    },
  ];

  return (
    <GridContainer elevation={0}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          Inventory Management
        </Typography>
        {selectedRows.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip
              label={`${selectedRows.length} selected`}
              color="primary"
              size="small"
            />
            <IconButton
              size="small"
              onClick={(e) => setAnchorEl(e.currentTarget)}
            >
              <MoreVert />
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={() => setAnchorEl(null)}
            >
              <MenuItem onClick={() => handleBulkAction('increase')}>
                <AddCircle sx={{ mr: 1, fontSize: 20 }} /> Increase by 10
              </MenuItem>
              <MenuItem onClick={() => handleBulkAction('decrease')}>
                <RemoveCircle sx={{ mr: 1, fontSize: 20 }} /> Decrease by 10
              </MenuItem>
              <MenuItem onClick={() => handleBulkAction('delete')}>
                <Delete sx={{ mr: 1, fontSize: 20 }} /> Delete Selected
              </MenuItem>
            </Menu>
          </Box>
        )}
      </Box>
      
      <Box sx={{ flexGrow: 1, height: 'calc(100% - 60px)' }}>
        <StyledDataGrid
          rows={rows}
          columns={columns}
          editMode="row"
          rowModesModel={rowModesModel}
          onRowModesModelChange={setRowModesModel}
          onRowEditStop={handleRowEditStop}
          processRowUpdate={processRowUpdate}
          onRowSelectionModelChange={(newSelection) => {
            setSelectedRows(newSelection as string[]);
          }}
          checkboxSelection
          disableRowSelectionOnClick
          pageSizeOptions={[10, 25, 50, 100]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
          }}
          slots={{
            toolbar: GridToolbar,
          }}
          slotProps={{
            toolbar: {
              showQuickFilter: true,
              quickFilterProps: { debounceMs: 500 },
            },
          }}
          sx={{
            '& .MuiDataGrid-toolbarContainer': {
              padding: 2,
              borderBottom: 1,
              borderColor: 'divider',
            },
          }}
        />
      </Box>
    </GridContainer>
  );
};

export default InventoryGrid;