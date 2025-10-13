# BOM Calculator Application - Requirements Specification

## 1. Project Overview

### 1.1 Purpose
A web-based Bill of Materials (BOM) calculator for tracking robot parts inventory and managing assembly of multiple robot types. The system enables efficient inventory management, assembly planning, and material ordering for robotic platforms.

### 1.2 Scope
- Track loose parts inventory for three robot models (SO-ARM100, LeKiwi, XLERobot)
- Calculate assembly capacity based on current inventory
- Generate order sheets for additional robot builds
- Manage differentiation between loose parts and assembled units
- Support extensibility for future robot models

### 1.3 Target Users
- Robotics engineers and technicians
- Inventory managers
- Assembly team members
- Procurement specialists

## 2. Functional Requirements

### 2.1 Inventory Management (MUST HAVE)

#### FR-001: Parts Entry
- System SHALL provide tabular entry interface for parts inventory
- System SHALL support batch entry of multiple parts
- System SHALL validate part numbers against known BOM databases
- System SHALL support quantity updates (add, subtract, set)

#### FR-002: Part Categorization
- System SHALL differentiate between loose parts and assembled components
- System SHALL track parts by robot model association
- System SHALL support shared parts across multiple robot models
- System SHALL maintain part metadata (description, unit cost, supplier)

#### FR-003: Inventory Status
- System SHALL display real-time inventory levels
- System SHALL highlight critical shortages
- System SHALL show parts availability status (in-stock, low, out-of-stock)
- System SHALL calculate inventory value

### 2.2 Assembly Calculation (MUST HAVE)

#### FR-004: Assembly Capacity
- System SHALL calculate maximum number of complete robots buildable from current inventory
- System SHALL identify limiting parts (bottlenecks)
- System SHALL show partial assembly possibilities
- System SHALL support multi-robot simultaneous calculation

#### FR-005: Assembly Planning
- System SHALL generate assembly recommendations
- System SHALL optimize parts allocation across robot types
- System SHALL track reserved parts for planned assemblies
- System SHALL maintain assembly history

### 2.3 Order Management (MUST HAVE)

#### FR-006: Order Sheet Generation
- System SHALL generate order sheets for specified number of robots
- System SHALL calculate required parts minus current inventory
- System SHALL group orders by supplier
- System SHALL include cost estimates

#### FR-007: Order Templates
- System SHALL support downloadable blank inventory worksheets
- System SHALL export order sheets in multiple formats (PDF, CSV, Excel)
- System SHALL maintain order history
- System SHALL support recurring order templates

### 2.4 User Interface (MUST HAVE)

#### FR-008: Tablet Optimization
- System SHALL be optimized for 10-inch tablet displays
- System SHALL support touch interactions
- System SHALL provide responsive layout (768x1024 minimum)
- System SHALL support both portrait and landscape orientations

#### FR-009: Navigation
- System SHALL provide intuitive navigation between features
- System SHALL support quick access to common tasks
- System SHALL maintain context during navigation
- System SHALL support breadcrumb navigation

### 2.5 Data Management (MUST HAVE)

#### FR-010: BOM Integration
- System SHALL import BOM data from external sources
- System SHALL support manual BOM updates
- System SHALL validate BOM consistency
- System SHALL track BOM versions

#### FR-011: Data Persistence
- System SHALL persist all inventory changes
- System SHALL support data backup/restore
- System SHALL maintain audit trail
- System SHALL support data export

### 2.6 Extensibility (SHOULD HAVE)

#### FR-012: Robot Model Management
- System SHALL support adding new robot models
- System SHALL allow custom BOM definitions
- System SHALL support BOM inheritance/variations
- System SHALL maintain backward compatibility

## 3. Non-Functional Requirements

### 3.1 Performance
- NFR-001: Page load time SHALL be < 2 seconds
- NFR-002: Calculation updates SHALL complete < 500ms
- NFR-003: System SHALL support 100+ concurrent users
- NFR-004: Database queries SHALL complete < 200ms

### 3.2 Usability
- NFR-005: System SHALL require < 30 minutes training for new users
- NFR-006: Common tasks SHALL require < 3 clicks/taps
- NFR-007: System SHALL provide contextual help
- NFR-008: Error messages SHALL be clear and actionable

### 3.3 Reliability
- NFR-009: System SHALL maintain 99.5% uptime
- NFR-010: System SHALL handle network interruptions gracefully
- NFR-011: System SHALL recover from errors without data loss
- NFR-012: System SHALL validate all user inputs

