# BOM Calculator - Frontend Pseudocode

## Module: Main Application Component (App.tsx)

```pseudocode
COMPONENT BOMCalculatorApp:
    STATE:
        inventory: Map<string, InventoryItem>
        robotModels: Array<RobotModel>
        buildableResults: Map<string, BuildableResult>
        selectedTab: string = "inventory"
        isLoading: boolean = false
        error: string | null = null
        lastSync: timestamp | null = null
        
    LIFECYCLE_HOOK componentDidMount():
        // TEST: Loads initial data on mount
        // TEST: Handles API failures gracefully
        // TEST: Shows loading state during fetch
        
        SET isLoading = true
        TRY:
            inventory = AWAIT fetchInventory()
            robotModels = AWAIT fetchRobotModels()
            buildableResults = AWAIT calculateAllBuildable()
            lastSync = NOW()
        CATCH error:
            SET error = "Failed to load initial data"
            SHOW_TOAST(error, "error")
        FINALLY:
            SET isLoading = false
    
    METHOD handleTabSwitch(tabName: string):
        // TEST: Switches between tabs correctly
        // TEST: Maintains state when switching tabs
        // TEST: Updates URL for bookmarking
        
        SET selectedTab = tabName
        UPDATE_URL_PARAMS({tab: tabName})
    
    RENDER():
        // TEST: Renders loading state
        // TEST: Renders error state
        // TEST: Renders main content when loaded
        
        RETURN (
            <Container>
                <Header 
                    onExportInventory={exportInventory}
                    onGenerateOrder={openOrderDialog}
                    lastSync={lastSync}
                />
                
                <TabNavigation 
                    activeTab={selectedTab}
                    onTabChange={handleTabSwitch}
                    tabs={["inventory", "assembly", "orders", "settings"]}
                />
                
                {isLoading && <LoadingSpinner />}
                {error && <ErrorMessage message={error} />}
                
                {!isLoading && !error && (
                    <TabContent>
                        {selectedTab === "inventory" && 
                            <InventoryTab 
                                inventory={inventory}
                                onInventoryUpdate={updateInventory}
                            />
                        }
                        {selectedTab === "assembly" && 
                            <AssemblyTab 
                                buildableResults={buildableResults}
                                robotModels={robotModels}
                            />
                        }
                        {selectedTab === "orders" && 
                            <OrdersTab 
                                onGenerateOrder={generateOrderSheet}
                            />
                        }
                        {selectedTab === "settings" && 
                            <SettingsTab 
                                robotModels={robotModels}
                                onImportBOM={importBOM}
                            />
                        }
                    </TabContent>
                )}
            </Container>
        )
```

## Module: Inventory Management Component (InventoryTab.tsx)

