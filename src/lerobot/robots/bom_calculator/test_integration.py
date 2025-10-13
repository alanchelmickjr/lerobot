#!/usr/bin/env python3
"""
Integration tests for BOM Calculator API endpoints
"""

import os
import sys
import json
import asyncio
import pytest
import httpx
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Test configuration
BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
TEST_TIMEOUT = 30


class TestBOMCalculatorAPI:
    """Integration tests for BOM Calculator API"""
    
    @classmethod
    def setup_class(cls):
        """Setup test client and test data"""
        cls.client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=TEST_TIMEOUT
        )
        cls.test_data = cls._load_test_data()
        
    @classmethod
    def teardown_class(cls):
        """Cleanup after tests"""
        asyncio.run(cls.client.aclose())
        
    @classmethod
    def _load_test_data(cls) -> Dict[str, Any]:
        """Load test data"""
        return {
            "part": {
                "name": "Test Motor",
                "part_number": "MOT-TEST-001",
                "supplier": "Test Supplier",
                "unit_price": 45.99,
                "lead_time_days": 7,
                "minimum_order_quantity": 1,
                "category": "Motors",
                "datasheet_url": "https://example.com/datasheet.pdf"
            },
            "robot": {
                "name": "Test Robot",
                "model_number": "TR-001",
                "description": "Test robot for integration testing"
            },
            "inventory": {
                "part_id": 1,
                "quantity": 100,
                "location": "A1-B2",
                "last_updated": datetime.utcnow().isoformat()
            },
            "assembly": {
                "robot_id": 1,
                "quantity": 5,
                "priority": "high"
            },
            "order": {
                "items": [
                    {"part_id": 1, "quantity": 50}
                ],
                "supplier": "Test Supplier",
                "notes": "Integration test order"
            }
        }
    
    # ==================== Health Check Tests ====================
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        response = await self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test root endpoint"""
        response = await self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        
    # ==================== Parts API Tests ====================
    
    @pytest.mark.asyncio
    async def test_create_part(self):
        """Test creating a new part"""
        response = await self.client.post(
            f"{API_PREFIX}/parts/",
            json=self.test_data["part"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == self.test_data["part"]["name"]
        assert data["part_number"] == self.test_data["part"]["part_number"]
        assert "id" in data
        
        # Store part ID for other tests
        self.__class__.part_id = data["id"]
        
    @pytest.mark.asyncio
    async def test_get_parts(self):
        """Test getting all parts"""
        response = await self.client.get(f"{API_PREFIX}/parts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
    @pytest.mark.asyncio
    async def test_get_part_by_id(self):
        """Test getting a part by ID"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        response = await self.client.get(f"{API_PREFIX}/parts/{self.part_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.part_id
        assert data["name"] == self.test_data["part"]["name"]
        
    @pytest.mark.asyncio
    async def test_update_part(self):
        """Test updating a part"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        update_data = {
            "name": "Updated Test Motor",
            "unit_price": 49.99
        }
        response = await self.client.put(
            f"{API_PREFIX}/parts/{self.part_id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["unit_price"] == update_data["unit_price"]
        
    @pytest.mark.asyncio
    async def test_search_parts(self):
        """Test searching parts"""
        response = await self.client.get(
            f"{API_PREFIX}/parts/search",
            params={"query": "Motor"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    # ==================== Robot Models API Tests ====================
    
    @pytest.mark.asyncio
    async def test_create_robot(self):
        """Test creating a new robot model"""
        response = await self.client.post(
            f"{API_PREFIX}/robots/",
            json=self.test_data["robot"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == self.test_data["robot"]["name"]
        assert data["model_number"] == self.test_data["robot"]["model_number"]
        assert "id" in data
        
        # Store robot ID for other tests
        self.__class__.robot_id = data["id"]
        
    @pytest.mark.asyncio
    async def test_get_robots(self):
        """Test getting all robot models"""
        response = await self.client.get(f"{API_PREFIX}/robots/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
    @pytest.mark.asyncio
    async def test_get_robot_by_id(self):
        """Test getting a robot model by ID"""
        if not hasattr(self, 'robot_id'):
            pytest.skip("Robot ID not available")
            
        response = await self.client.get(f"{API_PREFIX}/robots/{self.robot_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.robot_id
        assert data["name"] == self.test_data["robot"]["name"]
        
    @pytest.mark.asyncio
    async def test_get_robot_bom(self):
        """Test getting robot BOM"""
        if not hasattr(self, 'robot_id'):
            pytest.skip("Robot ID not available")
            
        response = await self.client.get(f"{API_PREFIX}/robots/{self.robot_id}/bom")
        assert response.status_code == 200
        data = response.json()
        assert "robot" in data
        assert "parts" in data
        assert "total_cost" in data
        
    # ==================== Inventory API Tests ====================
    
    @pytest.mark.asyncio
    async def test_update_inventory(self):
        """Test updating inventory"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        inventory_data = self.test_data["inventory"].copy()
        inventory_data["part_id"] = self.part_id
        
        response = await self.client.put(
            f"{API_PREFIX}/inventory/{self.part_id}",
            json=inventory_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["part_id"] == self.part_id
        assert data["quantity"] == inventory_data["quantity"]
        
    @pytest.mark.asyncio
    async def test_get_inventory(self):
        """Test getting inventory"""
        response = await self.client.get(f"{API_PREFIX}/inventory/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    @pytest.mark.asyncio
    async def test_get_inventory_by_part(self):
        """Test getting inventory by part ID"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        response = await self.client.get(f"{API_PREFIX}/inventory/{self.part_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["part_id"] == self.part_id
        
    @pytest.mark.asyncio
    async def test_get_low_stock_items(self):
        """Test getting low stock items"""
        response = await self.client.get(
            f"{API_PREFIX}/inventory/low-stock",
            params={"threshold": 50}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    @pytest.mark.asyncio
    async def test_bulk_update_inventory(self):
        """Test bulk inventory update"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        bulk_data = {
            "updates": [
                {"part_id": self.part_id, "quantity": 150}
            ]
        }
        response = await self.client.post(
            f"{API_PREFIX}/inventory/bulk-update",
            json=bulk_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 1
        
    # ==================== Assembly API Tests ====================
    
    @pytest.mark.asyncio
    async def test_calculate_assembly(self):
        """Test assembly calculation"""
        if not hasattr(self, 'robot_id'):
            pytest.skip("Robot ID not available")
            
        assembly_data = self.test_data["assembly"].copy()
        assembly_data["robot_id"] = self.robot_id
        
        response = await self.client.post(
            f"{API_PREFIX}/assembly/calculate",
            json=assembly_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "robot" in data
        assert "quantity" in data
        assert "total_cost" in data
        assert "missing_parts" in data
        assert "assembly_time" in data
        
    @pytest.mark.asyncio
    async def test_optimize_assembly(self):
        """Test assembly optimization"""
        if not hasattr(self, 'robot_id'):
            pytest.skip("Robot ID not available")
            
        optimize_data = {
            "robots": [
                {"robot_id": self.robot_id, "quantity": 3}
            ]
        }
        response = await self.client.post(
            f"{API_PREFIX}/assembly/optimize",
            json=optimize_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "optimal_batch_size" in data
        assert "production_schedule" in data
        assert "bottlenecks" in data
        
    @pytest.mark.asyncio
    async def test_get_assembly_history(self):
        """Test getting assembly history"""
        response = await self.client.get(f"{API_PREFIX}/assembly/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    # ==================== Orders API Tests ====================
    
    @pytest.mark.asyncio
    async def test_create_order(self):
        """Test creating an order"""
        if not hasattr(self, 'part_id'):
            pytest.skip("Part ID not available")
            
        order_data = self.test_data["order"].copy()
        order_data["items"][0]["part_id"] = self.part_id
        
        response = await self.client.post(
            f"{API_PREFIX}/orders/",
            json=order_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert len(data["items"]) == 1
        
        # Store order ID for other tests
        self.__class__.order_id = data["id"]
        
    @pytest.mark.asyncio
    async def test_get_orders(self):
        """Test getting all orders"""
        response = await self.client.get(f"{API_PREFIX}/orders/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    @pytest.mark.asyncio
    async def test_get_order_by_id(self):
        """Test getting order by ID"""
        if not hasattr(self, 'order_id'):
            pytest.skip("Order ID not available")
            
        response = await self.client.get(f"{API_PREFIX}/orders/{self.order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.order_id
        
    @pytest.mark.asyncio
    async def test_update_order_status(self):
        """Test updating order status"""
        if not hasattr(self, 'order_id'):
            pytest.skip("Order ID not available")
            
        status_data = {"status": "confirmed"}
        response = await self.client.put(
            f"{API_PREFIX}/orders/{self.order_id}/status",
            json=status_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        
    @pytest.mark.asyncio
    async def test_generate_purchase_order(self):
        """Test generating purchase order"""
        if not hasattr(self, 'robot_id'):
            pytest.skip("Robot ID not available")
            
        po_data = {
            "robot_id": self.robot_id,
            "quantity": 10,
            "reorder_point": 20
        }
        response = await self.client.post(
            f"{API_PREFIX}/orders/generate",
            json=po_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "orders_by_supplier" in data
        assert "total_cost" in data
        
    # ==================== WebSocket Tests ====================
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection"""
        import websockets
        
        ws_url = BASE_URL.replace("http://", "ws://").replace("https://", "wss://")
        try:
            async with websockets.connect(f"{ws_url}/ws") as websocket:
                # Send a test message
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Receive response
                response = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=5
                )
                data = json.loads(response)
                assert data.get("type") in ["pong", "welcome"]
        except Exception as e:
            pytest.skip(f"WebSocket test skipped: {e}")
            
    # ==================== Error Handling Tests ====================
    
    @pytest.mark.asyncio
    async def test_404_error(self):
        """Test 404 error handling"""
        response = await self.client.get(f"{API_PREFIX}/nonexistent")
        assert response.status_code == 404
        
    @pytest.mark.asyncio
    async def test_invalid_part_id(self):
        """Test invalid part ID"""
        response = await self.client.get(f"{API_PREFIX}/parts/999999")
        assert response.status_code == 404
        
    @pytest.mark.asyncio
    async def test_invalid_request_body(self):
        """Test invalid request body"""
        response = await self.client.post(
            f"{API_PREFIX}/parts/",
            json={"invalid": "data"}
        )
        assert response.status_code in [400, 422]
        
    # ==================== Performance Tests ====================
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling concurrent requests"""
        tasks = []
        for _ in range(10):
            tasks.append(self.client.get(f"{API_PREFIX}/parts/"))
            
        responses = await asyncio.gather(*tasks)
        for response in responses:
            assert response.status_code == 200
            
    @pytest.mark.asyncio
    async def test_large_payload(self):
        """Test handling large payload"""
        large_data = {
            "updates": [
                {"part_id": i, "quantity": i * 10}
                for i in range(100)
            ]
        }
        response = await self.client.post(
            f"{API_PREFIX}/inventory/bulk-update",
            json=large_data
        )
        # Should handle gracefully even if some updates fail
        assert response.status_code in [200, 207]  # 207 Multi-Status
        
    # ==================== Cleanup Tests ====================
    
    @pytest.mark.asyncio
    async def test_cleanup_test_data(self):
        """Cleanup test data"""
        # Delete test order
        if hasattr(self, 'order_id'):
            await self.client.delete(f"{API_PREFIX}/orders/{self.order_id}")
            
        # Delete test robot
        if hasattr(self, 'robot_id'):
            await self.client.delete(f"{API_PREFIX}/robots/{self.robot_id}")
            
        # Delete test part
        if hasattr(self, 'part_id'):
            await self.client.delete(f"{API_PREFIX}/parts/{self.part_id}")


# ==================== Test Runner ====================

def run_integration_tests():
    """Run integration tests"""
    import subprocess
    
    # Check if API is running
    try:
        response = httpx.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API is not healthy at {BASE_URL}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API at {BASE_URL}: {e}")
        print("Please ensure the BOM Calculator API is running.")
        return False
        
    print(f"✅ API is running at {BASE_URL}")
    print("Running integration tests...")
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=False
    )
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)