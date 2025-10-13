# BOM Calculator - Domain Model

## Core Entities

### 1. Part
Represents an individual component that can be used in robot assembly.

**Attributes:**
- `part_id`: string (unique identifier)
- `name`: string (human-readable name)
- `description`: string (detailed description)
- `category`: PartCategory (enum: SERVO, ELECTRONICS, MECHANICAL, POWER, FASTENER, SENSOR, STRUCTURAL)
- `unit_cost`: decimal (optional)
- `supplier`: string (optional)
- `supplier_part_number`: string (optional)
- `minimum_order_quantity`: integer (default: 1)
- `lead_time_days`: integer (optional)
- `specifications`: dict (key-value pairs for technical specs)
- `is_assembly`: boolean (indicates if this is a pre-assembled component)
- `created_at`: timestamp
- `updated_at`: timestamp

**Invariants:**
- part_id must be unique across the system
- name cannot be empty
- unit_cost >= 0 if specified
- minimum_order_quantity >= 1

### 2. RobotModel
Defines a specific robot model and its configuration.

**Attributes:**
- `model_id`: string (unique identifier)
- `name`: string (e.g., "SO-ARM100", "LeKiwi", "XLERobot")
- `description`: string
- `version`: string (BOM version)
- `documentation_url`: string (link to official documentation)
- `image_url`: string (optional)
- `is_active`: boolean (whether this model is currently supported)
- `parent_model_id`: string (optional, for models that extend others)
- `created_at`: timestamp
- `updated_at`: timestamp

**Invariants:**
- model_id must be unique
- name cannot be empty
- parent_model_id must reference valid model if specified

### 3. BillOfMaterials
Defines the parts required to build a specific robot model.

**Attributes:**
- `bom_id`: string (unique identifier)
- `robot_model_id`: string (foreign key to RobotModel)
- `version`: string (BOM version)
- `is_current`: boolean (indicates if this is the active BOM version)
- `items`: list[BOMItem]
- `notes`: string (optional)
- `created_at`: timestamp
- `updated_at`: timestamp

**Invariants:**
- Only one BOM per robot_model can have is_current = true
- All items must reference valid parts or robot models

### 4. BOMItem
Represents a single line item in a bill of materials.

**Attributes:**
- `item_id`: string (unique identifier)
- `bom_id`: string (foreign key to BillOfMaterials)
- `part_id`: string (optional, references Part)
- `sub_model_id`: string (optional, references RobotModel for hierarchical BOMs)
- `quantity`: integer (required quantity)
- `is_optional`: boolean (whether this part is optional)
- `notes`: string (optional, assembly notes)

**Invariants:**
- Either part_id OR sub_model_id must be specified (not both)
- quantity must be >= 1
- Referenced part_id or sub_model_id must exist

### 5. Inventory
Tracks current stock levels of parts.

**Attributes:**
- `inventory_id`: string (unique identifier)
- `part_id`: string (foreign key to Part)
- `quantity_loose`: integer (unassembled parts)
- `quantity_assembled`: integer (parts in completed assemblies)
- `quantity_reserved`: integer (parts allocated for future builds)
- `location`: string (optional, storage location)
- `reorder_point`: integer (minimum stock level)
- `reorder_quantity`: integer (standard reorder amount)
- `last_updated`: timestamp
- `updated_by`: string (user who last updated)

**Invariants:**
- All quantities must be >= 0
- quantity_reserved <= quantity_loose
- part_id must reference valid part

### 6. Assembly
Represents a completed or in-progress robot assembly.

**Attributes:**
- `assembly_id`: string (unique identifier)
- `robot_model_id`: string (foreign key to RobotModel)
- `serial_number`: string (unique serial for this assembly)
- `status`: AssemblyStatus (enum: PLANNED, IN_PROGRESS, COMPLETED, CANCELLED)
- `assembly_date`: date (when assembly was/will be completed)
- `notes`: string (optional)
- `parts_consumed`: list[ConsumedPart]
- `created_at`: timestamp
- `created_by`: string
- `updated_at`: timestamp

**Invariants:**
- serial_number must be unique
- assembly_date required if status is COMPLETED
- parts_consumed must match BOM requirements when COMPLETED

### 7. ConsumedPart
Tracks parts used in a specific assembly.

**Attributes:**
- `consumed_id`: string (unique identifier)
- `assembly_id`: string (foreign key to Assembly)
- `part_id`: string (foreign key to Part)
- `quantity`: integer
- `consumed_date`: timestamp

**Invariants:**
- quantity must be > 0
- part_id must reference valid part

### 8. Order
Represents a purchase order for parts.

**Attributes:**
- `order_id`: string (unique identifier)
- `order_number`: string (human-readable order number)
- `supplier`: string
- `status`: OrderStatus (enum: DRAFT, SUBMITTED, CONFIRMED, SHIPPED, RECEIVED, CANCELLED)
- `order_date`: date
- `expected_delivery`: date (optional)
- `items`: list[OrderItem]
- `total_cost`: decimal
- `notes`: string (optional)
- `created_at`: timestamp
- `created_by`: string

**Invariants:**
- order_number must be unique
- total_cost >= 0
- expected_delivery >= order_date if specified

### 9. OrderItem
Represents a line item in an order.

**Attributes:**
- `order_item_id`: string (unique identifier)
- `order_id`: string (foreign key to Order)
- `part_id`: string (foreign key to Part)
- `quantity`: integer
- `unit_cost`: decimal
- `line_total`: decimal

