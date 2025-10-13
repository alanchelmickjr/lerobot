import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Button,
  TextField,
  Typography,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Chip,
  IconButton,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Close,
  Add,
  Remove,
  SwapHoriz,
  Save,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface BulkUpdateDialogProps {
  open: boolean;
  onClose: () => void;
  selectedItems: any[];
  onUpdate: (updates: any) => void;
}

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    borderRadius: theme.spacing(2),
    maxWidth: 600,
    width: '100%',
    background: theme.palette.mode === 'dark'
      ? 'linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%)'
      : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  },
}));

const DialogHeader = styled(DialogTitle)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  paddingBottom: theme.spacing(1),
  borderBottom: `2px solid ${theme.palette.primary.main}`,
}));

const UpdateOption = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1.5),
  border: `1px solid ${theme.palette.divider}`,
  marginBottom: theme.spacing(2),
  transition: 'all 0.3s ease',
  cursor: 'pointer',
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

const ActionButton = styled(Button)(({ theme }) => ({
  borderRadius: theme.spacing(1.5),
  padding: theme.spacing(1.5, 3),
  textTransform: 'none',
  fontWeight: 600,
  fontSize: '1rem',
}));

const SelectedItemChip = styled(Chip)(({ theme }) => ({
  margin: theme.spacing(0.5),
  borderRadius: theme.spacing(1),
}));

