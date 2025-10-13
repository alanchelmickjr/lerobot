#!/usr/bin/env node
/**
 * End-to-End Tests for BOM Calculator UI
 * Uses Playwright for browser automation and testing
 */

const { chromium, firefox, webkit } = require('playwright');
const { expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// Test configuration
const BASE_URL = process.env.TEST_FRONTEND_URL || 'http://localhost:3000';
const API_URL = process.env.TEST_API_URL || 'http://localhost:8000';
const HEADLESS = process.env.HEADLESS !== 'false';
const BROWSER = process.env.BROWSER || 'chromium';
const TIMEOUT = 30000;

// Test data
const testData = {
    part: {
        name: 'E2E Test Motor',
        partNumber: 'E2E-MOT-001',
        supplier: 'E2E Supplier',
        unitPrice: '29.99',
        leadTime: '5',
        minOrder: '1',
        category: 'Motors'
    },
    robot: {
        name: 'E2E Test Robot',
        modelNumber: 'E2E-BOT-001',
        description: 'Robot for E2E testing'
    },
    inventory: {
        quantity: '100',
        location: 'E2E-A1'
    },
    assembly: {
        quantity: '5'
    },
    order: {
        quantity: '50',
        notes: 'E2E test order'
    }
};

class BOMCalculatorE2ETests {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.testResults = [];
    }

    async setup() {
        console.log('🚀 Setting up E2E tests...');
        
        // Launch browser
        const browserType = BROWSER === 'firefox' ? firefox : 
                           BROWSER === 'webkit' ? webkit : chromium;
        
        this.browser = await browserType.launch({
            headless: HEADLESS,
            slowMo: HEADLESS ? 0 : 100
        });
        
        this.context = await this.browser.newContext({
            viewport: { width: 1280, height: 720 },
            ignoreHTTPSErrors: true
        });
        
        this.page = await this.context.newPage();
        this.page.setDefaultTimeout(TIMEOUT);
        
        // Setup request interceptor for debugging
        this.page.on('request', request => {
            if (request.url().includes('/api/')) {
                console.log('  📡 API Request:', request.method(), request.url());
            }
        });
        
        this.page.on('response', response => {
            if (response.url().includes('/api/') && response.status() >= 400) {
                console.log('  ❌ API Error:', response.status(), response.url());
            }
        });
        
        console.log('✅ Setup complete\n');
    }

    async teardown() {
        console.log('\n🧹 Cleaning up...');
        if (this.browser) {
            await this.browser.close();
        }
        console.log('✅ Cleanup complete');
    }

    async runTest(name, testFn) {
        console.log(`\n📝 Running: ${name}`);
        try {
            await testFn.call(this);
            console.log(`  ✅ PASSED`);
            this.testResults.push({ name, status: 'PASSED' });
        } catch (error) {
            console.log(`  ❌ FAILED: ${error.message}`);
            this.testResults.push({ name, status: 'FAILED', error: error.message });
            
            // Take screenshot on failure
            const screenshotPath = path.join(__dirname, `screenshots/failure-${Date.now()}.png`);
            await this.page.screenshot({ path: screenshotPath, fullPage: true });
            console.log(`  📸 Screenshot saved: ${screenshotPath}`);
        }
    }

    // ==================== Navigation Tests ====================

    async testHomePage() {
        await this.page.goto(BASE_URL);
        await this.page.waitForLoadState('networkidle');
        
        // Check if dashboard loads
        const title = await this.page.textContent('h1');
        expect(title).toContain('Dashboard');
        
        // Check for main navigation elements
        await expect(this.page.locator('nav')).toBeVisible();
        await expect(this.page.locator('text=Dashboard')).toBeVisible();
        await expect(this.page.locator('text=Inventory')).toBeVisible();
        await expect(this.page.locator('text=Assembly')).toBeVisible();
        await expect(this.page.locator('text=Orders')).toBeVisible();
    }

    async testNavigation() {
        // Navigate to Inventory
        await this.page.click('text=Inventory');
        await this.page.waitForURL('**/inventory');
        await expect(this.page.locator('h1')).toContainText('Inventory');
        
        // Navigate to Assembly
        await this.page.click('text=Assembly');
        await this.page.waitForURL('**/assembly');
        await expect(this.page.locator('h1')).toContainText('Assembly');
        
        // Navigate to Orders
        await this.page.click('text=Orders');
        await this.page.waitForURL('**/orders');
        await expect(this.page.locator('h1')).toContainText('Orders');
        
        // Navigate back to Dashboard
        await this.page.click('text=Dashboard');
        await this.page.waitForURL('**/');
        await expect(this.page.locator('h1')).toContainText('Dashboard');
    }

    // ==================== Parts Management Tests ====================

    async testAddPart() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Click Add Part button
        await this.page.click('button:has-text("Add Part")');
        
        // Fill in part form
        await this.page.fill('input[name="name"]', testData.part.name);
        await this.page.fill('input[name="partNumber"]', testData.part.partNumber);
        await this.page.fill('input[name="supplier"]', testData.part.supplier);
        await this.page.fill('input[name="unitPrice"]', testData.part.unitPrice);
        await this.page.fill('input[name="leadTime"]', testData.part.leadTime);
        await this.page.fill('input[name="minOrder"]', testData.part.minOrder);
        await this.page.selectOption('select[name="category"]', testData.part.category);
        
        // Submit form
        await this.page.click('button:has-text("Save")');
        
        // Verify part was added
        await this.page.waitForSelector(`text=${testData.part.name}`);
        await expect(this.page.locator(`text=${testData.part.name}`)).toBeVisible();
    }

    async testSearchParts() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Search for the test part
        await this.page.fill('input[placeholder*="Search"]', testData.part.name);
        await this.page.press('input[placeholder*="Search"]', 'Enter');
        
        // Verify search results
        await this.page.waitForSelector(`text=${testData.part.name}`);
        const results = await this.page.locator('.part-card').count();
        expect(results).toBeGreaterThan(0);
    }

    async testEditPart() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Find and click edit on test part
        const partCard = this.page.locator(`.part-card:has-text("${testData.part.name}")`);
        await partCard.locator('button:has-text("Edit")').click();
        
        // Update part price
        await this.page.fill('input[name="unitPrice"]', '39.99');
        await this.page.click('button:has-text("Save")');
        
        // Verify update
        await this.page.waitForSelector('text=39.99');
        await expect(this.page.locator('text=39.99')).toBeVisible();
    }

    // ==================== Inventory Management Tests ====================

    async testUpdateInventory() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Find test part
        const partCard = this.page.locator(`.part-card:has-text("${testData.part.name}")`);
        
        // Update quantity
        await partCard.locator('button:has-text("Update Stock")').click();
        await this.page.fill('input[name="quantity"]', testData.inventory.quantity);
        await this.page.fill('input[name="location"]', testData.inventory.location);
        await this.page.click('button:has-text("Update")');
        
        // Verify update
        await this.page.waitForSelector(`text=${testData.inventory.quantity}`);
        await expect(partCard.locator(`text=${testData.inventory.quantity}`)).toBeVisible();
    }

    async testBulkInventoryUpdate() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Select multiple parts
        await this.page.check('input[type="checkbox"]', { force: true });
        
        // Click bulk update
        await this.page.click('button:has-text("Bulk Update")');
        
        // Fill bulk update form
        await this.page.fill('input[name="quantity"]', '200');
        await this.page.click('button:has-text("Apply")');
        
        // Verify updates
        await this.page.waitForTimeout(1000);
        const updatedCards = await this.page.locator('text=200').count();
        expect(updatedCards).toBeGreaterThan(0);
    }

    async testLowStockAlert() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Filter for low stock items
        await this.page.click('button:has-text("Filters")');
        await this.page.check('input[name="lowStock"]');
        await this.page.click('button:has-text("Apply Filters")');
        
        // Check for low stock indicators
        const lowStockIndicators = await this.page.locator('.low-stock-indicator').count();
        console.log(`  Found ${lowStockIndicators} low stock items`);
    }

    // ==================== Assembly Tests ====================

    async testAssemblyCalculation() {
        await this.page.goto(`${BASE_URL}/assembly`);
        
        // Select robot model
        await this.page.selectOption('select[name="robotModel"]', { index: 1 });
        
        // Enter quantity
        await this.page.fill('input[name="quantity"]', testData.assembly.quantity);
        
        // Calculate
        await this.page.click('button:has-text("Calculate")');
        
        // Verify results
        await this.page.waitForSelector('.assembly-results');
        await expect(this.page.locator('text=Total Cost')).toBeVisible();
        await expect(this.page.locator('text=Required Parts')).toBeVisible();
        await expect(this.page.locator('text=Assembly Time')).toBeVisible();
    }

    async testAssemblyOptimization() {
        await this.page.goto(`${BASE_URL}/assembly`);
        
        // Click optimize button
        await this.page.click('button:has-text("Optimize")');
        
        // Add multiple robots
        await this.page.click('button:has-text("Add Robot")');
        await this.page.selectOption('select[name="robotModel1"]', { index: 1 });
        await this.page.fill('input[name="quantity1"]', '3');
        
        // Run optimization
        await this.page.click('button:has-text("Run Optimization")');
        
        // Verify optimization results
        await this.page.waitForSelector('.optimization-results');
        await expect(this.page.locator('text=Optimal Batch Size')).toBeVisible();
        await expect(this.page.locator('text=Production Schedule')).toBeVisible();
    }

    async testBottleneckAnalysis() {
        await this.page.goto(`${BASE_URL}/assembly`);
        
        // Navigate to bottleneck analysis
        await this.page.click('text=Bottleneck Analysis');
        
        // Verify bottleneck chart
        await this.page.waitForSelector('.bottleneck-chart');
        await expect(this.page.locator('.bottleneck-chart')).toBeVisible();
    }

    // ==================== Order Management Tests ====================

    async testCreateOrder() {
        await this.page.goto(`${BASE_URL}/orders`);
        
        // Click create order
        await this.page.click('button:has-text("Create Order")');
        
        // Select supplier
        await this.page.selectOption('select[name="supplier"]', { index: 1 });
        
        // Add items
        await this.page.click('button:has-text("Add Item")');
        await this.page.selectOption('select[name="part"]', { index: 1 });
        await this.page.fill('input[name="quantity"]', testData.order.quantity);
        
        // Add notes
        await this.page.fill('textarea[name="notes"]', testData.order.notes);
        
        // Submit order
        await this.page.click('button:has-text("Submit Order")');
        
        // Verify order created
        await this.page.waitForSelector('.order-success');
        await expect(this.page.locator('text=Order created successfully')).toBeVisible();
    }

    async testGeneratePurchaseOrder() {
        await this.page.goto(`${BASE_URL}/orders`);
        
        // Click generate PO
        await this.page.click('button:has-text("Generate PO")');
        
        // Select robot and quantity
        await this.page.selectOption('select[name="robot"]', { index: 1 });
        await this.page.fill('input[name="quantity"]', '10');
        
        // Generate
        await this.page.click('button:has-text("Generate")');
        
        // Verify PO preview
        await this.page.waitForSelector('.po-preview');
        await expect(this.page.locator('text=Purchase Order Preview')).toBeVisible();
        await expect(this.page.locator('text=Total Cost')).toBeVisible();
    }

    async testOrderHistory() {
        await this.page.goto(`${BASE_URL}/orders`);
        
        // Click history tab
        await this.page.click('text=Order History');
        
        // Verify history table
        await this.page.waitForSelector('.order-history-table');
        await expect(this.page.locator('.order-history-table')).toBeVisible();
        
        // Test filtering
        await this.page.selectOption('select[name="status"]', 'pending');
        await this.page.waitForTimeout(500);
        
        const rows = await this.page.locator('.order-row').count();
        console.log(`  Found ${rows} pending orders`);
    }

    // ==================== Responsive Design Tests ====================

    async testMobileResponsiveness() {
        // Set mobile viewport
        await this.page.setViewportSize({ width: 375, height: 667 });
        await this.page.goto(BASE_URL);
        
        // Check mobile menu
        await this.page.click('.mobile-menu-button');
        await expect(this.page.locator('.mobile-navigation')).toBeVisible();
        
        // Navigate on mobile
        await this.page.click('text=Inventory');
        await this.page.waitForURL('**/inventory');
        
        // Check mobile layout
        const cards = await this.page.locator('.part-card').count();
        for (let i = 0; i < Math.min(cards, 3); i++) {
            const card = this.page.locator('.part-card').nth(i);
            const box = await card.boundingBox();
            expect(box.width).toBeLessThan(360);
        }
        
        // Reset viewport
        await this.page.setViewportSize({ width: 1280, height: 720 });
    }

    async testTabletResponsiveness() {
        // Set tablet viewport
        await this.page.setViewportSize({ width: 768, height: 1024 });
        await this.page.goto(BASE_URL);
        
        // Check tablet layout
        await expect(this.page.locator('nav')).toBeVisible();
        
        // Navigate to inventory
        await this.page.click('text=Inventory');
        
        // Check grid layout
        const cards = await this.page.locator('.part-card').count();
        console.log(`  Tablet view shows ${cards} part cards`);
        
        // Reset viewport
        await this.page.setViewportSize({ width: 1280, height: 720 });
    }

    // ==================== Real-time Updates Tests ====================

    async testWebSocketConnection() {
        await this.page.goto(BASE_URL);
        
        // Check WebSocket connection
        const wsConnected = await this.page.evaluate(() => {
            return new Promise((resolve) => {
                const ws = new WebSocket('ws://localhost:8000/ws');
                ws.onopen = () => resolve(true);
                ws.onerror = () => resolve(false);
                setTimeout(() => resolve(false), 5000);
            });
        });
        
        expect(wsConnected).toBe(true);
        console.log('  WebSocket connection established');
    }

    async testRealTimeInventoryUpdate() {
        // Open two browser contexts
        const context2 = await this.browser.newContext();
        const page2 = await context2.newPage();
        
        // Navigate both to inventory
        await this.page.goto(`${BASE_URL}/inventory`);
        await page2.goto(`${BASE_URL}/inventory`);
        
        // Update inventory in first page
        const partCard = this.page.locator(`.part-card`).first();
        await partCard.locator('button:has-text("Update Stock")').click();
        await this.page.fill('input[name="quantity"]', '999');
        await this.page.click('button:has-text("Update")');
        
        // Check if update appears in second page
        await page2.waitForTimeout(2000);
        await expect(page2.locator('text=999')).toBeVisible();
        
        await context2.close();
    }

    // ==================== Performance Tests ====================

    async testPageLoadPerformance() {
        const metrics = [];
        
        for (const route of ['/', '/inventory', '/assembly', '/orders']) {
            const startTime = Date.now();
            await this.page.goto(`${BASE_URL}${route}`);
            await this.page.waitForLoadState('networkidle');
            const loadTime = Date.now() - startTime;
            
            metrics.push({ route, loadTime });
            console.log(`  ${route}: ${loadTime}ms`);
            
            // Page should load within 3 seconds
            expect(loadTime).toBeLessThan(3000);
        }
    }

    async testSearchPerformance() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Measure search response time
        const startTime = Date.now();
        await this.page.fill('input[placeholder*="Search"]', 'motor');
        await this.page.press('input[placeholder*="Search"]', 'Enter');
        await this.page.waitForSelector('.search-results');
        const searchTime = Date.now() - startTime;
        
        console.log(`  Search completed in ${searchTime}ms`);
        expect(searchTime).toBeLessThan(1000);
    }

    // ==================== Error Handling Tests ====================

    async testNetworkErrorHandling() {
        // Simulate network failure
        await this.page.route('**/api/**', route => route.abort());
        
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Should show error message
        await this.page.waitForSelector('.error-message');
        await expect(this.page.locator('text=Unable to load')).toBeVisible();
        
        // Clear route handler
        await this.page.unroute('**/api/**');
    }

    async testFormValidation() {
        await this.page.goto(`${BASE_URL}/inventory`);
        
        // Try to submit invalid form
        await this.page.click('button:has-text("Add Part")');
        await this.page.click('button:has-text("Save")');
        
        // Should show validation errors
        await expect(this.page.locator('.field-error')).toBeVisible();
        await expect(this.page.locator('text=required')).toBeVisible();
    }

    // ==================== Run All Tests ====================

    async runAllTests() {
        console.log('🏁 Starting BOM Calculator E2E Tests');
        console.log(`📍 Testing URL: ${BASE_URL}`);
        console.log(`🌐 Browser: ${BROWSER}`);
        console.log(`👁️  Headless: ${HEADLESS}\n`);
        
        await this.setup();
        
        // Navigation Tests
        await this.runTest('Home Page Loading', this.testHomePage);
        await this.runTest('Navigation Between Pages', this.testNavigation);
        
        // Parts Management Tests
        await this.runTest('Add New Part', this.testAddPart);
        await this.runTest('Search Parts', this.testSearchParts);
        await this.runTest('Edit Part', this.testEditPart);
        
        // Inventory Management Tests
        await this.runTest('Update Inventory', this.testUpdateInventory);
        await this.runTest('Bulk Inventory Update', this.testBulkInventoryUpdate);
        await this.runTest('Low Stock Alert', this.testLowStockAlert);
        
        // Assembly Tests
        await this.runTest('Assembly Calculation', this.testAssemblyCalculation);
        await this.runTest('Assembly Optimization', this.testAssemblyOptimization);
        await this.runTest('Bottleneck Analysis', this.testBottleneckAnalysis);
        
        // Order Management Tests
        await this.runTest('Create Order', this.testCreateOrder);
        await this.runTest('Generate Purchase Order', this.testGeneratePurchaseOrder);
        await this.runTest('Order History', this.testOrderHistory);
        
        // Responsive Design Tests
        await this.runTest('Mobile Responsiveness', this.testMobileResponsiveness);
        await this.runTest('Tablet Responsiveness', this.testTabletResponsiveness);
        
        // Real-time Updates Tests
        await this.runTest('WebSocket Connection', this.testWebSocketConnection);
        await this.runTest('Real-time Inventory Update', this.testRealTimeInventoryUpdate);
        
        // Performance Tests
        await this.runTest('Page Load Performance', this.testPageLoadPerformance);
        await this.runTest('Search Performance', this.testSearchPerformance);
        
        // Error Handling Tests
        await this.runTest('Network Error Handling', this.testNetworkErrorHandling);
        await this.runTest('Form Validation', this.testFormValidation);
        
        await this.teardown();
        
        // Print summary
        console.log('\n' + '='.repeat(50));
        console.log('📊 Test Results Summary');
        console.log('='.repeat(50));
        
        const passed = this.testResults.filter(r => r.status === 'PASSED').length;
        const failed = this.testResults.filter(r => r.status === 'FAILED').length;
        
        console.log(`✅ Passed: ${passed}`);
        console.log(`❌ Failed: ${failed}`);
        console.log(`📝 Total: ${this.testResults.length}`);
        
        if (failed > 0) {
            console.log('\n❌ Failed Tests:');
            this.testResults
                .filter(r => r.status === 'FAILED')
                .forEach(r => console.log(`  - ${r.name}: ${r.error}`));
        }
        
        console.log('\n' + '='.repeat(50));
        
        return failed === 0;
    }
}

// Main execution
async function main() {
    const tester = new BOMCalculatorE2ETests();
    
    try {
        // Create screenshots directory
        const screenshotsDir = path.join(__dirname, 'screenshots');
        if (!fs.existsSync(screenshotsDir)) {
            fs.mkdirSync(screenshotsDir);
        }
        
        const success = await tester.runAllTests();
        process.exit(success ? 0 : 1);
    } catch (error) {
        console.error('❌ Fatal error:', error);
        process.exit(1);
    }
}

// Run tests if executed directly
if (require.main === module) {
    main();
}

module.exports = BOMCalculatorE2ETests;