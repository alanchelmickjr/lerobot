# BOM Calculator - Backend Pseudocode

## Module: Database Layer (database.py)

```pseudocode
CLASS DatabaseManager:
    INIT(database_path: string = "bom_calculator.db"):
        // TEST: Database connection established successfully
        // TEST: Tables created if not exist
        self.connection = create_sqlite_connection(database_path)
        self.initialize_schema()
    
    METHOD initialize_schema():
        // TEST: All required tables are created
        // TEST: Indexes are properly set up
        CREATE TABLE IF NOT EXISTS parts (
            part_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            unit_cost DECIMAL,
            supplier TEXT,
            is_assembly BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        
        CREATE TABLE IF NOT EXISTS robot_models (
            model_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            version TEXT,
            documentation_url TEXT,
            parent_model_id TEXT,
            is_active BOOLEAN DEFAULT TRUE
        )
        
        CREATE TABLE IF NOT EXISTS bom_items (
            item_id TEXT PRIMARY KEY,
            robot_model_id TEXT NOT NULL,
            part_id TEXT,
            sub_model_id TEXT,
            quantity INTEGER NOT NULL,
            is_optional BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (robot_model_id) REFERENCES robot_models(model_id),
            CHECK (part_id IS NOT NULL OR sub_model_id IS NOT NULL)
        )
        
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id TEXT PRIMARY KEY,
            part_id TEXT NOT NULL UNIQUE,
            quantity_loose INTEGER DEFAULT 0,
            quantity_assembled INTEGER DEFAULT 0,
            quantity_reserved INTEGER DEFAULT 0,
            reorder_point INTEGER DEFAULT 0,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (part_id) REFERENCES parts(part_id)
        )
        
        CREATE TABLE IF NOT EXISTS assemblies (
            assembly_id TEXT PRIMARY KEY,
            robot_model_id TEXT NOT NULL,
            serial_number TEXT UNIQUE,
            status TEXT NOT NULL,
            assembly_date DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    
    METHOD get_part(part_id: string) -> Part:
        // TEST: Returns correct part when exists
        // TEST: Returns None when part doesn't exist
        // TEST: Handles database errors gracefully
        query = "SELECT * FROM parts WHERE part_id = ?"
        result = execute_query(query, [part_id])
        IF result:
            RETURN Part.from_dict(result)
        RETURN None
    
    METHOD update_inventory(part_id: string, quantity_change: int, change_type: string) -> bool:
        // TEST: Inventory updated correctly for positive changes
        // TEST: Inventory updated correctly for negative changes
        // TEST: Cannot reduce inventory below zero
        // TEST: Audit trail created for changes
        BEGIN TRANSACTION
        TRY:
            current = get_inventory(part_id)
            IF change_type == "loose":
                new_quantity = current.quantity_loose + quantity_change
                IF new_quantity < 0:
                    RAISE ValueError("Cannot have negative inventory")
                UPDATE inventory SET quantity_loose = new_quantity
            COMMIT
            RETURN True
        CATCH Exception:
            ROLLBACK
            RETURN False
```

## Module: BOM Service (bom_service.py)

