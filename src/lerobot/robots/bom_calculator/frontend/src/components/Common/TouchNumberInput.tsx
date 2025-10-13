import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Typography,
  Slider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Add,
  Remove,
  Undo,
  Check,
  Close,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface TouchNumberInputProps {
  value: number;
  onChange: (value: number) => void;
  onCommit?: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label?: string;
  unit?: string;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
  showSlider?: boolean;
  quickValues?: number[];
}

const InputContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.05)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    borderColor: theme.palette.primary.main,
    boxShadow: theme.shadows[2],
  },
  '&:focus-within': {
    borderColor: theme.palette.primary.main,
    boxShadow: `0 0 0 2px ${theme.palette.primary.main}25`,
  },
}));

const StepButton = styled(IconButton)(({ theme }) => ({
  width: 56,
  height: 56,
  borderRadius: theme.spacing(1.5),
  backgroundColor: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.08)'
    : 'rgba(0, 0, 0, 0.04)',
  '&:hover': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
    transform: 'scale(1.05)',
  },
  '&:active': {
    transform: 'scale(0.95)',
  },
  transition: 'all 0.2s ease',
}));

const QuickValueChip = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(1, 2),
  borderRadius: theme.spacing(3),
  backgroundColor: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.1)'
    : 'rgba(0, 0, 0, 0.05)',
  cursor: 'pointer',
  userSelect: 'none',
  transition: 'all 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
  },
  '&:active': {
    transform: 'scale(0.95)',
  },
}));

const ValueDisplay = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'baseline',
  justifyContent: 'center',
  gap: theme.spacing(1),
  minHeight: 48,
}));

const TouchNumberInput: React.FC<TouchNumberInputProps> = ({
  value,
  onChange,
  onCommit,
  min = 0,
  max = 999999,
  step = 1,
  label,
  unit,
  disabled = false,
  size = 'medium',
  showSlider = false,
  quickValues = [],
}) => {
  const theme = useTheme();
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'lg'));
  const [localValue, setLocalValue] = useState(value);
  const [isEditing, setIsEditing] = useState(false);
  const [originalValue, setOriginalValue] = useState(value);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleIncrement = () => {
    const newValue = Math.min(localValue + step, max);
    setLocalValue(newValue);
    onChange(newValue);
  };

  const handleDecrement = () => {
    const newValue = Math.max(localValue - step, min);
    setLocalValue(newValue);
    onChange(newValue);
  };

  const handleSliderChange = (_: Event, newValue: number | number[]) => {
    const val = Array.isArray(newValue) ? newValue[0] : newValue;
    setLocalValue(val);
    onChange(val);
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value) || 0;
    if (!isNaN(val) && val >= min && val <= max) {
      setLocalValue(val);
      onChange(val);
    }
  };

  const handleQuickValue = (quickValue: number) => {
    setLocalValue(quickValue);
    onChange(quickValue);
    if (onCommit) {
      onCommit(quickValue);
    }
  };

  const handleStartEdit = () => {
    setOriginalValue(localValue);
    setIsEditing(true);
  };

  const handleCommit = () => {
    if (onCommit) {
      onCommit(localValue);
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setLocalValue(originalValue);
    onChange(originalValue);
    setIsEditing(false);
  };

  const getFontSize = () => {
    switch (size) {
      case 'small': return '1.5rem';
      case 'large': return '3rem';
      default: return '2rem';
    }
  };

  return (
    <InputContainer elevation={0}>
      {label && (
        <Typography
          variant="subtitle2"
          color="textSecondary"
          gutterBottom
          sx={{ fontWeight: 600, mb: 2 }}
        >
          {label}
        </Typography>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <StepButton
            onClick={handleDecrement}
            disabled={disabled || localValue <= min}
            size={size}
          >
            <Remove />
          </StepButton>

          <ValueDisplay sx={{ flex: 1 }}>
            {isEditing ? (
              <TextField
                value={localValue}
                onChange={handleTextChange}
                type="number"
                inputProps={{ min, max, step }}
                autoFocus
                variant="standard"
                sx={{
                  '& input': {
                    fontSize: getFontSize(),
                    textAlign: 'center',
                    fontWeight: 600,
                  },
                }}
              />
            ) : (
              <motion.div
                onClick={handleStartEdit}
                whileTap={{ scale: 0.95 }}
                style={{ cursor: 'pointer' }}
              >
                <Typography
                  variant="h3"
                  sx={{
                    fontSize: getFontSize(),
                    fontWeight: 700,
                    color: 'primary.main',
                  }}
                >
                  {localValue.toLocaleString()}
                </Typography>
              </motion.div>
            )}
            {unit && (
              <Typography
                variant="body1"
                color="textSecondary"
                sx={{ fontSize: '1.2rem', fontWeight: 500 }}
              >
                {unit}
              </Typography>
            )}
          </ValueDisplay>

          <StepButton
            onClick={handleIncrement}
            disabled={disabled || localValue >= max}
            size={size}
          >
            <Add />
          </StepButton>
        </Box>

        {isEditing && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                <IconButton
                  onClick={handleCommit}
                  color="primary"
                  sx={{
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  }}
                >
                  <Check />
                </IconButton>
                <IconButton
                  onClick={handleCancel}
                  color="error"
                  sx={{
                    backgroundColor: 'error.main',
                    color: 'error.contrastText',
                    '&:hover': {
                      backgroundColor: 'error.dark',
                    },
                  }}
                >
                  <Close />
                </IconButton>
              </Box>
            </motion.div>
          </AnimatePresence>
        )}

        {showSlider && (
          <Box sx={{ px: 2 }}>
            <Slider
              value={localValue}
              onChange={handleSliderChange}
              min={min}
              max={max}
              step={step}
              disabled={disabled}
              valueLabelDisplay="auto"
              sx={{
                height: 8,
                '& .MuiSlider-thumb': {
                  width: 24,
                  height: 24,
                },
              }}
            />
          </Box>
        )}

        {quickValues.length > 0 && (
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
            {quickValues.map((qv) => (
              <QuickValueChip
                key={qv}
                onClick={() => handleQuickValue(qv)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {qv.toLocaleString()}
                </Typography>
              </QuickValueChip>
            ))}
          </Box>
        )}
      </Box>
    </InputContainer>
  );
};

export default TouchNumberInput;