**Invariants:**
- quantity > 0
- unit_cost >= 0
- line_total = quantity * unit_cost

### 10. User
Represents a system user.

**Attributes:**
- `user_id`: string (unique identifier)
- `username`: string (unique)
- `email`: string (unique)
- `full_name`: string
- `role`: UserRole (enum: ADMIN, MANAGER, TECHNICIAN, VIEWER)
- `is_active`: boolean
- `created_at`: timestamp
- `last_login`: timestamp

**Invariants:**
- username and email must be unique
- email must be valid format

## Relationships

1. **RobotModel** can have parent/child relationships (hierarchical)
   - LeKiwi extends SO-ARM100
   - XLERobot extends LeKiwi

2. **BillOfMaterials** belongs to one **RobotModel**
   - One-to-many relationship
   - Multiple versions possible per model

3. **BOMItem** references either:
   - A **Part** (direct component)
   - Another **RobotModel** (sub-assembly)

4. **Inventory** tracks one **Part**
   - One-to-one relationship

5. **Assembly** is built from one **RobotModel**
   - Many assemblies can be created from one model

6. **ConsumedPart** links **Assembly** to **Part**
   - Many-to-many relationship with quantity

7. **Order** contains multiple **OrderItem**
   - One-to-many relationship

8. **OrderItem** references one **Part**
   - Many-to-one relationship

## Domain Services

### InventoryService
- `check_availability(robot_model_id, quantity) -> AvailabilityResult`
- `reserve_parts(robot_model_id, quantity) -> ReservationResult`
- `consume_parts(assembly_id, parts_list) -> ConsumptionResult`
- `release_reservation(reservation_id) -> ReleaseResult`
- `update_stock(part_id, quantity_change, reason) -> UpdateResult`

### AssemblyCalculator
- `calculate_buildable_quantity(robot_model_id) -> BuildableResult`
- `identify_bottlenecks(robot_model_id) -> list[BottleneckPart]`
- `calculate_parts_needed(robot_model_id, quantity) -> list[PartRequirement]`
- `optimize_build_mix(models_list) -> OptimizationResult`

### OrderService
- `generate_order_sheet(robot_model_id, quantity) -> OrderSheet`
- `create_order_from_shortages() -> Order`
- `calculate_order_cost(order_items) -> decimal`
- `track_order_status(order_id) -> OrderStatus`

### BOMService
- `expand_bom(robot_model_id) -> list[ExpandedBOMItem]`
- `validate_bom(bom_id) -> ValidationResult`
- `compare_bom_versions(bom_id1, bom_id2) -> ComparisonResult`
- `import_bom_from_source(source_url, format) -> BillOfMaterials`

## Value Objects

### PartRequirement
- `part_id`: string
- `required_quantity`: integer
- `available_quantity`: integer
- `shortage_quantity`: integer
- `is_critical`: boolean

### AvailabilityResult
- `can_build`: boolean
- `max_buildable`: integer
- `missing_parts`: list[PartRequirement]
- `warnings`: list[string]

### BuildableResult
- `robot_model_id`: string
- `max_quantity`: integer
- `limiting_parts`: list[PartRequirement]
- `partial_builds_possible`: integer

### BottleneckPart
- `part_id`: string
- `part_name`: string
- `available`: integer
- `required_per_unit`: integer
- `max_units_possible`: integer
- `shortage_for_next_unit`: integer

### OrderSheet
- `robot_model`: RobotModel
- `target_quantity`: integer
- `parts_needed`: list[PartRequirement]
- `grouped_by_supplier`: dict[string, list[PartRequirement]]
- `estimated_cost`: decimal
- `generation_date`: timestamp

## Aggregate Boundaries

1. **Part Aggregate**
   - Root: Part
   - Includes: Specifications

2. **Robot Model Aggregate**
   - Root: RobotModel
   - Includes: BillOfMaterials, BOMItem

3. **Inventory Aggregate**
   - Root: Inventory
   - Standalone aggregate for stock management

4. **Assembly Aggregate**
   - Root: Assembly
   - Includes: ConsumedPart

5. **Order Aggregate**
   - Root: Order
   - Includes: OrderItem

## Business Rules

1. **Inventory Rules**
   - Cannot reserve more parts than available loose inventory
   - Assembly consumption must match BOM requirements
   - Reorder triggered when quantity falls below reorder_point

2. **Assembly Rules**
   - Cannot complete assembly without all required parts
   - Serial numbers must be unique across all assemblies
   - Status transitions: PLANNED -> IN_PROGRESS -> COMPLETED

3. **BOM Rules**
   - Circular dependencies not allowed in hierarchical BOMs
   - Only one current version per robot model
   - Version changes require approval (audit trail)

4. **Order Rules**
   - Orders cannot be modified after SUBMITTED status
   - Minimum order quantities must be respected
   - Order cancellation only allowed in DRAFT or SUBMITTED status

## Events

1. **InventoryUpdated**
   - Triggered when stock levels change
   - Payload: part_id, old_quantity, new_quantity, reason

2. **AssemblyCompleted**
   - Triggered when assembly status changes to COMPLETED
   - Payload: assembly_id, robot_model_id, parts_consumed

3. **LowStockAlert**
   - Triggered when inventory falls below reorder_point
   - Payload: part_id, current_quantity, reorder_point

4. **OrderPlaced**
   - Triggered when order status changes to SUBMITTED
   - Payload: order_id, supplier, items, total_cost

5. **BOMVersionChanged**
   - Triggered when new BOM version becomes current
   - Payload: robot_model_id, old_version, new_version