```pseudocode
CLASS BOMService:
    INIT(database: DatabaseManager):
        self.db = database
        self.cache = {}
    
    METHOD expand_bom(robot_model_id: string, multiplier: int = 1) -> dict[string, int]:
        // TEST: Correctly expands simple BOM without sub-models
        // TEST: Correctly expands hierarchical BOM with sub-models
        // TEST: Handles circular dependencies gracefully
        // TEST: Caches results for performance
        // TEST: Multiplier correctly scales quantities
        
        IF robot_model_id IN self.cache:
            cached_result = self.cache[robot_model_id].copy()
            FOR part_id, quantity IN cached_result:
                cached_result[part_id] = quantity * multiplier
            RETURN cached_result
        
        expanded_parts = {}
        bom_items = self.db.get_bom_items(robot_model_id)
        
        FOR item IN bom_items:
            IF item.part_id:
                // Direct part reference
                IF item.part_id IN expanded_parts:
                    expanded_parts[item.part_id] += item.quantity * multiplier
                ELSE:
                    expanded_parts[item.part_id] = item.quantity * multiplier
            ELIF item.sub_model_id:
                // Recursive expansion for sub-models
                // TEST: Detect circular dependencies
                IF item.sub_model_id == robot_model_id:
                    RAISE CircularDependencyError(f"Circular dependency detected: {robot_model_id}")
                
                sub_parts = expand_bom(item.sub_model_id, item.quantity * multiplier)
                FOR sub_part_id, sub_quantity IN sub_parts:
                    IF sub_part_id IN expanded_parts:
                        expanded_parts[sub_part_id] += sub_quantity
                    ELSE:
                        expanded_parts[sub_part_id] = sub_quantity
        
        self.cache[robot_model_id] = expanded_parts.copy()
        RETURN expanded_parts
    
    METHOD validate_bom(robot_model_id: string) -> ValidationResult:
        // TEST: Valid BOM passes validation
        // TEST: Missing parts detected
        // TEST: Circular dependencies detected
        // TEST: Invalid quantities detected
        
        result = ValidationResult()
        TRY:
            expanded = expand_bom(robot_model_id)
            
            FOR part_id IN expanded:
                part = self.db.get_part(part_id)
                IF NOT part:
                    result.add_error(f"Part {part_id} not found in database")
            
            IF expanded AND NOT result.has_errors():
                result.is_valid = True
        CATCH CircularDependencyError as e:
            result.add_error(str(e))
        
        RETURN result
    
    METHOD import_bom_from_json(json_data: dict, robot_model_id: string) -> bool:
        // TEST: Valid JSON imports successfully
        // TEST: Invalid JSON rejected
        // TEST: Duplicate parts handled correctly
        // TEST: Transaction rollback on error
        
        BEGIN TRANSACTION
        TRY:
            // Validate JSON structure
            IF NOT validate_json_schema(json_data):
                RAISE ValueError("Invalid BOM JSON format")
            
            // Create robot model if not exists
            model = RobotModel(
                model_id=robot_model_id,
                name=json_data["name"],
                description=json_data["description"],
                version=json_data["version"]
            )
            self.db.save_robot_model(model)
            
            // Import parts
            FOR part_data IN json_data["parts"]:
                part = Part(
                    part_id=part_data["id"],
                    name=part_data["name"],
                    category=part_data.get("category", "GENERAL")
                )
                self.db.save_part(part)
            
            // Import BOM items
            FOR item_data IN json_data["bom_items"]:
                item = BOMItem(
                    robot_model_id=robot_model_id,
                    part_id=item_data.get("part_id"),
                    sub_model_id=item_data.get("sub_model_id"),
                    quantity=item_data["quantity"]
                )
                self.db.save_bom_item(item)
            
            COMMIT
            RETURN True
        CATCH Exception as e:
            ROLLBACK
            LOG_ERROR(f"BOM import failed: {e}")
            RETURN False
```

## Module: Assembly Calculator (assembly_calculator.py)