```pseudocode
COMPONENT InventoryTab:
    PROPS:
        inventory: Map<string, InventoryItem>
        onInventoryUpdate: Function
    
    STATE:
        searchTerm: string = ""
        filterCategory: string = "all"
        sortBy: string = "name"
        editingItem: string | null = null
        bulkEditMode: boolean = false
        selectedItems: Set<string> = new Set()
        
    METHOD handleSearch(term: string):
        // TEST: Filters inventory by search term
        // TEST: Case-insensitive search
        // TEST: Searches multiple fields
        
        SET searchTerm = term.toLowerCase()
    
    METHOD handleQuantityChange(partId: string, newQuantity: number):
        // TEST: Updates quantity for positive values
        // TEST: Prevents negative quantities
        // TEST: Debounces API calls
        // TEST: Shows optimistic updates
        
        IF newQuantity < 0:
            SHOW_TOAST("Quantity cannot be negative", "warning")
            RETURN
        
        // Optimistic update
        UPDATE_LOCAL_STATE(partId, newQuantity)
        
        // Debounced API call
        DEBOUNCE(500ms):
            TRY:
                result = AWAIT updateInventoryAPI(partId, newQuantity)
                IF NOT result.success:
                    ROLLBACK_LOCAL_STATE(partId)
                    SHOW_TOAST("Failed to update inventory", "error")
            CATCH error:
                ROLLBACK_LOCAL_STATE(partId)
                SHOW_TOAST("Network error", "error")
    
    METHOD handleBulkUpdate():
        // TEST: Updates multiple items at once
        // TEST: Shows progress during bulk update
        // TEST: Handles partial failures
        
        IF selectedItems.size === 0:
            SHOW_TOAST("No items selected", "warning")
            RETURN
        
        SHOW_PROGRESS_DIALOG()
        
        updates = []
        FOR partId IN selectedItems:
            updates.push({
                partId: partId,
                quantity: inventory[partId].quantity
            })
        
        TRY:
            result = AWAIT bulkUpdateInventoryAPI(updates)
            SHOW_TOAST(`Updated ${result.successCount} items`, "success")
            IF result.failures.length > 0:
                SHOW_ERROR_DETAILS(result.failures)
        CATCH error:
            SHOW_TOAST("Bulk update failed", "error")
        FINALLY:
            HIDE_PROGRESS_DIALOG()
            SET selectedItems = new Set()
            SET bulkEditMode = false
    
    METHOD renderInventoryTable():
        // TEST: Renders all inventory items
        // TEST: Applies filters correctly
        // TEST: Sorts by selected column
        // TEST: Highlights low stock items
        
        filteredInventory = inventory.filter(item => {
            matchesSearch = item.name.toLowerCase().includes(searchTerm) OR
                          item.partId.toLowerCase().includes(searchTerm)
            matchesCategory = filterCategory === "all" OR 
                            item.category === filterCategory
            RETURN matchesSearch AND matchesCategory
        })
        
        sortedInventory = filteredInventory.sort((a, b) => {
            SWITCH sortBy:
                CASE "name": RETURN a.name.localeCompare(b.name)
                CASE "quantity": RETURN a.quantity - b.quantity
                CASE "category": RETURN a.category.localeCompare(b.category)
                CASE "value": RETURN (a.quantity * a.unitCost) - (b.quantity * b.unitCost)
        })
        
        RETURN (
            <Table>
                <TableHeader>
                    <TableRow>
                        {bulkEditMode && <Checkbox />}
                        <TableCell onClick={() => setSortBy("name")}>Part Name</TableCell>
                        <TableCell onClick={() => setSortBy("category")}>Category</TableCell>
                        <TableCell onClick={() => setSortBy("quantity")}>Quantity</TableCell>
                        <TableCell>Reorder Point</TableCell>
                        <TableCell>Actions</TableCell>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {sortedInventory.map(item => (
                        <TableRow 
                            key={item.partId}
                            className={item.quantity <= item.reorderPoint ? "low-stock" : ""}
                        >
                            {bulkEditMode && 
                                <Checkbox 
                                    checked={selectedItems.has(item.partId)}
                                    onChange={() => toggleSelection(item.partId)}
                                />
                            }
                            <TableCell>{item.name}</TableCell>
                            <TableCell>
                                <CategoryBadge category={item.category} />
                            </TableCell>
                            <TableCell>
                                {editingItem === item.partId ? (
                                    <QuantityInput 
                                        value={item.quantity}
                                        onChange={(val) => handleQuantityChange(item.partId, val)}
                                        onBlur={() => setEditingItem(null)}
                                    />
                                ) : (
                                    <QuantityDisplay 
                                        value={item.quantity}
                                        onClick={() => setEditingItem(item.partId)}
                                    />
                                )}
                            </TableCell>
                            <TableCell>
                                {item.reorderPoint}
                                {item.quantity <= item.reorderPoint && 
                                    <WarningIcon title="Below reorder point" />
                                }
                            </TableCell>
                            <TableCell>
                                <ActionButtons 
                                    onEdit={() => openEditDialog(item)}
                                    onHistory={() => showHistory(item.partId)}
                                    onDelete={() => confirmDelete(item.partId)}
                                />
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        )
    
    RENDER():
        RETURN (
            <div className="inventory-tab">
                <InventoryToolbar>
                    <SearchInput 
                        value={searchTerm}
                        onChange={handleSearch}
                        placeholder="Search parts..."
                    />
                    <CategoryFilter 
                        value={filterCategory}
                        onChange={setFilterCategory}
                        categories={getUniqueCategories(inventory)}
                    />
                    <Button 
                        onClick={() => setBulkEditMode(!bulkEditMode)}
                        variant={bulkEditMode ? "primary" : "secondary"}
                    >
                        {bulkEditMode ? "Cancel Bulk Edit" : "Bulk Edit"}
                    </Button>
                    {bulkEditMode && selectedItems.size > 0 && 
                        <Button onClick={handleBulkUpdate}>
                            Update {selectedItems.size} Items
                        </Button>
                    }
                </InventoryToolbar>
                
                <InventoryStats 
                    totalParts={inventory.size}
                    totalValue={calculateTotalValue(inventory)}
                    lowStockCount={countLowStock(inventory)}
                />
                
                {renderInventoryTable()}
            </div>
        )
```

