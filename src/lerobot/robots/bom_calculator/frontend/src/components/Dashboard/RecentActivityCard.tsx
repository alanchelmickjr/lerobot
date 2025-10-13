import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  IconButton,
  Tooltip,
  Avatar,
  AvatarGroup,
} from '@mui/material';
import {
  History,
  AddCircle,
  RemoveCircle,
  SwapHoriz,
  Build,
  ShoppingCart,
  InfoOutlined,
  AccessTime,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '@mui/material/styles';

interface Activity {
  id: string;
  type: 'add' | 'remove' | 'update' | 'assembly' | 'order';
  title: string;
  description: string;
  timestamp: Date;
  user?: string;
  quantity?: number;
  status?: 'success' | 'warning' | 'error';
}

interface RecentActivityCardProps {
  activities?: Activity[];
}

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  borderRadius: theme.spacing(2),
  background: theme.palette.mode === 'dark'
    ? 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)'
    : 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: theme.shadows[8],
    transform: 'translateY(-4px)',
  },
}));

const HeaderBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: theme.spacing(3),
  paddingBottom: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const ActivityItem = styled(motion.div)(({ theme }) => ({
  padding: theme.spacing(1.5),
  marginBottom: theme.spacing(1),
  borderRadius: theme.spacing(1.5),
  background: theme.palette.mode === 'dark'
    ? 'rgba(255, 255, 255, 0.03)'
    : 'rgba(0, 0, 0, 0.02)',
  border: `1px solid ${theme.palette.divider}`,
  transition: 'all 0.2s ease',
  '&:hover': {
    background: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.05)'
      : 'rgba(0, 0, 0, 0.04)',
    borderColor: theme.palette.primary.main,
    transform: 'translateX(4px)',
  },
}));

const TimelineConnector = styled(Box)(({ theme }) => ({
  position: 'absolute',
  left: 28,
  top: 44,
  bottom: 0,
  width: 2,
  background: theme.palette.divider,
  zIndex: 0,
}));

const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'add',
    title: 'Parts Added',
    description: 'Added 50 Servo Motors XL320 to inventory',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    user: 'John Doe',
    quantity: 50,
    status: 'success',
  },
  {
    id: '2',
    type: 'assembly',
    title: 'Robot Assembled',
    description: '2 Koch v1.1 robots assembled successfully',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    user: 'Jane Smith',
    quantity: 2,
    status: 'success',
  },
  {
    id: '3',
    type: 'remove',
    title: 'Parts Consumed',
    description: 'Used 20 Control Boards for assembly',
    timestamp: new Date(Date.now() - 1000 * 60 * 60),
    user: 'Mike Johnson',
    quantity: -20,
    status: 'warning',
  },
  {
    id: '4',
    type: 'order',
    title: 'Order Placed',
    description: 'Purchase order #PO-2024-001 created',
    timestamp: new Date(Date.now() - 1000 * 60 * 120),
    user: 'Sarah Wilson',
    status: 'success',
  },
  {
    id: '5',
    type: 'update',
    title: 'Stock Updated',
    description: 'Low stock alert for Gripper Assembly',
    timestamp: new Date(Date.now() - 1000 * 60 * 180),
    status: 'error',
  },
];

const RecentActivityCard: React.FC<RecentActivityCardProps> = ({ activities = mockActivities }) => {
  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'add':
        return <AddCircle sx={{ color: '#4caf50' }} />;
      case 'remove':
        return <RemoveCircle sx={{ color: '#ff9800' }} />;
      case 'update':
        return <SwapHoriz sx={{ color: '#2196f3' }} />;
      case 'assembly':
        return <Build sx={{ color: '#9c27b0' }} />;
      case 'order':
        return <ShoppingCart sx={{ color: '#00bcd4' }} />;
      default:
        return <History />;
    }
  };

  const getStatusColor = (status?: Activity['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatTime = (date: Date) => {
    const minutes = Math.floor((Date.now() - date.getTime()) / 60000);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getUserInitials = (name?: string) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  return (
    <StyledCard elevation={0}>
      <CardContent sx={{ p: 3, position: 'relative' }}>
        <HeaderBox>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <History sx={{ fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 600 }}>
                Recent Activity
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Last {activities.length} actions
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AvatarGroup max={3} sx={{ '& .MuiAvatar-root': { width: 32, height: 32, fontSize: 12 } }}>
              {activities.slice(0, 3).map((activity) => (
                <Avatar key={activity.id} sx={{ bgcolor: 'primary.main' }}>
                  {getUserInitials(activity.user)}
                </Avatar>
              ))}
            </AvatarGroup>
            <Tooltip title="View all activities">
              <IconButton size="small">
                <InfoOutlined />
              </IconButton>
            </Tooltip>
          </Box>
        </HeaderBox>

        <Box sx={{ position: 'relative' }}>
          <TimelineConnector />
          <AnimatePresence>
            {activities.map((activity, index) => (
              <ActivityItem
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ delay: index * 0.1 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, position: 'relative', zIndex: 1 }}>
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'background.paper',
                      border: 2,
                      borderColor: 'divider',
                    }}
                  >
                    {getActivityIcon(activity.type)}
                  </Box>
                  
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                        {activity.title}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {activity.quantity && (
                          <Chip
                            label={`${activity.quantity > 0 ? '+' : ''}${activity.quantity}`}
                            size="small"
                            color={activity.quantity > 0 ? 'success' : 'warning'}
                            sx={{ height: 20, fontSize: 11 }}
                          />
                        )}
                        {activity.status && (
                          <Chip
                            label={activity.status}
                            size="small"
                            color={getStatusColor(activity.status)}
                            variant="outlined"
                            sx={{ height: 20, fontSize: 11 }}
                          />
                        )}
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 0.5 }}>
                      {activity.description}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <AccessTime sx={{ fontSize: 14, color: 'text.secondary' }} />
                        <Typography variant="caption" color="textSecondary">
                          {formatTime(activity.timestamp)}
                        </Typography>
                      </Box>
                      {activity.user && (
                        <Typography variant="caption" color="textSecondary">
                          by {activity.user}
                        </Typography>
                      )}
                    </Box>
                  </Box>
                </Box>
              </ActivityItem>
            ))}
          </AnimatePresence>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default RecentActivityCard;