```pseudocode
CLASS AssemblyCalculator:
    INIT(database: DatabaseManager, bom_service: BOMService):
        self.db = database
        self.bom_service = bom_service
    
    METHOD calculate_buildable_quantity(robot_model_id: string) -> BuildableResult:
        // TEST: Correctly calculates when all parts available
        // TEST: Correctly identifies bottleneck parts
        // TEST: Returns zero when critical part missing
        // TEST: Handles hierarchical BOMs correctly
        // TEST: Considers reserved inventory
        
        expanded_bom = self.bom_service.expand_bom(robot_model_id)
        inventory_status = {}
        limiting_parts = []
        max_buildable = INFINITY
        
        FOR part_id, required_quantity IN expanded_bom:
            inventory = self.db.get_inventory(part_id)
            available = inventory.quantity_loose - inventory.quantity_reserved
            
            inventory_status[part_id] = {
                "required": required_quantity,
                "available": available,
                "possible_units": available // required_quantity
            }
            
            IF inventory_status[part_id]["possible_units"] < max_buildable:
                max_buildable = inventory_status[part_id]["possible_units"]
                limiting_parts = [part_id]
            ELIF inventory_status[part_id]["possible_units"] == max_buildable:
                limiting_parts.append(part_id)
        
        IF max_buildable == INFINITY:
            max_buildable = 0
        
        RETURN BuildableResult(
            robot_model_id=robot_model_id,
            max_quantity=max_buildable,
            limiting_parts=limiting_parts,
            inventory_status=inventory_status
        )
    
    METHOD calculate_parts_needed(robot_model_id: string, target_quantity: int) -> list[PartRequirement]:
        // TEST: Correctly calculates parts for target quantity
        // TEST: Subtracts current inventory from requirements
        // TEST: Identifies shortages accurately
        // TEST: Handles zero target quantity
        
        IF target_quantity <= 0:
            RETURN []
        
        expanded_bom = self.bom_service.expand_bom(robot_model_id, target_quantity)
        requirements = []
        
        FOR part_id, total_needed IN expanded_bom:
            inventory = self.db.get_inventory(part_id)
            available = inventory.quantity_loose - inventory.quantity_reserved
            shortage = max(0, total_needed - available)
            
            requirement = PartRequirement(
                part_id=part_id,
                required_quantity=total_needed,
                available_quantity=available,
                shortage_quantity=shortage,
                is_critical=(shortage > 0)
            )
            requirements.append(requirement)
        
        RETURN requirements
    
    METHOD optimize_build_mix(robot_models: list[tuple[string, int]]) -> OptimizationResult:
        // TEST: Finds optimal mix when resources limited
        // TEST: Prioritizes based on constraints
        // TEST: Handles impossible combinations
        // TEST: Maximizes total output
        
        // Collect all parts needed
        total_requirements = {}
        FOR model_id, desired_quantity IN robot_models:
            expanded = self.bom_service.expand_bom(model_id, desired_quantity)
            FOR part_id, quantity IN expanded:
                IF part_id IN total_requirements:
                    total_requirements[part_id] += quantity
                ELSE:
                    total_requirements[part_id] = quantity
        
        // Check inventory constraints
        constraints = []
        FOR part_id, needed IN total_requirements:
            inventory = self.db.get_inventory(part_id)
            available = inventory.quantity_loose - inventory.quantity_reserved
            IF available < needed:
                constraints.append({
                    "part_id": part_id,
                    "available": available,
                    "needed": needed,
                    "shortage": needed - available
                })
        
        // Optimize if constraints exist
        IF constraints:
            // Use linear programming or heuristic to find best mix
            optimized_quantities = optimize_with_constraints(
                robot_models, total_requirements, constraints
            )
        ELSE:
            optimized_quantities = {model_id: qty FOR model_id, qty IN robot_models}
        
        RETURN OptimizationResult(
            requested=robot_models,
            optimized=optimized_quantities,
            constraints=constraints
        )
```

## Module: Inventory Service (inventory_service.py)