## Module: Assembly Calculator Component (AssemblyTab.tsx)

```pseudocode
COMPONENT AssemblyTab:
    PROPS:
        buildableResults: Map<string, BuildableResult>
        robotModels: Array<RobotModel>
    
    STATE:
        selectedModel: string | null = null
        targetQuantity: number = 1
        showDetails: boolean = false
        comparisonMode: boolean = false
        compareModels: Set<string> = new Set()
        
    METHOD calculateBuildable(modelId: string):
        // TEST: Calculates correct buildable quantity
        // TEST: Identifies bottleneck parts
        // TEST: Updates when inventory changes
        // TEST: Handles hierarchical BOMs
        
        result = AWAIT calculateBuildableAPI(modelId)
        UPDATE_STATE(buildableResults, modelId, result)
        
        IF result.maxBuildable === 0:
            IDENTIFY_CRITICAL_SHORTAGES(result)
            SUGGEST_ALTERNATIVES(modelId)
    
    METHOD handleModelSelection(modelId: string):
        // TEST: Loads model details
        // TEST: Updates buildable calculation
        // TEST: Shows BOM breakdown
        
        SET selectedModel = modelId
        SET showDetails = true
        
        IF NOT buildableResults.has(modelId):
            calculateBuildable(modelId)
    
    METHOD renderBuildableCard(model: RobotModel):
        // TEST: Shows buildable quantity
        // TEST: Highlights bottlenecks
        // TEST: Shows visual indicators
        
        result = buildableResults.get(model.id)
        
        RETURN (
            <Card 
                className="buildable-card"
                onClick={() => handleModelSelection(model.id)}
            >
                <CardHeader>
                    <ModelIcon model={model} />
                    <Title>{model.name}</Title>
                    {comparisonMode && 
                        <Checkbox 
                            checked={compareModels.has(model.id)}
                            onChange={() => toggleComparison(model.id)}
                        />
                    }
                </CardHeader>
                <CardBody>
                    <BuildableQuantity 
                        value={result?.maxBuildable || 0}
                        size="large"
                    />
                    <Description>{model.description}</Description>
                    
                    {result?.limitingParts.length > 0 && (
                        <LimitingParts>
                            <Label>Limited by:</Label>
                            {result.limitingParts.slice(0, 3).map(partId => (
                                <PartChip 
                                    key={partId}
                                    partId={partId}
                                    onClick={() => highlightPart(partId)}
                                />
                            ))}
                            {result.limitingParts.length > 3 && 
                                <MoreChip count={result.limitingParts.length - 3} />
                            }
                        </LimitingParts>
                    )}
                    
                    <ProgressBar 
                        value={calculateCompleteness(result)}
                        color={getProgressColor(result)}
                    />
                </CardBody>
                <CardFooter>
                    <Button 
                        size="small"
                        onClick={() => openAssemblyWizard(model.id)}
                    >
                        Start Assembly
                    </Button>
                    <Button 
                        size="small"
                        variant="secondary"
                        onClick={() => generateOrderForModel(model.id)}
                    >
                        Order Parts
                    </Button>
                </CardFooter>
            </Card>
        )
    
    METHOD renderDetailsPanel():
        // TEST: Shows complete BOM breakdown
        // TEST: Highlights available/missing parts
        // TEST: Calculates partial assemblies
        
        IF NOT selectedModel:
            RETURN null
        
        model = robotModels.find(m => m.id === selectedModel)
        result = buildableResults.get(selectedModel)
        
        RETURN (
            <DetailsPanel>
                <PanelHeader>
                    <Title>{model.name} - Assembly Details</Title>
                    <CloseButton onClick={() => setShowDetails(false)} />
                </PanelHeader>
                
                <PanelBody>
                    <Section title="Build Capacity">
                        <Metric 
                            label="Complete Units"
                            value={result.maxBuildable}
                            icon="complete"
                        />
                        <Metric 
                            label="Partial Assemblies"
                            value={calculatePartialAssemblies(result)}
                            icon="partial"
                        />
                    </Section>
                    
                    <Section title="Parts Requirements">
                        <BOMTable>
                            {result.expandedBOM.map(item => (
                                <BOMRow key={item.partId}>
                                    <PartName>{item.partName}</PartName>
                                    <Quantity>
                                        <Available>{item.available}</Available>
                                        <Separator>/</Separator>
                                        <Required>{item.required}</Required>
                                    </Quantity>
                                    <Status>
                                        {item.available >= item.required ? (
                                            <CheckIcon color="green" />
                                        ) : (
                                            <WarningIcon 
                                                color="red"
                                                title={`Short by ${item.required - item.available}`}
                                            />
                                        )}
                                    </Status>
                                </BOMRow>
                            ))}
                        </BOMTable>
                    </Section>
                    
                    <Section title="Assembly Optimizer">
                        <TargetQuantityInput>
                            <Label>Target Quantity:</Label>
                            <NumberInput 
                                value={targetQuantity}
                                onChange={setTargetQuantity}
                                min={1}
                                max={100}
                            />
                            <Button onClick={() => optimizeForTarget(targetQuantity)}>
                                Optimize
                            </Button>
                        </TargetQuantityInput>
                        
                        {targetQuantity > result.maxBuildable && (
                            <ShortageAlert>
                                <AlertIcon />
                                <Message>
                                    Need to order parts for {targetQuantity - result.maxBuildable} more units
                                </Message>
                                <Button 
                                    variant="primary"
                                    onClick={() => generateOrderForQuantity(selectedModel, targetQuantity - result.maxBuildable)}
                                >
                                    Generate Order
                                </Button>
                            </ShortageAlert>
                        )}
                    </Section>
                </PanelBody>
            </DetailsPanel>
        )
    
    RENDER():
        RETURN (
            <div className="assembly-tab">
                <AssemblyToolbar>
                    <Button 
                        onClick={() => setComparisonMode(!comparisonMode)}
                        variant={comparisonMode ? "primary" : "secondary"}
                    >
                        {comparisonMode ? "Exit Comparison" : "Compare Models"}
                    </Button>
                    {comparisonMode && compareModels.size >= 2 && 
                        <Button onClick={showComparisonMatrix}>
                            Compare Selected ({compareModels.size})
                        </Button>
                    }
                    <RefreshButton onClick={recalculateAll} />
                </AssemblyToolbar>
                
                <ModelGrid>
                    {robotModels.map(model => renderBuildableCard(model))}
                </ModelGrid>
                
                {showDetails && renderDetailsPanel()}
                
                {comparisonMode && compareModels.size >= 2 && 
                    <ComparisonMatrix 
                        models={Array.from(compareModels)}
                        buildableResults={buildableResults}
                    />
                }
            </div>
        )
```

