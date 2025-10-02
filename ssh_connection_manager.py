#!/usr/bin/env python3
"""
SSH Connection Manager for LeRobot Remote Access
Auto-login functionality with sshpass integration
"""

import asyncio
import subprocess
import threading
import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import os
import shutil

class ConnectionStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

@dataclass
class ConnectionInfo:
    session_id: str
    host: str
    username: str
    status: ConnectionStatus
    connected_at: Optional[float] = None
    last_heartbeat: Optional[float] = None
    error_count: int = 0
    process: Optional[subprocess.Popen] = None

class SSHConnectionManager:
    """Manages SSH connections with auto-login capabilities using sshpass"""
    
    def __init__(self, 
                 host: str = "192.168.88.22",
                 username: str = "feetech", 
                 password: str = "feetech",
                 heartbeat_interval: int = 30,
                 connection_timeout: int = 10,
                 max_retry_attempts: int = 3):
        """
        Initialize SSH Connection Manager
        
        Args:
            host: Target Linux box IP address
            username: SSH username
            password: SSH password
            heartbeat_interval: Seconds between heartbeat checks
            connection_timeout: Timeout for SSH connections
            max_retry_attempts: Maximum reconnection attempts
        """
        self.host = host
        self.username = username
        self.password = password
        self.heartbeat_interval = heartbeat_interval
        self.connection_timeout = connection_timeout
        self.max_retry_attempts = max_retry_attempts
        
        # Connection pool
        self.connection_pool: Dict[str, ConnectionInfo] = {}
        
        # Background tasks
        self.heartbeat_task = None
        self.heartbeat_running = False
        
        # Logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Check sshpass availability
        self._check_sshpass_availability()
        
    def _check_sshpass_availability(self) -> bool:
        """Check if sshpass is installed and available"""
        if not shutil.which("sshpass"):
            self.logger.error("❌ sshpass not found! Install with: sudo apt-get install sshpass")
            return False
        
        self.logger.info("✅ sshpass found and available")
        return True
        
    def install_sshpass(self) -> bool:
        """Install sshpass dependency"""
        try:
            self.logger.info("🔧 Installing sshpass...")
            result = subprocess.run([
                "sudo", "apt-get", "install", "-y", "sshpass"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info("✅ sshpass installed successfully")
                return True
            else:
                self.logger.error(f"❌ sshpass installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("❌ sshpass installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ sshpass installation error: {e}")
            return False
    
    def connect(self, session_id: str = "default") -> bool:
        """
        Establish SSH connection using sshpass
        
        Args:
            session_id: Unique identifier for this connection
            
        Returns:
            True if connection successful, False otherwise
        """
        if session_id in self.connection_pool:
            connection = self.connection_pool[session_id]
            if connection.status == ConnectionStatus.CONNECTED:
                self.logger.info(f"Session '{session_id}' already connected")
                return True
        
        # Create new connection info
        connection = ConnectionInfo(
            session_id=session_id,
            host=self.host,
            username=self.username,
            status=ConnectionStatus.CONNECTING
        )
        
        self.connection_pool[session_id] = connection
        
        try:
            self.logger.info(f"🌐 Connecting to {self.username}@{self.host}...")
            
            # Test connection first
            test_cmd = [
                "sshpass", "-p", self.password,
                "ssh", "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no",
                f"{self.username}@{self.host}",
                "echo 'Connection test successful'"
            ]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=self.connection_timeout
            )
            
            if result.returncode == 0:
                connection.status = ConnectionStatus.CONNECTED
                connection.connected_at = time.time()
                connection.last_heartbeat = time.time()
                connection.error_count = 0
                
                self.logger.info(f"✅ SSH connection established to {self.host}")
                
                # Start heartbeat monitoring if not already running
                if not self.heartbeat_running:
                    self._start_heartbeat_monitoring()
                
                return True
            else:
                connection.status = ConnectionStatus.ERROR
                connection.error_count += 1
                self.logger.error(f"❌ SSH connection failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            connection.status = ConnectionStatus.ERROR
            connection.error_count += 1
            self.logger.error("❌ SSH connection timed out")
            return False
        except Exception as e:
            connection.status = ConnectionStatus.ERROR
            connection.error_count += 1
            self.logger.error(f"❌ SSH connection error: {e}")
            return False
    
    async def execute_command(self, command: str, session_id: str = "default") -> Dict:
        """
        Execute remote command via SSH
        
        Args:
            command: Command to execute on remote system
            session_id: Connection session to use
            
        Returns:
            Dictionary with command result
        """
        if session_id not in self.connection_pool:
            return {
                "success": False,
                "error": f"Session '{session_id}' not found",
                "stdout": "",
                "stderr": ""
            }
        
        connection = self.connection_pool[session_id]
        if connection.status != ConnectionStatus.CONNECTED:
            return {
                "success": False,
                "error": f"Session '{session_id}' not connected",
                "stdout": "",
                "stderr": ""
            }
        
        try:
            self.logger.info(f"🔧 Executing remote command: {command}")
            
            ssh_cmd = [
                "sshpass", "-p", self.password,
                "ssh", "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no",
                f"{self.username}@{self.host}",
                command
            ]
            
            result = await asyncio.create_subprocess_exec(
                *ssh_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=30.0  # 30 second timeout for commands
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode()
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Command execution timed out",
                "stdout": "",
                "stderr": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Command execution error: {e}",
                "stdout": "",
                "stderr": ""
            }
    
    async def start_remote_control(self, mode: str = "coordinated", session_id: str = "default") -> bool:
        """
        Start remote bimanual control session
        
        Args:
            mode: Control mode (coordinated, independent, mirror)
            session_id: Connection session to use
            
        Returns:
            True if remote control started successfully
        """
        # Setup remote environment first
        setup_commands = [
            "cd ~/lerobot",
            "source ~/miniconda3/bin/activate",
            "conda activate lerobot"
        ]
        
        setup_command = " && ".join(setup_commands)
        result = await self.execute_command(setup_command, session_id)
        
        if not result["success"]:
            self.logger.error(f"❌ Remote environment setup failed: {result['error']}")
            return False
        
        # Start remote bimanual control
        remote_cmd = f"cd ~/lerobot && python simple_touch_ui.py --mode {mode}"
        result = await self.execute_command(remote_cmd, session_id)
        
        if result["success"]:
            self.logger.info(f"✅ Remote {mode} control started")
            return True
        else:
            self.logger.error(f"❌ Remote control startup failed: {result['error']}")
            return False
    
    def is_connected(self, session_id: str = "default") -> bool:
        """Check if session is connected"""
        if session_id not in self.connection_pool:
            return False
        
        connection = self.connection_pool[session_id]
        return connection.status == ConnectionStatus.CONNECTED
    
    def get_connection_status(self, session_id: str = "default") -> Dict:
        """Get detailed connection status"""
        if session_id not in self.connection_pool:
            return {
                "exists": False,
                "status": "not_found"
            }
        
        connection = self.connection_pool[session_id]
        return {
            "exists": True,
            "status": connection.status.value,
            "host": connection.host,
            "username": connection.username,
            "connected_at": connection.connected_at,
            "last_heartbeat": connection.last_heartbeat,
            "error_count": connection.error_count,
            "uptime": time.time() - connection.connected_at if connection.connected_at else 0
        }
    
    def disconnect(self, session_id: str = "default") -> bool:
        """Disconnect SSH session"""
        if session_id not in self.connection_pool:
            return False
        
        connection = self.connection_pool[session_id]
        
        try:
            if connection.process and connection.process.poll() is None:
                connection.process.terminate()
                connection.process.wait(timeout=5)
            
            connection.status = ConnectionStatus.DISCONNECTED
            self.logger.info(f"✅ Session '{session_id}' disconnected")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error disconnecting session '{session_id}': {e}")
            return False
    
    def disconnect_all(self) -> None:
        """Disconnect all SSH sessions"""
        for session_id in list(self.connection_pool.keys()):
            self.disconnect(session_id)
        
        # Stop heartbeat monitoring
        self.heartbeat_running = False
        if self.heartbeat_task:
            self.heartbeat_task.join(timeout=2.0)
    
    def _start_heartbeat_monitoring(self) -> None:
        """Start background heartbeat monitoring"""
        if self.heartbeat_running:
            return
        
        self.heartbeat_running = True
        self.heartbeat_task = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.heartbeat_task.start()
        self.logger.info("🔄 Started heartbeat monitoring")
    
    def _heartbeat_loop(self) -> None:
        """Background heartbeat monitoring loop"""
        while self.heartbeat_running:
            try:
                for session_id, connection in self.connection_pool.items():
                    if connection.status == ConnectionStatus.CONNECTED:
                        self._check_connection_health(session_id)
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Heartbeat error: {e}")
                time.sleep(5)  # Shorter retry interval on error
    
    def _check_connection_health(self, session_id: str) -> None:
        """Check health of a specific connection"""
        if session_id not in self.connection_pool:
            return
        
        connection = self.connection_pool[session_id]
        
        try:
            # Simple ping command to test connection
            test_cmd = [
                "sshpass", "-p", self.password,
                "ssh", "-o", "ConnectTimeout=3",
                "-o", "StrictHostKeyChecking=no",
                f"{self.username}@{self.host}",
                "echo 'heartbeat'"
            ]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                connection.last_heartbeat = time.time()
                connection.error_count = 0
                self.logger.debug(f"💓 Heartbeat OK for session '{session_id}'")
            else:
                connection.error_count += 1
                self.logger.warning(f"⚠️ Heartbeat failed for session '{session_id}' (errors: {connection.error_count})")
                
                # Auto-reconnect if too many errors
                if connection.error_count >= 3:
                    self.logger.info(f"🔄 Auto-reconnecting session '{session_id}'...")
                    self._attempt_reconnect(session_id)
                    
        except Exception as e:
            connection.error_count += 1
            self.logger.warning(f"⚠️ Heartbeat exception for session '{session_id}': {e}")
    
    def _attempt_reconnect(self, session_id: str) -> None:
        """Attempt to reconnect a failed session"""
        if session_id not in self.connection_pool:
            return
        
        connection = self.connection_pool[session_id]
        connection.status = ConnectionStatus.RECONNECTING
        
        for attempt in range(self.max_retry_attempts):
            self.logger.info(f"🔄 Reconnection attempt {attempt + 1}/{self.max_retry_attempts} for '{session_id}'")
            
            if self.connect(session_id):
                self.logger.info(f"✅ Session '{session_id}' reconnected successfully")
                return
            
            time.sleep(5)  # Wait before retry
        
        # All reconnection attempts failed
        connection.status = ConnectionStatus.ERROR
        self.logger.error(f"❌ Failed to reconnect session '{session_id}' after {self.max_retry_attempts} attempts")

# Convenience functions for easy integration
def create_ssh_manager(**kwargs) -> SSHConnectionManager:
    """Create and return an SSH connection manager instance"""
    return SSHConnectionManager(**kwargs)

def test_remote_connection(host: str = "192.168.88.22", 
                          username: str = "feetech", 
                          password: str = "feetech") -> bool:
    """Test SSH connection to remote Linux box"""
    manager = SSHConnectionManager(host=host, username=username, password=password)
    return manager.connect()

async def execute_remote_command(command: str, 
                                host: str = "192.168.88.22",
                                username: str = "feetech", 
                                password: str = "feetech") -> Dict:
    """Execute a single remote command"""
    manager = SSHConnectionManager(host=host, username=username, password=password)
    if manager.connect():
        result = await manager.execute_command(command)
        manager.disconnect()
        return result
    else:
        return {
            "success": False,
            "error": "Failed to connect to remote host",
            "stdout": "",
            "stderr": ""
        }

if __name__ == "__main__":
    # Test the SSH connection manager
    print("🧪 Testing SSH Connection Manager...")
    
    manager = SSHConnectionManager()
    
    # Test connection
    if manager.connect():
        print("✅ SSH connection successful!")
        
        # Test command execution
        async def test_commands():
            result = await manager.execute_command("whoami")
            print(f"Remote user: {result.get('stdout', '').strip()}")
            
            result = await manager.execute_command("pwd")
            print(f"Remote directory: {result.get('stdout', '').strip()}")
            
            result = await manager.execute_command("uname -a")
            print(f"Remote system: {result.get('stdout', '').strip()}")
        
        # Run async test
        asyncio.run(test_commands())
        
        # Test status
        status = manager.get_connection_status()
        print(f"Connection status: {status}")
        
        # Cleanup
        manager.disconnect_all()
        print("✅ Test completed successfully")
    else:
        print("❌ SSH connection failed!")
        print("Make sure the remote Linux box is accessible at 192.168.88.22")