```pseudocode
CLASS InventoryService:
    INIT(database: DatabaseManager):
        self.db = database
        self.observers = []
    
    METHOD update_stock(part_id: string, quantity_change: int, reason: string) -> UpdateResult:
        // TEST: Stock increases correctly
        // TEST: Stock decreases correctly
        // TEST: Prevents negative stock
        // TEST: Audit trail created
        // TEST: Notifications sent for low stock
        
        BEGIN TRANSACTION
        TRY:
            current_inventory = self.db.get_inventory(part_id)
            IF NOT current_inventory:
                current_inventory = Inventory(part_id=part_id)
            
            new_quantity = current_inventory.quantity_loose + quantity_change
            IF new_quantity < 0:
                RAISE InsufficientStockError(f"Cannot reduce stock below 0 for {part_id}")
            
            current_inventory.quantity_loose = new_quantity
            current_inventory.last_updated = NOW()
            
            self.db.save_inventory(current_inventory)
            
            // Create audit record
            audit = InventoryAudit(
                part_id=part_id,
                change_quantity=quantity_change,
                reason=reason,
                timestamp=NOW(),
                resulting_quantity=new_quantity
            )
            self.db.save_audit(audit)
            
            // Check for low stock alert
            IF new_quantity <= current_inventory.reorder_point:
                self.notify_low_stock(part_id, new_quantity)
            
            COMMIT
            RETURN UpdateResult(success=True, new_quantity=new_quantity)
        CATCH Exception as e:
            ROLLBACK
            RETURN UpdateResult(success=False, error=str(e))
    
    METHOD reserve_parts(robot_model_id: string, quantity: int) -> ReservationResult:
        // TEST: Successfully reserves available parts
        // TEST: Fails when insufficient parts
        // TEST: Atomic transaction for all parts
        // TEST: Reservation can be cancelled
        
        bom_service = BOMService(self.db)
        expanded_bom = bom_service.expand_bom(robot_model_id, quantity)
        reservation_id = generate_uuid()
        
        BEGIN TRANSACTION
        TRY:
            reserved_parts = []
            FOR part_id, needed_quantity IN expanded_bom:
                inventory = self.db.get_inventory(part_id)
                available = inventory.quantity_loose - inventory.quantity_reserved
                
                IF available < needed_quantity:
                    RAISE InsufficientStockError(
                        f"Insufficient stock for {part_id}: need {needed_quantity}, have {available}"
                    )
                
                inventory.quantity_reserved += needed_quantity
                self.db.save_inventory(inventory)
                
                reserved_parts.append({
                    "part_id": part_id,
                    "quantity": needed_quantity
                })
            
            // Save reservation record
            reservation = Reservation(
                reservation_id=reservation_id,
                robot_model_id=robot_model_id,
                quantity=quantity,
                parts=reserved_parts,
                created_at=NOW(),
                expires_at=NOW() + HOURS(24)
            )
            self.db.save_reservation(reservation)
            
            COMMIT
            RETURN ReservationResult(
                success=True,
                reservation_id=reservation_id,
                reserved_parts=reserved_parts
            )
        CATCH Exception as e:
            ROLLBACK
            RETURN ReservationResult(success=False, error=str(e))
    
    METHOD consume_parts(assembly_id: string, parts_list: list[dict]) -> ConsumptionResult:
        // TEST: Parts consumed correctly from inventory
        // TEST: Assembly record updated
        // TEST: Cannot consume more than available
        // TEST: Audit trail created
        
        BEGIN TRANSACTION
        TRY:
            consumed_records = []
            FOR part IN parts_list:
                inventory = self.db.get_inventory(part["part_id"])
                IF inventory.quantity_loose < part["quantity"]:
                    RAISE InsufficientStockError(
                        f"Cannot consume {part['quantity']} of {part['part_id']}"
                    )
                
                inventory.quantity_loose -= part["quantity"]
                inventory.quantity_assembled += part["quantity"]
                self.db.save_inventory(inventory)
                
                consumed = ConsumedPart(
                    assembly_id=assembly_id,
                    part_id=part["part_id"],
                    quantity=part["quantity"],
                    consumed_date=NOW()
                )
                self.db.save_consumed_part(consumed)
                consumed_records.append(consumed)
            
            // Update assembly status
            assembly = self.db.get_assembly(assembly_id)
            assembly.status = "IN_PROGRESS"
            self.db.save_assembly(assembly)
            
            COMMIT
            RETURN ConsumptionResult(success=True, consumed_parts=consumed_records)
        CATCH Exception as e:
            ROLLBACK
            RETURN ConsumptionResult(success=False, error=str(e))
```

## Module: Order Service (order_service.py)