## Module: Order Management Component (OrdersTab.tsx)

```pseudocode
COMPONENT OrdersTab:
    PROPS:
        onGenerateOrder: Function
    
    STATE:
        orders: Array<Order> = []
        selectedOrder: Order | null = null
        showGenerateDialog: boolean = false
        generationParams: OrderGenerationParams = {}
        isGenerating: boolean = false
        
    METHOD generateOrderSheet(params: OrderGenerationParams):
        // TEST: Generates complete order sheet
        // TEST: Groups by supplier
        // TEST: Respects minimum quantities
        // TEST: Calculates shipping estimates
        
        SET isGenerating = true
        
        TRY:
            orderSheet = AWAIT generateOrderSheetAPI(params)
            
            // Process and group items
            groupedItems = groupBySupplier(orderSheet.items)
            
            // Calculate totals
            subtotal = calculateSubtotal(orderSheet.items)
            shipping = estimateShipping(groupedItems)
            tax = calculateTax(subtotal)
            total = subtotal + shipping + tax
            
            // Create order record
            order = {
                id: generateOrderId(),
                date: NOW(),
                status: "DRAFT",
                items: orderSheet.items,
                groupedItems: groupedItems,
                totals: {
                    subtotal: subtotal,
                    shipping: shipping,
                    tax: tax,
                    total: total
                },
                params: params
            }
            
            ADD_TO_STATE(orders, order)
            SET selectedOrder = order
            SET showGenerateDialog = false
            
            SHOW_TOAST("Order sheet generated successfully", "success")
        CATCH error:
            SHOW_TOAST("Failed to generate order sheet", "error")
        FINALLY:
            SET isGenerating = false
    
    METHOD exportOrder(order: Order, format: string):
        // TEST: Exports to CSV format
        // TEST: Exports to PDF format
        // TEST: Exports to Excel format
        // TEST: Includes all necessary fields
        
        SWITCH format:
            CASE "csv":
                csvContent = convertOrderToCSV(order)
                downloadFile(csvContent, `order_${order.id}.csv`, "text/csv")
            
            CASE "pdf":
                pdfBlob = AWAIT generateOrderPDF(order)
                downloadFile(pdfBlob, `order_${order.id}.pdf`, "application/pdf")
            
            CASE "excel":
                excelBlob = AWAIT generateOrderExcel(order)
                downloadFile(excelBlob, `order_${order.id}.xlsx`, "application/vnd.ms-excel")
            
            DEFAULT:
                SHOW_TOAST("Unsupported format", "error")
    
    METHOD renderOrderGenerationDialog():
        // TEST: Shows model selection
        // TEST: Validates quantity input
        // TEST: Shows cost preview
        
        RETURN (
            <Dialog 
                isOpen={showGenerateDialog}
                onClose={() => setShowGenerateDialog(false)}
            >
                <DialogHeader>Generate Order Sheet</DialogHeader>
                <DialogBody>
                    <FormGroup>
                        <Label>Robot Model</Label>
                        <Select 
                            value={generationParams.modelId}
                            onChange={(val) => updateParams({modelId: val})}
                        >
                            <Option value="">Select a model...</Option>
                            {robotModels.map(model => (
                                <Option key={model.id} value={model.id}>
                                    {model.name}
                                </Option>
                            ))}
                        </Select>
                    </FormGroup>
                    
                    <FormGroup>
                        <Label>Quantity to Build</Label>
                        <NumberInput 
                            value={generationParams.quantity}
                            onChange={(val) => updateParams({quantity: val})}
                            min={1}
                            max={1000}
                        />
                    </FormGroup>
                    
                    <FormGroup>
                        <Label>Priority</Label>
                        <RadioGroup 
                            value={generationParams.priority}
                            onChange={(val) => updateParams({priority: val})}
                        >
                            <Radio value="standard">Standard</Radio>
                            <Radio value="rush">Rush (add 25% to cost)</Radio>
                            <Radio value="economy">Economy (longer lead time)</Radio>
                        </RadioGroup>
                    </FormGroup>
                    
                    <FormGroup>
                        <Label>Include Spares</Label>
                        <Checkbox 
                            checked={generationParams.includeSpares}
                            onChange={(val) => updateParams({includeSpares: val})}
                        >
                            Add 10% spare parts
                        </Checkbox>
                    </FormGroup>
                    
                    {generationParams.modelId && generationParams.quantity && (
                        <CostPreview>
                            <EstimatedCost 
                                modelId={generationParams.modelId}
                                quantity={generationParams.quantity}
                                includeSpares={generationParams.includeSpares}
                            />
                        </CostPreview>
                    )}
                </DialogBody>
                <DialogFooter>
                    <Button 
                        variant="secondary"
                        onClick={() => setShowGenerateDialog(false)}
                    >
                        Cancel
                    </Button>
                    <Button 
                        variant="primary"
                        onClick={() => generateOrderSheet(generationParams)}
                        disabled={!generationParams.modelId || !generationParams.quantity || isGenerating}
                    >
                        {isGenerating ? "Generating..." : "Generate Order"}
                    </Button>
                </DialogFooter>
            </Dialog>
        )
    
    METHOD renderOrderList():
        // TEST: Shows all orders
        // TEST: Filters by status
        // TEST: Sorts by date
        
        RETURN (
            <OrderList>
                {orders.length === 0 ? (
                    <EmptyState>
                        <EmptyIcon />
                        <EmptyMessage>No orders generated yet</EmptyMessage>
                        <Button onClick={() => setShowGenerateDialog(true)}>
                            Generate First Order
                        </Button>
                    </EmptyState>
                ) : (
                    orders.map(order => (
                        <OrderCard 
                            key={order.id}
                            onClick={() => setSelectedOrder(order)}
                            selected={selectedOrder?.id === order.id}
                        >
                            <OrderHeader>
                                <OrderNumber>Order #{order.id}</OrderNumber>
                                <StatusBadge status={order.status} />
                            </OrderHeader>
                            <OrderInfo>
                                <InfoRow>
                                    <Label>Date:</Label>
                                    <Value>{formatDate(order.date)}</Value>
                                </InfoRow>
                                <InfoRow>
                                    <Label>Items:</Label>
                                    <Value>{order.items.length}</Value>
                                </InfoRow>
                                <InfoRow>
                                    <Label>Total:</Label>
                                    <Value>${order.totals.total.toFixed(2)}</Value>
                                </InfoRow>
                            </OrderInfo>
                            <OrderActions>
                                <IconButton 
                                    icon="download"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        exportOrder(order, "pdf")
                                    }}
                                />
                                <IconButton 
                                    icon="duplicate"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        duplicateOrder(order)
                                    }}
                                />
                                <IconButton 
                                    icon="delete"
                                    onClick={(e) => {
                                        e.stopPropagation()
                                        confirmDeleteOrder(order.id)
                                    }}
                                />
                            </OrderActions>
                        </OrderCard>
                    ))
                )}
            </OrderList>
        )
    
    RENDER():
        RETURN (
            <div className="orders-tab">
                <OrdersToolbar>
                    <Button 
                        variant="primary"
                        onClick={() => setShowGenerateDialog(true)}
                    >
                        <PlusIcon /> Generate Order
                    </Button>
                    <ExportMenu>
                        <Button variant="secondary">
                            Export All <ChevronDownIcon />
                        </Button>
                        <MenuItems>
                            <MenuItem onClick={() => exportAllOrders("csv")}>
                                As CSV
                            </MenuItem>
                            <MenuItem onClick={() => exportAllOrders("excel")}>
                                As Excel
                            </MenuItem>
                        </MenuItems>
                    </ExportMenu>
                </OrdersToolbar>
                
                <SplitPanel>
                    <LeftPanel>{renderOrderList()}</LeftPanel>
                    <RightPanel>
                        {selectedOrder ? (
                            <OrderDetails 
                                order={selectedOrder}
                                onExport={exportOrder}
                                onStatusChange={updateOrderStatus}
                            />
                        ) : (
                            <EmptyDetailsState>
                                Select an order to view details
                            </EmptyDetailsState>
                        )}
                    </RightPanel>
                </SplitPanel>
                
                {renderOrderGenerationDialog()}
            </div>
        )
```