### 3.4 Security
- NFR-013: System SHALL authenticate users
- NFR-014: System SHALL encrypt sensitive data
- NFR-015: System SHALL maintain access logs
- NFR-016: System SHALL prevent SQL injection

### 3.5 Compatibility
- NFR-017: System SHALL support Chrome, Firefox, Safari browsers
- NFR-018: System SHALL work on iOS and Android tablets
- NFR-019: System SHALL support offline mode for viewing
- NFR-020: System SHALL sync when connection restored

## 4. Constraints

### 4.1 Technical Constraints
- Python 3.9+ with FastAPI for backend
- React 18+ with TypeScript for frontend
- SQLite for standalone deployment
- Must run without internet after initial setup

### 4.2 Business Constraints
- Initial release must support three robot models
- Must integrate with existing BOM formats
- Must be deployable on standard hardware
- Must not require specialized training

### 4.3 Regulatory Constraints
- Must comply with data protection regulations
- Must maintain audit trail for compliance
- Must support data retention policies

## 5. Acceptance Criteria

### 5.1 Inventory Management
- ✓ User can add/update/delete parts inventory
- ✓ System correctly categorizes parts
- ✓ Inventory levels update in real-time
- ✓ System identifies critical shortages

### 5.2 Assembly Calculation
- ✓ System correctly calculates buildable robots
- ✓ System identifies bottleneck parts
- ✓ Calculations update within 500ms
- ✓ Multi-robot calculations are accurate

### 5.3 Order Management
- ✓ Generated order sheets are complete and accurate
- ✓ Export formats are properly formatted
- ✓ Templates download successfully
- ✓ Order history is maintained

### 5.4 User Interface
- ✓ Interface is usable on 10-inch tablet
- ✓ Touch interactions work correctly
- ✓ Layout adapts to orientation changes
- ✓ Navigation is intuitive

## 6. Use Cases

### UC-001: Add Parts to Inventory
**Actor**: Inventory Manager
**Precondition**: User is authenticated
**Flow**:
1. User navigates to inventory management
2. User selects robot model
3. User enters part quantities
4. System validates entries
5. System updates inventory
**Postcondition**: Inventory reflects new quantities

### UC-002: Calculate Assembly Capacity
**Actor**: Assembly Technician
**Precondition**: Inventory data exists
**Flow**:
1. User navigates to assembly calculator
2. User selects robot models
3. System calculates buildable units
4. System displays results with bottlenecks
5. User reviews recommendations
**Postcondition**: Assembly plan is generated

### UC-003: Generate Order Sheet
**Actor**: Procurement Specialist
**Precondition**: Target quantity specified
**Flow**:
1. User specifies robot quantities
2. System calculates required parts
3. System subtracts current inventory
4. System generates order sheet
5. User exports document
**Postcondition**: Order sheet is downloaded

## 7. Edge Cases

### 7.1 Data Edge Cases
- Empty inventory initialization
- Negative quantity prevention
- Duplicate part entries
- Missing BOM components
- Circular dependencies in assemblies

### 7.2 Calculation Edge Cases
- Zero inventory scenarios
- Partial assembly possibilities
- Shared parts conflicts
- Rounding errors in calculations
- Maximum quantity overflows

### 7.3 User Interface Edge Cases
- Screen rotation during data entry
- Network loss during save
- Concurrent user updates
- Session timeout handling
- Browser back button behavior

## 8. Dependencies

### 8.1 External Systems
- GitHub repositories for BOM sources
- File system for data persistence
- Browser local storage for caching

### 8.2 Libraries and Frameworks
- FastAPI for REST API
- React for UI components
- SQLite for data storage
- Pandas for data manipulation

## 9. Risks and Mitigation

### 9.1 Technical Risks
- **Risk**: BOM format changes
  **Mitigation**: Implement flexible parser with validation

- **Risk**: Performance with large inventories
  **Mitigation**: Implement pagination and caching

### 9.2 Business Risks
- **Risk**: Inaccurate calculations
  **Mitigation**: Comprehensive testing and validation

- **Risk**: User adoption
  **Mitigation**: Intuitive UI and training materials

## 10. Future Enhancements

- Mobile app version
- Barcode scanning support
- Integration with ERP systems
- Automated reorder points
- Predictive analytics
- Multi-language support
- Real-time collaboration
- Supply chain integration