```pseudocode
CLASS OrderService:
    INIT(database: DatabaseManager, assembly_calculator: AssemblyCalculator):
        self.db = database
        self.calculator = assembly_calculator
    
    METHOD generate_order_sheet(robot_model_id: string, quantity: int) -> OrderSheet:
        // TEST: Generates complete order sheet
        // TEST: Groups by supplier correctly
        // TEST: Calculates costs accurately
        // TEST: Respects minimum order quantities
        // TEST: Includes lead times
        
        parts_needed = self.calculator.calculate_parts_needed(robot_model_id, quantity)
        order_items = []
        grouped_by_supplier = {}
        total_cost = 0
        
        FOR requirement IN parts_needed:
            IF requirement.shortage_quantity > 0:
                part = self.db.get_part(requirement.part_id)
                
                // Adjust for minimum order quantity
                order_quantity = requirement.shortage_quantity
                IF part.minimum_order_quantity:
                    order_quantity = max(order_quantity, part.minimum_order_quantity)
                    order_quantity = ceil(requirement.shortage_quantity / part.minimum_order_quantity) * part.minimum_order_quantity
                
                order_item = {
                    "part_id": requirement.part_id,
                    "part_name": part.name,
                    "quantity_needed": requirement.shortage_quantity,
                    "quantity_to_order": order_quantity,
                    "unit_cost": part.unit_cost OR 0,
                    "line_total": order_quantity * (part.unit_cost OR 0),
                    "supplier": part.supplier OR "Unknown",
                    "lead_time_days": part.lead_time_days OR 0
                }
                
                order_items.append(order_item)
                total_cost += order_item["line_total"]
                
                // Group by supplier
                supplier = order_item["supplier"]
                IF supplier NOT IN grouped_by_supplier:
                    grouped_by_supplier[supplier] = []
                grouped_by_supplier[supplier].append(order_item)
        
        RETURN OrderSheet(
            robot_model_id=robot_model_id,
            target_quantity=quantity,
            order_items=order_items,
            grouped_by_supplier=grouped_by_supplier,
            estimated_cost=total_cost,
            generation_date=NOW()
        )
    
    METHOD create_order_from_sheet(order_sheet: OrderSheet) -> Order:
        // TEST: Order created with correct items
        // TEST: Order number generated uniquely
        // TEST: Status set to DRAFT initially
        // TEST: Can be submitted later
        
        order = Order(
            order_id=generate_uuid(),
            order_number=generate_order_number(),
            status="DRAFT",
            order_date=NOW(),
            items=[],
            total_cost=order_sheet.estimated_cost
        )
        
        FOR item IN order_sheet.order_items:
            order_item = OrderItem(
                order_id=order.order_id,
                part_id=item["part_id"],
                quantity=item["quantity_to_order"],
                unit_cost=item["unit_cost"],
                line_total=item["line_total"]
            )
            order.items.append(order_item)
        
        self.db.save_order(order)
        RETURN order
```

## Module: API Endpoints (api.py)