## Module: Touch-Optimized Components (TouchComponents.tsx)

```pseudocode
COMPONENT TouchOptimizedInput:
    PROPS:
        value: number
        onChange: Function
        min: number = 0
        max: number = 9999
    
    STATE:
        isEditing: boolean = false
        tempValue: string = value.toString()
        
    METHOD handleTouchStart(event):
        // TEST: Prevents zoom on double tap
        // TEST: Shows number pad on mobile
        // TEST: Enlarges input area
        
        event.preventDefault()
        SET isEditing = true
        
        IF isTouchDevice():
            INPUT_ELEMENT.inputMode = "numeric"
            INPUT_ELEMENT.pattern = "[0-9]*"
    
    METHOD handleIncrement(step: number = 1):
        // TEST: Increments by step value
        // TEST: Respects max value
        // TEST: Provides haptic feedback
        
        newValue = Math.min(value + step, max)
        onChange(newValue)
        
        IF supportsHaptics():
            TRIGGER_HAPTIC_FEEDBACK("light")
    
    METHOD handleDecrement(step: number = 1):
        // TEST: Decrements by step value
        // TEST: Respects min value
        // TEST: Provides haptic feedback
        
        newValue = Math.max(value - step, min)
        onChange(newValue)
        
        IF supportsHaptics():
            TRIGGER_HAPTIC_FEEDBACK("light")
    
    RENDER():
        RETURN (
            <div className="touch-input-container">
                <Button 
                    className="touch-button decrement"
                    onTouchStart={() => handleDecrement(10)}
                    onMouseDown={() => handleDecrement(10)}
                >
                    -10
                </Button>
                <Button 
                    className="touch-button decrement"
                    onTouchStart={() => handleDecrement(1)}
                    onMouseDown={() => handleDecrement(1)}
                >
                    -1
                </Button>
                
                <input 
                    type="number"
                    value={isEditing ? tempValue : value}
                    onChange={(e) => setTempValue(e.target.value)}
                    onBlur={() => {
                        onChange(parseInt(tempValue) || 0)
                        setIsEditing(false)
                    }}
                    onFocus={() => setIsEditing(true)}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    className="touch-number-input"
                />
                
                <Button 
                    className="touch-button increment"
                    onTouchStart={() => handleIncrement(1)}
                    onMouseDown={() => handleIncrement(1)}
                >
                    +1
                </Button>
                <Button 
                    className="touch-button increment"
                    onTouchStart={() => handleIncrement(10)}
                    onMouseDown={() => handleIncrement(10)}
                >
                    +10
                </Button>
            </div>
        )

COMPONENT SwipeableList:
    PROPS:
        items: Array<any>
        onSwipeLeft: Function
        onSwipeRight: Function
        renderItem: Function
    
    STATE:
        swipingItem: string | null = null
        swipeDistance: number = 0
        
    METHOD handleTouchStart(itemId: string, event):
        // TEST: Captures initial touch position
        // TEST: Stores swiping item
        
        SET swipingItem = itemId
        SET touchStartX = event.touches[0].clientX
    
    METHOD handleTouchMove(event):
        // TEST: Tracks swipe distance
        // TEST: Applies transform to item
        // TEST: Limits swipe distance
        
        IF NOT swipingItem:
            RETURN
        
        currentX = event.touches[0].clientX
        distance = currentX - touchStartX
        
        // Limit swipe distance
        SET swipeDistance = Math.max(-100, Math.min(100, distance))
        
        // Apply visual transform
        APPLY_TRANSFORM(`translateX(${swipeDistance}px)`)
    
    METHOD handleTouchEnd():
        // TEST: Triggers action on sufficient swipe
        // TEST: Animates back to position
        // TEST: Resets state
        
        IF Math.abs(swipeDistance) > 50:
            IF swipeDistance > 0:
                onSwipeRight(swipingItem)
            ELSE:
                onSwipeLeft(swipingItem)
        
        // Animate back
        ANIMATE_TRANSFORM("translateX(0)", 200ms)
        
        SET swipingItem = null
        SET swipeDistance = 0
    
    RENDER():
        RETURN (
            <div className="swipeable-list">
                {items.map(item => (
                    <div 
                        key={item.id}
                        className="swipeable-item"
                        onTouchStart={(e) => handleTouchStart(item.id, e)}
                        onTouchMove={handleTouchMove}
                        onTouchEnd={handleTouchEnd}
                        style={{
                            transform: swipingItem === item.id ? 
                                `translateX(${swipeDistance}px)` : 'none'
                        }}
                    >
                        {renderItem(item)}
                    </div>
                ))}
            </div>
        )
```

