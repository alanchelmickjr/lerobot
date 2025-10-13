# BOM Calculator User Guide

A comprehensive guide for using the Bill of Materials Calculator application for robot assembly management.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Inventory](#managing-inventory)
4. [Assembly Calculator](#assembly-calculator)
5. [Order Generation](#order-generation)
6. [Tablet Features](#tablet-features)
7. [Offline Usage](#offline-usage)
8. [Tips & Best Practices](#tips--best-practices)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Common Workflows](#common-workflows)

---

## Getting Started

### First-Time Setup

1. **Access the Application**
   - Open your web browser (Chrome, Firefox, or Safari recommended)
   - Navigate to `http://localhost:3000` (or your deployed URL)
   - For tablets: Add to home screen for app-like experience

2. **Login**
   - Enter your username and password
   - Select "Remember Me" for quick access on personal devices
   - Contact your administrator for credentials

3. **Initial Configuration**
   - Select your default warehouse/location
   - Choose your preferred theme (Light/Dark)
   - Set notification preferences
   - Configure default robot models

### User Interface Overview

The application features a modern Material Design 3 interface optimized for tablets:

- **Top Navigation Bar**: Quick access to search, filters, and settings
- **Side Navigation Drawer**: Main menu for feature access
- **Content Area**: Main workspace for current task
- **Floating Action Button**: Quick add/create actions
- **Status Bar**: Connection status and notifications

---

## Dashboard Overview

### Key Metrics Display

The dashboard provides real-time insights into your inventory and assembly capacity:

**Inventory Statistics**
- Total Parts Count
- Low Stock Alerts (items below reorder point)
- Total Inventory Value
- Categories Overview

**Assembly Capacity**
- SO-ARM100: Shows buildable units with visual progress ring
- LeKiwi: Displays capacity with component breakdown
- XLERobot: Complex assembly status with sub-assembly tracking

**Recent Activity**
- Last 10 inventory changes
- Recent assemblies completed
- Pending orders status
- System notifications

### Navigation Tips
- Tap any metric card for detailed view
- Swipe between robot models for quick comparison
- Long-press cards to pin to favorites

---

## Managing Inventory

### Viewing Inventory

1. **Grid View** (Default for tablets)
   - Visual cards showing part image, name, quantity
   - Color-coded stock levels (Green: Good, Yellow: Low, Red: Critical)
   - Quick actions via swipe gestures

2. **List View** (Compact mode)
   - Tabular format for bulk viewing
   - Sort by: Name, Category, Quantity, Last Updated
   - Multi-select for batch operations

### Adding/Updating Parts

#### Quick Update (Single Part)
1. Find the part using search or browse
2. Tap the quantity field
3. Use the touch-optimized number input:
   - Tap +/- buttons for single increments
   - Tap +10/-10 for larger adjustments
   - Use preset buttons (0, 10, 25, 50, 100)
   - Or type directly using on-screen keyboard
4. Tap "Save" or press Enter

#### Bulk Update (Multiple Parts)
1. Switch to List View
2. Tap "Edit Mode" button
3. Select multiple parts using checkboxes
4. Choose bulk action:
   - Add to all selected
   - Set all to specific value
   - Apply percentage change
5. Confirm changes

### Inventory Categories

Parts are organized into logical categories:
- **Servos**: All servo motors by voltage and gear ratio
- **Electronics**: Raspberry Pi, ESP32, power supplies
- **Mechanical**: Frames, brackets, screws, bearings
- **Wheels**: Omnidirectional and standard wheels
- **Cables**: Power, data, and extension cables
- **Sensors**: Cameras, IMUs, encoders
- **Tools**: Assembly and maintenance tools

### Stock Alerts

The system automatically monitors stock levels:
- **Critical** (Red): Below minimum required for any assembly
- **Low** (Yellow): Below reorder point but assemblies possible
- **Good** (Green): Adequate stock levels
- **Overstocked** (Blue): Significantly above reorder point

---

## Assembly Calculator

### Calculating Build Capacity

1. **Select Robot Model**
   - Tap on robot card from dashboard
   - Or navigate to Assembly → Calculate

2. **View Results**
   - **Maximum Buildable**: Large number display
   - **Bottleneck Parts**: List of limiting components
   - **Partial Assembly**: What can be pre-assembled
   - **Visual Chart**: Radial progress showing capacity

3. **Understanding Bottlenecks**
   Each bottleneck shows:
   - Part name and image
   - Required vs Available quantity
   - Progress bar showing availability percentage
   - Quick order button for missing parts

### Multi-Model Optimization

Calculate optimal build mix across models:

1. Navigate to Assembly → Optimize Mix
2. Set target quantities for each model
3. System calculates:
   - Feasible combinations
   - Shared parts conflicts
   - Optimal build sequence
4. Review recommendations
5. Apply or adjust as needed

### Assembly Planning

1. **Create Assembly Plan**
   - Select robot model and quantity
   - Choose assembly date/deadline
   - System reserves parts automatically
   - Generate pick list for warehouse

2. **Track Assembly Progress**
   - Mark stages as complete
   - Update partial assemblies
   - Log any issues or defects
   - Complete and update inventory

---

## Order Generation

### Creating Orders

1. **Quick Order (Single Model)**
   - From any bottleneck alert, tap "Order"
   - System calculates exact needs
   - Review and submit

2. **Custom Order**
   - Navigate to Orders → New Order
   - Specify target quantities for each model
   - Set build timeline
   - System generates complete order sheet

### Order Sheet Features

Generated orders include:
- **Parts List**: Grouped by supplier
- **Quantities**: Calculated with safety stock
- **Cost Estimates**: Per part and total
- **Supplier Info**: Contact and account details
- **Lead Times**: Expected delivery windows
- **Notes**: Special instructions or requirements

### Order Workflow

1. **Generate**
   - Input requirements
   - Review calculated needs
   - Adjust quantities if needed

2. **Export**
   - PDF for printing/emailing
   - CSV for spreadsheet import
   - Direct email to suppliers
   - Save as template

3. **Track**
   - Mark as ordered
   - Update expected delivery
   - Receive and update inventory
   - Close order

---

## Tablet Features

### Touch Gestures

The application supports intuitive touch interactions:

- **Tap**: Select or activate
- **Long Press**: Enter selection mode or show context menu
- **Swipe Right**: Quick edit action
- **Swipe Left**: Quick delete (with confirmation)
- **Pinch**: Zoom charts and diagrams
- **Two-finger Swipe**: Navigate between sections

### Optimized Layouts

**Portrait Mode**
- Single column layout
- Stacked cards
- Full-width inputs
- Bottom navigation bar

**Landscape Mode**
- Split-view layout
- Side-by-side panels
- Floating navigation
- More information density

### Quick Actions

**Floating Action Button (FAB)**
- Position: Bottom-right corner
- Primary action changes by context:
  - Inventory: Add new part
  - Assembly: Calculate capacity
  - Orders: Generate order

**Swipe Actions**
- Available on list items
- Right swipe: Edit
- Left swipe: Delete/Archive
- Customizable in settings

---

## Offline Usage

### Offline Capabilities

The application works without internet connection:

1. **Viewing**: All data cached locally
2. **Editing**: Changes queued for sync
3. **Calculations**: Fully functional offline
4. **Orders**: Saved locally, sent when online

### Sync Indicator

Connection status shown in status bar:
- 🟢 **Green**: Online and synced
- 🟡 **Yellow**: Offline, changes pending
- 🔴 **Red**: Sync error, action required

### Managing Offline Changes

1. Changes made offline are queued
2. Queue icon shows pending count
3. When connection restored:
   - Automatic sync attempts
   - Conflict resolution if needed
   - Notification of sync completion

---

## Tips & Best Practices

### Inventory Management

✅ **DO:**
- Update inventory immediately after physical changes
- Use bulk edit for large updates
- Set realistic reorder points
- Regular audits (weekly/monthly)
- Use notes field for important details

❌ **DON'T:**
- Delay inventory updates
- Ignore low stock warnings
- Override system calculations without reason
- Delete parts still in use

### Assembly Planning

✅ **Best Practices:**
- Plan assemblies 1-2 weeks ahead
- Reserve parts for confirmed orders
- Update partial assembly status
- Document any substitutions
- Complete assemblies promptly

💡 **Pro Tips:**
- Use assembly templates for repeat builds
- Pre-stage common sub-assemblies
- Keep 10% safety stock for critical parts
- Schedule assemblies during low-activity periods

### Order Management

✅ **Recommendations:**
- Consolidate orders to same supplier
- Order slightly above minimum for volume discounts
- Track lead times for better planning
- Keep supplier contact info updated
- Document order issues for future reference

### Data Quality

✅ **Maintain Accuracy:**
- Regular physical counts
- Verify BOM accuracy periodically
- Update part costs quarterly
- Clean up obsolete parts
- Standardize part naming

---

## Keyboard Shortcuts

For users with keyboard attached to tablet or desktop users:

### Global Shortcuts
- `Ctrl/Cmd + K`: Quick search
- `Ctrl/Cmd + N`: New item (context-aware)
- `Ctrl/Cmd + S`: Save current changes
- `Ctrl/Cmd + Z`: Undo last action
- `Esc`: Close dialog/cancel

### Navigation
- `Alt + I`: Go to Inventory
- `Alt + A`: Go to Assembly
- `Alt + O`: Go to Orders
- `Alt + D`: Go to Dashboard
- `Tab`: Navigate forward
- `Shift + Tab`: Navigate backward

### Inventory Shortcuts
- `E`: Edit selected item
- `D`: Delete selected items
- `Space`: Toggle selection
- `Ctrl/Cmd + A`: Select all
- `+/-`: Increment/decrement quantity

### Assembly Shortcuts
- `C`: Calculate capacity
- `R`: Refresh calculations
- `O`: Order missing parts
- `P`: Create assembly plan

---

## Common Workflows

### Weekly Inventory Audit

1. **Preparation**
   - Generate current inventory report
   - Print count sheets or use tablet
   - Assign sections to team members

2. **Counting**
   - Physical count by category
   - Note discrepancies
   - Check for damaged items
   - Verify locations

3. **Update System**
   - Enter counts using bulk edit
   - Document reasons for variances
   - Adjust damaged/obsolete items
   - Review and confirm changes

4. **Follow-up**
   - Generate variance report
   - Update reorder points if needed
   - Order low stock items
   - File audit documentation

### Preparing for Robot Build

1. **Check Capacity**
   - Select robot model
   - Run assembly calculator
   - Review bottlenecks

2. **Generate Order** (if needed)
   - Create order for missing parts
   - Add safety margin (10-15%)
   - Submit to suppliers
   - Track delivery

3. **Reserve Parts**
   - Create assembly plan
   - Set build date
   - System reserves inventory
   - Generate pick list

4. **Execute Build**
   - Retrieve parts using pick list
   - Update partial assembly progress
   - Complete build
   - Update system as "Assembled"

### Month-End Reporting

1. **Generate Reports**
   - Inventory value report
   - Assembly summary
   - Order history
   - Stock movement analysis

2. **Review Metrics**
   - Compare to previous months
   - Identify trends
   - Note concerns or achievements

3. **Planning**
   - Forecast next month needs
   - Adjust reorder points
   - Plan maintenance downtime
   - Schedule team training

---

## Getting Help

### In-App Help
- Tap the `?` icon for context-sensitive help
- Tooltips appear on long-press
- Tutorial mode available for new users

### Support Resources
- User Forum: Share tips and get community help
- Video Tutorials: Step-by-step visual guides
- Documentation: This guide and technical docs
- Support Email: support@bomcalculator.com

### Reporting Issues
When reporting problems:
1. Note the exact steps that led to issue
2. Take screenshot if possible (Power + Volume Down)
3. Check network connection
4. Include error messages
5. Submit via Help → Report Issue

---

## Appendix

### Supported Browsers
- Chrome 90+ (Recommended)
- Firefox 88+
- Safari 14+
- Edge 90+

### Minimum Requirements
- Screen: 7" minimum, 10" recommended
- Resolution: 768x1024 minimum
- Network: 3G minimum, WiFi recommended
- Storage: 50MB for offline data

### Data Limits
- Maximum parts: 10,000
- Maximum concurrent users: 100
- Sync frequency: Every 30 seconds
- Session timeout: 4 hours

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Next Review**: April 2024

For technical documentation, see the [Developer Guide](DEVELOPER_GUIDE.md).  
For deployment instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).