```pseudocode
CLASS BOMCalculatorAPI:
    INIT(database_path: string = "bom_calculator.db"):
        self.db = DatabaseManager(database_path)
        self.bom_service = BOMService(self.db)
        self.assembly_calculator = AssemblyCalculator(self.db, self.bom_service)
        self.inventory_service = InventoryService(self.db)
        self.order_service = OrderService(self.db, self.assembly_calculator)
    
    @GET("/api/inventory")
    METHOD get_inventory() -> JSONResponse:
        // TEST: Returns all inventory items
        // TEST: Handles empty inventory
        // TEST: Returns proper JSON format
        
        inventory_items = self.db.get_all_inventory()
        RETURN JSONResponse({
            "success": True,
            "data": [item.to_dict() FOR item IN inventory_items]
        })
    
    @POST("/api/inventory/update")
    METHOD update_inventory(request: InventoryUpdateRequest) -> JSONResponse:
        // TEST: Updates single part inventory
        // TEST: Validates input data
        // TEST: Returns error for invalid part
        // TEST: Handles concurrent updates
        
        VALIDATE request.part_id IS NOT EMPTY
        VALIDATE request.quantity IS INTEGER
        
        result = self.inventory_service.update_stock(
            part_id=request.part_id,
            quantity_change=request.quantity,
            reason=request.reason OR "Manual update"
        )
        
        IF result.success:
            RETURN JSONResponse({
                "success": True,
                "new_quantity": result.new_quantity
            })
        ELSE:
            RETURN JSONResponse({
                "success": False,
                "error": result.error
            }, status_code=400)
    
    @GET("/api/calculate/{robot_model_id}")
    METHOD calculate_buildable(robot_model_id: string) -> JSONResponse:
        // TEST: Calculates buildable quantity correctly
        // TEST: Returns bottleneck information
        // TEST: Handles invalid model ID
        
        TRY:
            result = self.assembly_calculator.calculate_buildable_quantity(robot_model_id)
            RETURN JSONResponse({
                "success": True,
                "data": {
                    "model_id": result.robot_model_id,
                    "max_buildable": result.max_quantity,
                    "limiting_parts": result.limiting_parts,
                    "inventory_status": result.inventory_status
                }
            })
        CATCH Exception as e:
            RETURN JSONResponse({
                "success": False,
                "error": str(e)
            }, status_code=400)
    
    @POST("/api/order/generate")
    METHOD generate_order(request: OrderGenerationRequest) -> JSONResponse:
        // TEST: Generates order sheet for valid request
        // TEST: Validates model and quantity
        // TEST: Returns downloadable format
        
        VALIDATE request.robot_model_id IS NOT EMPTY
        VALIDATE request.quantity > 0
        
        order_sheet = self.order_service.generate_order_sheet(
            robot_model_id=request.robot_model_id,
            quantity=request.quantity
        )
        
        RETURN JSONResponse({
            "success": True,
            "data": order_sheet.to_dict()
        })
    
    @POST("/api/assembly/create")
    METHOD create_assembly(request: AssemblyCreationRequest) -> JSONResponse:
        // TEST: Creates assembly record
        // TEST: Reserves parts successfully
        // TEST: Generates unique serial number
        
        serial_number = generate_serial_number(request.robot_model_id)
        
        assembly = Assembly(
            assembly_id=generate_uuid(),
            robot_model_id=request.robot_model_id,
            serial_number=serial_number,
            status="PLANNED",
            notes=request.notes
        )
        
        // Reserve parts
        reservation_result = self.inventory_service.reserve_parts(
            robot_model_id=request.robot_model_id,
            quantity=1
        )
        
        IF reservation_result.success:
            assembly.reservation_id = reservation_result.reservation_id
            self.db.save_assembly(assembly)
            RETURN JSONResponse({
                "success": True,
                "data": {
                    "assembly_id": assembly.assembly_id,
                    "serial_number": assembly.serial_number,
                    "reservation_id": assembly.reservation_id
                }
            })
        ELSE:
            RETURN JSONResponse({
                "success": False,
                "error": reservation_result.error
            }, status_code=400)
    
    @GET("/api/bom/{robot_model_id}")
    METHOD get_bom(robot_model_id: string) -> JSONResponse:
        // TEST: Returns expanded BOM
        // TEST: Handles hierarchical BOMs
        // TEST: Returns proper structure
        
        expanded_bom = self.bom_service.expand_bom(robot_model_id)
        bom_items = []
        
        FOR part_id, quantity IN expanded_bom:
            part = self.db.get_part(part_id)
            bom_items.append({
                "part_id": part_id,
                "part_name": part.name IF part ELSE "Unknown",
                "quantity": quantity,
                "category": part.category IF part ELSE "Unknown"
            })
        
        RETURN JSONResponse({
            "success": True,
            "data": {
                "robot_model_id": robot_model_id,
                "items": bom_items
            }
        })
    
    @POST("/api/bom/import")
    METHOD import_bom(request: BOMImportRequest) -> JSONResponse:
        // TEST: Imports valid BOM data
        // TEST: Rejects invalid format
        // TEST: Handles duplicates
        
        VALIDATE request.robot_model_id IS NOT EMPTY
        VALIDATE request.bom_data IS NOT EMPTY
        
        success = self.bom_service.import_bom_from_json(
            json_data=request.bom_data,
            robot_model_id=request.robot_model_id
        )
        
        IF success:
            RETURN JSONResponse({
                "success": True,
                "message": f"BOM imported for {request.robot_model_id}"
            })
        ELSE:
            RETURN JSONResponse({
                "success": False,
                "error": "Failed to import BOM"
            }, status_code=400)
    
    @GET("/api/export/inventory")
    METHOD export_inventory() -> FileResponse:
        // TEST: Exports inventory as CSV
        // TEST: Includes all fields
        // TEST: Proper CSV format
        
        inventory_items = self.db.get_all_inventory()
        csv_content = "Part ID,Part Name,Quantity Loose,Quantity Assembled,Quantity Reserved,Reorder Point\n"
        
        FOR item IN inventory_items:
            part = self.db.get_part(item.part_id)
            csv_content += f"{item.part_id},{part.name},{item.quantity_loose},"
            csv_content += f"{item.quantity_assembled},{item.quantity_reserved},{item.reorder_point}\n"
        
        RETURN FileResponse(
            content=csv_content,
            media_type="text/csv",
            filename="inventory_export.csv"
        )