import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Button,
  Collapse,
  Typography,
  Slider,
  InputAdornment,
} from '@mui/material';
import {
  Search,
  FilterList,
  Clear,
  ExpandMore,
  ExpandLess,
  Category,
  Business,
  LocationOn,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface FilterValues {
  search: string;
  category: string;
  status: string;
  supplier: string;
  location: string;
  minQuantity: number;
  maxQuantity: number;
  minPrice: number;
  maxPrice: number;
}

interface InventoryFiltersProps {
  onFilterChange: (filters: FilterValues) => void;
  categories?: string[];
  suppliers?: string[];
  locations?: string[];
}

const FilterContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(2),
}));

const FilterChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  borderRadius: theme.spacing(1),
  fontWeight: 500,
  '&:hover': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
  },
}));

const SearchField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: theme.spacing(2),
    backgroundColor: theme.palette.background.paper,
    '&:hover': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.main,
      },
    },
    '&.Mui-focused': {
      '& .MuiOutlinedInput-notchedOutline': {
        borderColor: theme.palette.primary.main,
        borderWidth: 2,
      },
    },
  },
}));

const defaultCategories = ['Motors', 'Sensors', 'Controllers', 'Structural', 'Electronics', 'Fasteners'];
const defaultSuppliers = ['Robotis', 'Custom Parts Co', 'Tech Supplier Inc', 'Direct Factory'];
const defaultLocations = ['A1-B2', 'A2-C1', 'B1-A3', 'C1-D4', 'Warehouse 2'];

