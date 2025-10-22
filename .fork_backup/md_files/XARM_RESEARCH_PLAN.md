# xArm Integration Research Plan

## 🎯 **Objective**
Add xArm robotic arm support to LeRobot framework while maintaining compatibility with existing SO101 bi-manual system.

## 🔍 **Current Status in Codebase**
- **Mentioned in**: `DEPLOYMENT_PACKAGE.md` - "XArm (protocol research needed)"
- **Test reference**: `tests/policies/test_policies.py` - commented xArm test case
- **Future goal**: Listed in bi-manual upgrade guide

## 🏭 **xArm Technical Specifications**

### **Communication Protocol**
- **Protocol**: TCP/IP over Ethernet
- **Port**: Default 502 (Modbus TCP) or custom
- **SDK**: xArm-Python-SDK (official UFactory SDK)
- **Data format**: JSON commands / binary protocols

### **Hardware Differences from SO101**
```
SO101:                    xArm6:
- USB Serial              - Ethernet TCP/IP  
- Simple servo control    - Complex trajectory planning
- 6 basic motors          - 6 precision joints + gripper
- ~1kg payload           - 5kg+ payload
- Hobby-grade            - Industrial-grade
```

## 📋 **Implementation Plan**

### **Phase 1: Research & Protocol Analysis**
1. **Study xArm-Python-SDK**
   - Install official SDK: `pip install xarm-python-sdk`
   - Analyze communication patterns
   - Test basic connection and control

2. **Protocol Mapping**
   - Map xArm SDK to LeRobot Robot interface
   - Define action/observation formats
   - Plan configuration structure

### **Phase 2: LeRobot Integration**
1. **Create xArm Robot Classes**
   ```
   src/lerobot/robots/xarm/
   ├── __init__.py
   ├── config_xarm.py          # XArmConfig class
   ├── xarm_follower.py        # XArmFollower implementation
   └── xarm.mdx                # Documentation
   ```

2. **Create xArm Teleoperator** (if needed)
   ```
   src/lerobot/teleoperators/xarm_leader/
   ├── __init__.py
   ├── config_xarm_leader.py   # XArmLeaderConfig
   └── xarm_leader.py          # XArmLeader implementation
   ```

### **Phase 3: Multi-Modal Integration**
1. **Enhanced Detection API**
   - Extend `bimanual_api.py` to detect network-based robots
   - Add xArm auto-discovery via network scanning
   - Support mixed setups (SO101 + xArm)

2. **Scalable UI Updates**
   - Add xArm detection to touch interface
   - Support hybrid configurations
   - Professional-grade control modes

## 🔧 **Technical Challenges**

### **1. Communication Protocol Differences**
```python
# SO101 (Serial)
robot.bus.sync_write("Goal_Position", positions)

# xArm (TCP/IP)  
arm.set_servo_angle(angles, wait=False)
arm.set_position(x, y, z, roll, pitch, yaw)
```

### **2. Control Paradigms**
- **SO101**: Direct motor control
- **xArm**: High-level trajectory planning + low-level execution

### **3. Configuration Complexity**
- **Network discovery**: Find xArm on local network
- **Calibration**: Different from servo-based systems
- **Safety systems**: Industrial-grade safety protocols

## 💡 **Proof of Concept Code**

### **Basic xArm Detection**
```python
def detect_xarm_robots():
    """Detect xArm robots on network"""
    try:
        from xarm.wrapper import XArmAPI
        
        # Common xArm IP ranges
        ip_ranges = [
            "192.168.1.{}", 
            "192.168.0.{}"
        ]
        
        found_arms = []
        for ip_range in ip_ranges:
            for i in range(200, 220):  # Common xArm IP range
                ip = ip_range.format(i)
                try:
                    arm = XArmAPI(ip, timeout=1)
                    if arm.connected:
                        found_arms.append(ip)
                        arm.disconnect()
                except:
                    continue
                    
        return found_arms
    except ImportError:
        return []  # xArm SDK not installed
```

### **LeRobot xArm Config Structure**
```python
@RobotConfig.register_subclass("xarm")
@dataclass
class XArmConfig(RobotConfig):
    ip_address: str = "192.168.1.208"  # Default xArm IP
    model: str = "xarm6"  # xarm5, xarm6, xarm7, lite6
    
    # Safety settings
    max_velocity: float = 100.0  # mm/s
    max_acceleration: float = 1000.0  # mm/s²
    
    # Coordinate system
    use_cartesian: bool = True  # vs joint angles
    
    # Gripper settings  
    has_gripper: bool = True
    gripper_type: str = "vacuum"  # vacuum, electric, pneumatic
```

## 🎯 **Integration with Current System**

### **Enhanced Scalable Detection**
```python
def detect_hardware(self):
    """Detect all robot types: SO101 + xArm + LeKiwi"""
    
    # Current USB detection (SO101)
    usb_robots = self.detect_usb_robots()
    
    # New network detection (xArm) 
    network_robots = self.detect_network_robots()
    
    return {
        'total_robots': len(usb_robots) + len(network_robots),
        'usb_robots': usb_robots,
        'network_robots': network_robots,
        'mixed_setup': len(usb_robots) > 0 and len(network_robots) > 0
    }
```

### **Touch UI Updates**
- **Mixed configurations**: "2x SO101 + 1x xArm6 detected"
- **Professional modes**: High-precision coordination
- **Network status**: Connection quality indicators

## 📦 **Dependencies Required**
```bash
pip install xarm-python-sdk  # Official UFactory SDK
pip install netifaces        # Network interface detection  
pip install python-nmap      # Network scanning (optional)
```

## 🎯 **Success Criteria**
1. **xArm detection** working alongside SO101 detection
2. **Basic teleoperation** of single xArm
3. **Mixed bi-manual**: SO101 + xArm coordination
4. **Touch UI integration** with network robots
5. **Backwards compatibility** with existing SO101 setups

## 🚀 **Future Possibilities**
- **Industrial bi-manual**: 2x xArm6 high-precision coordination
- **Hybrid setups**: xArm precision + SO101 affordability  
- **Multi-site control**: Network-based remote operation
- **Professional workflows**: Integration with industrial systems

---

**Next Step**: Install xArm-Python-SDK and begin protocol analysis phase.