const BulkUpdateDialog: React.FC<BulkUpdateDialogProps> = ({
  open,
  onClose,
  selectedItems,
  onUpdate,
}) => {
  const [updateType, setUpdateType] = useState<'add' | 'subtract' | 'set' | ''>('');
  const [updateValue, setUpdateValue] = useState<number>(0);
  const [updateField, setUpdateField] = useState<'quantity' | 'minStock' | 'maxStock' | 'price'>('quantity');
  const [confirmStep, setConfirmStep] = useState(false);

  const handleUpdateTypeSelect = (type: 'add' | 'subtract' | 'set') => {
    setUpdateType(type);
    setConfirmStep(false);
  };

  const handleConfirm = () => {
    if (!confirmStep) {
      setConfirmStep(true);
      return;
    }
    
    const updates = {
      type: updateType,
      field: updateField,
      value: updateValue,
    };
    
    onUpdate(updates);
    handleClose();
  };

  const handleClose = () => {
    setUpdateType('');
    setUpdateValue(0);
    setUpdateField('quantity');
    setConfirmStep(false);
    onClose();
  };

  const getUpdatePreview = () => {
    if (!updateType || !updateValue) return null;
    
    switch (updateType) {
      case 'add':
        return `Add ${updateValue} to ${updateField}`;
      case 'subtract':
        return `Subtract ${updateValue} from ${updateField}`;
      case 'set':
        return `Set ${updateField} to ${updateValue}`;
      default:
        return null;
    }
  };

  const getAffectedItemsPreview = () => {
    if (!selectedItems || selectedItems.length === 0) return [];
    
    return selectedItems.map(item => {
      let newValue = item[updateField];
      
      switch (updateType) {
        case 'add':
          newValue = item[updateField] + updateValue;
          break;
        case 'subtract':
          newValue = Math.max(0, item[updateField] - updateValue);
          break;
        case 'set':
          newValue = updateValue;
          break;
      }
      
      return {
        ...item,
        oldValue: item[updateField],
        newValue,
        change: newValue - item[updateField],
      };
    });
  };

  return (
    <StyledDialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      TransitionComponent={motion.div}
      TransitionProps={{
        initial: { opacity: 0, scale: 0.9 },
        animate: { opacity: 1, scale: 1 },
        exit: { opacity: 0, scale: 0.9 },
      }}
    >
      <DialogHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SwapHoriz sx={{ color: 'primary.main', fontSize: 28 }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              Bulk Update
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Update {selectedItems.length} selected items
            </Typography>
          </Box>
        </Box>
        <IconButton onClick={handleClose} size="small">
          <Close />
        </IconButton>
      </DialogHeader>

      <DialogContent sx={{ pt: 3 }}>
        {!confirmStep ? (
          <>
            {/* Selected Items Display */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                Selected Items ({selectedItems.length})
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap' }}>
                {selectedItems.slice(0, 5).map((item, index) => (
                  <SelectedItemChip
                    key={index}
                    label={item.name || `Item ${index + 1}`}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                ))}
                {selectedItems.length > 5 && (
                  <SelectedItemChip
                    label={`+${selectedItems.length - 5} more`}
                    size="small"
                    color="default"
                  />
                )}
              </Box>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {/* Update Type Selection */}
            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Select Update Type
            </Typography>
            
            <UpdateOption
              className={updateType === 'add' ? 'selected' : ''}
              onClick={() => handleUpdateTypeSelect('add')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Add sx={{ color: 'success.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Add to Current Value
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Increase the current value by a specified amount
                  </Typography>
                </Box>
              </Box>
            </UpdateOption>

            <UpdateOption
              className={updateType === 'subtract' ? 'selected' : ''}
              onClick={() => handleUpdateTypeSelect('subtract')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Remove sx={{ color: 'warning.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Subtract from Current Value
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Decrease the current value by a specified amount
                  </Typography>
                </Box>
              </Box>
            </UpdateOption>

            <UpdateOption
              className={updateType === 'set' ? 'selected' : ''}
              onClick={() => handleUpdateTypeSelect('set')}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <SwapHoriz sx={{ color: 'info.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Set to Specific Value
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Replace the current value with a new value
                  </Typography>
                </Box>
              </Box>
            </UpdateOption>

            {updateType && (
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                >
                  <Box sx={{ mt: 3 }}>
                    <FormControl component="fieldset" sx={{ width: '100%' }}>
                      <FormLabel component="legend" sx={{ mb: 2 }}>
                        Select Field to Update
                      </FormLabel>
                      <RadioGroup
                        value={updateField}
                        onChange={(e) => setUpdateField(e.target.value as any)}
                        sx={{ gap: 1 }}
                      >
                        <FormControlLabel value="quantity" control={<Radio />} label="Quantity" />
                        <FormControlLabel value="minStock" control={<Radio />} label="Minimum Stock" />
                        <FormControlLabel value="maxStock" control={<Radio />} label="Maximum Stock" />
                        <FormControlLabel value="price" control={<Radio />} label="Unit Price" />
                      </RadioGroup>
                    </FormControl>

                    <TextField
                      fullWidth
                      type="number"
                      label={`${updateType === 'add' ? 'Add' : updateType === 'subtract' ? 'Subtract' : 'Set'} Value`}
                      value={updateValue}
                      onChange={(e) => setUpdateValue(Number(e.target.value))}
                      sx={{ mt: 3 }}
                      InputProps={{
                        startAdornment: updateField === 'price' ? '$' : null,
                      }}
                    />
                  </Box>
                </motion.div>
              </AnimatePresence>
            )}
          </>
        ) : (
          /* Confirmation Step */
          <Box>
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                Please review the changes before confirming
              </Typography>
            </Alert>

            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
              Update Summary
            </Typography>
            
            <Box sx={{ p: 2, borderRadius: 1, bgcolor: 'background.default', mb: 3 }}>
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {getUpdatePreview()}
              </Typography>
            </Box>

            <Typography variant="subtitle2" color="textSecondary" gutterBottom>
              Affected Items Preview
            </Typography>
            
            <List dense sx={{ maxHeight: 200, overflow: 'auto', bgcolor: 'background.default', borderRadius: 1 }}>
              {getAffectedItemsPreview().map((item, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    {item.change > 0 ? (
                      <CheckCircle sx={{ color: 'success.main' }} />
                    ) : item.change < 0 ? (
                      <Warning sx={{ color: 'warning.main' }} />
                    ) : (
                      <SwapHoriz sx={{ color: 'info.main' }} />
                    )}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.name}
                    secondary={`${item.oldValue} → ${item.newValue} (${item.change > 0 ? '+' : ''}${item.change})`}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3, gap: 2 }}>
        <ActionButton
          onClick={handleClose}
          variant="outlined"
          color="inherit"
        >
          Cancel
        </ActionButton>
        {confirmStep && (
          <ActionButton
            onClick={() => setConfirmStep(false)}
            variant="outlined"
            color="primary"
          >
            Back
          </ActionButton>
        )}
        <ActionButton
          onClick={handleConfirm}
          variant="contained"
          color="primary"
          disabled={!updateType || !updateValue}
          startIcon={confirmStep ? <Save /> : null}
        >
          {confirmStep ? 'Confirm Update' : 'Next'}
        </ActionButton>
      </DialogActions>
    </StyledDialog>
  );
};

export default BulkUpdateDialog;