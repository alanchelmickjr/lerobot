# LeRover: Autonomous Mobile Robot

LeRover is an autonomous version of the LeKiwi mobile robot, featuring AI-powered navigation and manipulation capabilities.

## Features

- **Autonomous Navigation**: AI-driven obstacle avoidance and path planning
- **Vision-Language Processing**: Local SmolVLM integration for scene understanding
- **Remote AI Inference**: Distributed AI processing over WiFi via Raspberry Pi
- **High-Resolution Cameras**: Support for 1080p and 2K camera feeds
- **ALOHA Integration**: Optional advanced manipulation policies
- **Teleoperation with Autonomy**: Manual control with autonomous assistance

## Hardware Requirements

- LeKiwi mobile robot base
- SO-101 or compatible robotic arm
- Raspberry Pi 4/5 with camera
- 1080p or 2K cameras (front and wrist)
- WiFi network

## Software Requirements

```bash
pip install lerobot[all]  # Full installation with all dependencies
# Additional requirements for AI features:
pip install transformers torch torchvision
```

## Quick Start

### 1. Setup the AI Inference Server (Raspberry Pi)

```bash
# On your Raspberry Pi
python ai_inference_server.py --port 8888
```

### 2. Autonomous Operation

```bash
# Direct autonomous control
python autonomous_lerover.py \
  --task "Navigate autonomously and avoid obstacles" \
  --raspi-ip 192.168.1.100 \
  --smolvlm-path /path/to/smolvlm
```

### 3. Teleoperation with Autonomy

```bash
# Remote control with autonomy toggle
python teleoperate_lerover.py
```

## Configuration

### Basic Configuration

```python
from lerobot.robots.lerover import LeRoverConfig, LeRoverAutonomyConfig

autonomy_config = LeRoverAutonomyConfig(
    enable_ai_inference=True,
    raspi_ip="192.168.1.100",
    raspi_port=8888,
    smolvlm_model_path="/path/to/smolvlm",
    autonomy_enabled=True,
    vision_fps=10,
    navigation_speed_mps=0.2
)

config = LeRoverConfig(
    port="/dev/ttyACM0",
    autonomy=autonomy_config
)
```

### Camera Configuration

LeRover supports high-resolution cameras:

- **Front Camera**: 1920x1080 (1080p) for navigation
- **Wrist Camera**: 2048x1536 (2K) for manipulation

## Usage Examples

### Basic Autonomous Navigation

```python
from lerobot.robots.lerover import LeRover, LeRoverConfig

config = LeRoverConfig(autonomy=LeRoverAutonomyConfig(autonomy_enabled=True))
robot = LeRover(config)
robot.connect()
robot.start_autonomy("Navigate to the blue object")
```

### Remote Client Control

```python
from lerobot.robots.lerover import LeRoverClient, LeRoverClientConfig

config = LeRoverClientConfig(remote_ip="192.168.1.100")
client = LeRoverClient(config)
client.connect()
client.toggle_autonomy()  # Enable autonomous mode
```

### Teleoperation with Autonomy

```python
from lerobot.teleoperators.keyboard import KeyboardTeleoperator
from lerobot.robots.lerover import LeRoverClient

# Setup teleoperator and robot client
teleop = KeyboardTeleoperator()
robot = LeRoverClient(config)

# Main control loop
while True:
    obs = robot.get_observation()
    action = teleop(obs)
    action["autonomy_active"] = float(robot.autonomy_enabled)
    robot.send_action(action)
```

## AI Integration

### SmolVLM Integration

For local vision-language processing:

```python
autonomy_config = LeRoverAutonomyConfig(
    smolvlm_model_path="/path/to/smolvlm-model",
    smolvlm_device="cpu"  # or "cuda"
)
```

### ALOHA Policy Integration

For advanced manipulation:

```python
autonomy_config = LeRoverAutonomyConfig(
    use_aloha_policy=True,
    aloha_model_path="/path/to/aloha-policy"
)
```

### Remote AI Inference

The AI inference server provides:

- Real-time obstacle detection
- Scene understanding
- Action recommendation
- Task-specific processing

## Safety Features

- **Emergency Stop**: Immediate halt via `emergency_stop()` method
- **Obstacle Detection**: Automatic stopping when obstacles are detected
- **Speed Limiting**: Configurable maximum velocities
- **Timeout Protection**: Automatic shutdown after maximum operation time
- **Watchdog Timer**: Network communication monitoring

## Network Architecture

```
[Control PC] <---WiFi---> [Raspberry Pi with AI]
       |                        |
       |                        |
    LeRover Client         AI Inference Server
       |                        |
       v                        v
[LeRover Robot] <---USB/Serial---> [Motors & Cameras]
```

## Troubleshooting

### Connection Issues
- Ensure Raspberry Pi and robot are on the same network
- Check firewall settings for port 8888
- Verify serial port permissions for motor control

### AI Inference Problems
- Confirm PyTorch and transformers are installed
- Check GPU memory if using CUDA
- Verify camera calibration and image quality

### Performance Issues
- Reduce vision_fps for slower hardware
- Use CPU-only mode if GPU is unavailable
- Monitor system resources during operation

## Contributing

To extend LeRover:

1. Add new AI models to `SmolVLMAgent`
2. Implement additional policies in autonomy loop
3. Extend camera configurations for new sensors
4. Add new teleoperation modes

## License

This implementation follows the same Apache 2.0 license as LeRobot.