const InventoryFilters: React.FC<InventoryFiltersProps> = ({
  onFilterChange,
  categories = defaultCategories,
  suppliers = defaultSuppliers,
  locations = defaultLocations,
}) => {
  const [filters, setFilters] = useState<FilterValues>({
    search: '',
    category: '',
    status: '',
    supplier: '',
    location: '',
    minQuantity: 0,
    maxQuantity: 1000,
    minPrice: 0,
    maxPrice: 1000,
  });

  const [expanded, setExpanded] = useState(false);
  const [activeFilters, setActiveFilters] = useState<string[]>([]);

  const handleFilterChange = (field: keyof FilterValues, value: any) => {
    const newFilters = { ...filters, [field]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);

    // Track active filters
    if (value && value !== '' && value !== 0) {
      if (!activeFilters.includes(field)) {
        setActiveFilters([...activeFilters, field]);
      }
    } else {
      setActiveFilters(activeFilters.filter(f => f !== field));
    }
  };

  const clearFilter = (field: keyof FilterValues) => {
    const defaultValue = typeof filters[field] === 'number' ? 0 : '';
    handleFilterChange(field, defaultValue);
  };

  const clearAllFilters = () => {
    const clearedFilters: FilterValues = {
      search: '',
      category: '',
      status: '',
      supplier: '',
      location: '',
      minQuantity: 0,
      maxQuantity: 1000,
      minPrice: 0,
      maxPrice: 1000,
    };
    setFilters(clearedFilters);
    setActiveFilters([]);
    onFilterChange(clearedFilters);
  };

  const getFilterLabel = (field: string, value: any): string => {
    if (field === 'minQuantity' || field === 'maxQuantity') {
      return `${field.replace('Quantity', ' Qty')}: ${value}`;
    }
    if (field === 'minPrice' || field === 'maxPrice') {
      return `${field.replace('Price', '')}: $${value}`;
    }
    return `${field}: ${value}`;
  };

  return (
    <FilterContainer elevation={0}>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {/* Main Search Bar */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <SearchField
            fullWidth
            variant="outlined"
            placeholder="Search parts by name, number, or description..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
              endAdornment: filters.search && (
                <InputAdornment position="end">
                  <IconButton size="small" onClick={() => clearFilter('search')}>
                    <Clear />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
          <Button
            variant="outlined"
            startIcon={expanded ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setExpanded(!expanded)}
            sx={{
              minWidth: 140,
              borderRadius: 2,
              textTransform: 'none',
            }}
          >
            <FilterList sx={{ mr: 1 }} />
            Filters ({activeFilters.length})
          </Button>
        </Box>

        {/* Quick Filter Chips */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <FilterChip
            label="In Stock"
            variant={filters.status === 'in_stock' ? 'filled' : 'outlined'}
            color={filters.status === 'in_stock' ? 'primary' : 'default'}
            onClick={() => handleFilterChange('status', filters.status === 'in_stock' ? '' : 'in_stock')}
          />
          <FilterChip
            label="Low Stock"
            variant={filters.status === 'low_stock' ? 'filled' : 'outlined'}
            color={filters.status === 'low_stock' ? 'warning' : 'default'}
            onClick={() => handleFilterChange('status', filters.status === 'low_stock' ? '' : 'low_stock')}
          />
          <FilterChip
            label="Out of Stock"
            variant={filters.status === 'out_of_stock' ? 'filled' : 'outlined'}
            color={filters.status === 'out_of_stock' ? 'error' : 'default'}
            onClick={() => handleFilterChange('status', filters.status === 'out_of_stock' ? '' : 'out_of_stock')}
          />
          {categories.slice(0, 4).map((cat) => (
            <FilterChip
              key={cat}
              label={cat}
              icon={<Category />}
              variant={filters.category === cat ? 'filled' : 'outlined'}
              color={filters.category === cat ? 'primary' : 'default'}
              onClick={() => handleFilterChange('category', filters.category === cat ? '' : cat)}
            />
          ))}
        </Box>

        {/* Expanded Filters */}
        <Collapse in={expanded}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2, mt: 2 }}>
              <FormControl fullWidth variant="outlined">
                <InputLabel>Category</InputLabel>
                <Select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  label="Category"
                  startAdornment={<Category sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((cat) => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth variant="outlined">
                <InputLabel>Supplier</InputLabel>
                <Select
                  value={filters.supplier}
                  onChange={(e) => handleFilterChange('supplier', e.target.value)}
                  label="Supplier"
                  startAdornment={<Business sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">All Suppliers</MenuItem>
                  {suppliers.map((sup) => (
                    <MenuItem key={sup} value={sup}>{sup}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth variant="outlined">
                <InputLabel>Location</InputLabel>
                <Select
                  value={filters.location}
                  onChange={(e) => handleFilterChange('location', e.target.value)}
                  label="Location"
                  startAdornment={<LocationOn sx={{ mr: 1, color: 'text.secondary' }} />}
                >
                  <MenuItem value="">All Locations</MenuItem>
                  {locations.map((loc) => (
                    <MenuItem key={loc} value={loc}>{loc}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>

            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                Quantity Range
              </Typography>
              <Box sx={{ px: 2 }}>
                <Slider
                  value={[filters.minQuantity, filters.maxQuantity]}
                  onChange={(_, value) => {
                    const [min, max] = value as number[];
                    handleFilterChange('minQuantity', min);
                    handleFilterChange('maxQuantity', max);
                  }}
                  valueLabelDisplay="auto"
                  min={0}
                  max={1000}
                  sx={{ mb: 2 }}
                />
              </Box>
            </Box>

            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Price Range
              </Typography>
              <Box sx={{ px: 2 }}>
                <Slider
                  value={[filters.minPrice, filters.maxPrice]}
                  onChange={(_, value) => {
                    const [min, max] = value as number[];
                    handleFilterChange('minPrice', min);
                    handleFilterChange('maxPrice', max);
                  }}
                  valueLabelDisplay="auto"
                  min={0}
                  max={1000}
                  valueLabelFormat={(value) => `$${value}`}
                  sx={{ mb: 2 }}
                />
              </Box>
            </Box>
          </motion.div>
        </Collapse>

        {/* Active Filters Display */}
        {activeFilters.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, alignItems: 'center' }}>
            <Typography variant="caption" color="textSecondary" sx={{ mr: 1 }}>
              Active filters:
            </Typography>
            {activeFilters.map((field) => (
              <Chip
                key={field}
                label={getFilterLabel(field, filters[field as keyof FilterValues])}
                onDelete={() => clearFilter(field as keyof FilterValues)}
                size="small"
                color="primary"
                variant="outlined"
              />
            ))}
            <Button
              size="small"
              onClick={clearAllFilters}
              startIcon={<Clear />}
              sx={{ ml: 1 }}
            >
              Clear All
            </Button>
          </Box>
        )}
      </Box>
    </FilterContainer>
  );
};

export default InventoryFilters;