## Module: API Client (apiClient.ts)

```pseudocode
CLASS APIClient:
    CONSTRUCTOR(baseURL: string = "/api"):
        this.baseURL = baseURL
        this.authToken = null
        this.requestQueue = []
        this.isOnline = navigator.onLine
        
        // Setup offline handling
        window.addEventListener("online", this.handleOnline)
        window.addEventListener("offline", this.handleOffline)
    
    METHOD request(endpoint: string, options: RequestOptions):
        // TEST: Makes successful API calls
        // TEST: Handles network errors
        // TEST: Queues requests when offline
        // TEST: Retries failed requests
        
        IF NOT this.isOnline:
            RETURN this.queueRequest(endpoint, options)
        
        TRY:
            response = AWAIT fetch(this.baseURL + endpoint, {
                ...options,
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": this.authToken ? `Bearer ${this.authToken}` : "",
                    ...options.headers
                }
            })
            
            IF NOT response.ok:
                THROW new APIError(response.status, response.statusText)
            
            data = AWAIT response.json()
            RETURN data
            
        CATCH error:
            IF error.status === 401:
                // Token expired, refresh
                AWAIT this.refreshToken()
                RETURN this.request(endpoint, options) // Retry
            ELIF error.status >= 500:
                // Server error, retry with backoff
                RETURN this.retryWithBackoff(endpoint, options)
            ELSE:
                THROW error
    
    METHOD queueRequest(endpoint: string, options: RequestOptions):
        // TEST: Queues requests when offline
        // TEST: Persists queue to localStorage
        // TEST: Processes queue when back online
        
        request = {
            id: generateUUID(),
            endpoint: endpoint,
            options: options,
            timestamp: NOW(),
            retries: 0
        }
        
        this.requestQueue.push(request)
        this.persistQueue()
        
        RETURN Promise.resolve({
            queued: true,
            requestId: request.id,
            message: "Request queued for when connection is restored"
        })
    
    METHOD processQueue():
        // TEST: Processes all queued requests
        // TEST: Handles failures in queue
        // TEST: Maintains order of requests
        
        WHILE this.requestQueue.length > 0:
            request = this.requestQueue.shift()
            
            TRY:
                result = AWAIT this.request(request.endpoint, request.options)
                this.notifyQueueSuccess(request.id, result)
            CATCH error:
                IF request.retries < 3:
                    request.retries++
                    this.requestQueue.push(request) // Re-queue
                ELSE:
                    this.notifyQueueFailure(request.id, error)
            
            this.persistQueue()
    
    // Inventory API Methods
    METHOD getInventory():
        RETURN this.request("/inventory", { method: "GET" })
    
    METHOD updateInventory(partId: string, quantity: number):
        RETURN this.request("/inventory/update", {
            method: "POST",
            body: JSON.stringify({ part_id: partId, quantity: quantity })
        })
    
    METHOD bulkUpdateInventory(updates: Array<InventoryUpdate>):
        RETURN this.request("/inventory/bulk-update", {
            method: "POST",
            body: JSON.stringify({ updates: updates })
        })
    
    // Assembly API Methods
    METHOD calculateBuildable(robotModelId: string):
        RETURN this.request(`/calculate/${robotModelId}`, { method: "GET" })
    
    METHOD createAssembly(robotModelId: string, notes: string):
        RETURN this.request("/assembly/create", {
            method: "POST",
            body: JSON.stringify({ 
                robot_model_id: robotModelId,
                notes: notes 
            })
        })
    
    // Order API Methods
    METHOD generateOrderSheet(params: OrderGenerationParams):
        RETURN this.request("/order/generate", {
            method: "POST",
            body: JSON.stringify(params)
        })
    
    METHOD exportInventory(format: string = "csv"):
        RETURN this.request(`/export/inventory?format=${format}`, { 
            method: "GET" 
        })
    
    // BOM API Methods
    METHOD getBOM(robotModelId: string):
        RETURN this.request(`/bom/${robotModelId}`, { method: "GET" })
    
    METHOD importBOM(robotModelId: string, bomData: object):
        RETURN this.request("/bom/import", {
            method: "POST",
            body: JSON.stringify({
                robot_model_id: robotModelId,
                bom_data: bomData
            })
        })