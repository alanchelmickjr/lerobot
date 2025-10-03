#!/usr/bin/env python3
"""
Simple Touch UI with OAK-D S2 Camera Background
Full-screen camera feed with overlay controls
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageTk

# Add lerobot to path
lerobot_path = Path('/home/feetech/lerobot/src')
if lerobot_path.exists() and str(lerobot_path) not in sys.path:
    sys.path.insert(0, str(lerobot_path))

from bimanual_api import BiManualAPI
from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader

# Import OAK camera support
try:
    from lerobot.cameras.depthai import DepthAICamera, DepthAICameraConfig
    from lerobot.cameras.configs import ColorMode
    CAMERA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Camera support not available: {e}")
    CAMERA_AVAILABLE = False

class SimpleTouchUI:
    def __init__(self):
        self.api = BiManualAPI()
        self.root = tk.Tk()
        
        # Robot control state
        self.robot = None
        self.teleop = None
        self.teleoperation_active = False
        self.control_thread = None
        
        # Camera state
        self.camera = None
        self.camera_active = False
        self.camera_thread = None
        self.camera_stop_event = threading.Event()
        
        # UI elements
        self.video_label = None
        self.overlay_frame = None
        
        self.setup_ui()
        self.setup_camera()
        
    def setup_ui(self):
        """Setup touch-optimized UI with camera background"""
        self.root.title("Bi-Manual Robot Control with OAK-D S2")
        self.root.geometry("800x480")
        self.root.configure(bg='black')
        
        # Make fullscreen on touch devices
        try:
            self.root.attributes('-fullscreen', True)
        except:
            pass
        
        # Create main canvas for video background
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Video background label (will be positioned to fill screen)
        self.video_label = tk.Label(self.canvas, bg='black')
        self.video_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Overlay frame for UI elements (transparent background)
        self.overlay_frame = tk.Frame(self.canvas, bg='black')
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay_frame.configure(bg='')  # Transparent
        
        # Status label with semi-transparent background
        status_bg_frame = tk.Frame(self.overlay_frame, bg='black', relief='solid', bd=1)
        status_bg_frame.pack(pady=20, padx=20, fill='x')
        
        self.status_label = tk.Label(
            status_bg_frame,
            text="🔍 Checking system...",
            font=('Arial', 16, 'bold'),
            bg='black',
            fg='white',
            pady=10
        )
        self.status_label.pack()
        
        # Mode buttons frame (initially hidden)
        self.button_frame = tk.Frame(self.overlay_frame, bg='black')
        
        modes = [
            ("🤝 COORDINATED", "#27ae60", self.start_coordinated),
            ("🆓 INDEPENDENT", "#3498db", self.start_independent),  
            ("🪞 MIRROR", "#9b59b6", self.start_mirror)
        ]
        
        for text, color, command in modes:
            btn = tk.Button(
                self.button_frame,
                text=text,
                font=('Arial', 20, 'bold'),
                bg=color,
                fg='white',
                activebackground=color,
                activeforeground='white',
                relief='flat',
                bd=0,
                pady=20,
                command=command
            )
            btn.pack(pady=10, padx=50, fill='x')
            
        # Exit button (always visible at bottom)
        exit_frame = tk.Frame(self.overlay_frame, bg='black')
        exit_frame.pack(side='bottom', fill='x', pady=20, padx=20)
        
        exit_btn = tk.Button(
            exit_frame,
            text="❌ EXIT",
            font=('Arial', 16, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            relief='flat',
            bd=2,
            pady=10,
            command=self.exit_app
        )
        exit_btn.pack(side='right')
        
        # Camera toggle button
        if CAMERA_AVAILABLE:
            camera_btn = tk.Button(
                exit_frame,
                text="📷 CAMERA",
                font=('Arial', 16, 'bold'),
                bg='#2980b9',
                fg='white',
                activebackground='#1f618d',
                relief='flat',
                bd=2,
                pady=10,
                command=self.toggle_camera
            )
            camera_btn.pack(side='left')
        
        # Check system in background
        threading.Thread(target=self.check_system, daemon=True).start()
    
    def setup_camera(self):
        """Initialize OAK-D S2 camera"""
        if not CAMERA_AVAILABLE:
            print("📷 Camera not available - DepthAI not installed")
            return
            
        try:
            config = DepthAICameraConfig(
                device_id="auto",  # Auto-detect OAK camera
                fps=30,
                width=640,
                height=480,
                color_mode=ColorMode.RGB,
                use_depth=False  # Disable depth for performance
            )
            self.camera = DepthAICamera(config)
            print("📷 OAK-D S2 camera initialized")
        except Exception as e:
            print(f"📷 Camera initialization failed: {e}")
            self.camera = None
    
    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.camera:
            self.setup_camera()
            if not self.camera:
                return
                
        if self.camera_active:
            self.stop_camera()
        else:
            self.start_camera()
    
    def start_camera(self):
        """Start camera feed"""
        if not self.camera:
            return
            
        try:
            self.camera.connect()
            self.camera_active = True
            self.camera_stop_event.clear()
            
            # Start camera thread
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            
            print("📷 Camera feed started")
        except Exception as e:
            print(f"📷 Camera start failed: {e}")
    
    def stop_camera(self):
        """Stop camera feed"""
        if self.camera_active:
            self.camera_active = False
            self.camera_stop_event.set()
            
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=2.0)
                
            if self.camera and self.camera.is_connected:
                self.camera.disconnect()
                
            # Clear video display
            self.video_label.configure(image='', bg='black')
            print("📷 Camera feed stopped")
    
    def _camera_loop(self):
        """Background camera capture loop"""
        while self.camera_active and not self.camera_stop_event.is_set():
            try:
                if self.camera and self.camera.is_connected:
                    # Read frame from camera
                    frame = self.camera.read()
                    
                    # Update display in main thread
                    self.root.after(0, lambda f=frame: self._update_camera_display(f))
                    
                time.sleep(1/30)  # ~30 FPS
                
            except Exception as e:
                print(f"📷 Camera error: {e}")
                time.sleep(0.1)
    
    def _update_camera_display(self, frame):
        """Update camera display in UI"""
        try:
            # Get current window size
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()
            
            if window_width <= 1 or window_height <= 1:
                return  # Window not ready
            
            # Resize frame to fit window while maintaining aspect ratio
            frame_height, frame_width = frame.shape[:2]
            
            # Calculate scaling to fill the entire window
            scale_w = window_width / frame_width
            scale_h = window_height / frame_height
            scale = max(scale_w, scale_h)  # Use max to fill entire window
            
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height))
            
            # Crop to fit window exactly (center crop)
            if new_width > window_width:
                x_offset = (new_width - window_width) // 2
                resized_frame = resized_frame[:, x_offset:x_offset+window_width]
            
            if new_height > window_height:
                y_offset = (new_height - window_height) // 2
                resized_frame = resized_frame[y_offset:y_offset+window_height, :]
            
            # Convert to PIL Image and then to PhotoImage
            image_pil = Image.fromarray(resized_frame)
            photo = ImageTk.PhotoImage(image_pil)
            
            # Update video label
            self.video_label.configure(image=photo)
            self.video_label.image = photo  # Keep a reference
            
        except Exception as e:
            print(f"📷 Display update error: {e}")
    
    def check_system(self):
        """Check system status (API call)"""
        time.sleep(1)  # Brief delay for UI to load
        
        status = self.api.get_system_status()
        
        if status['ready']:
            self.root.after(0, self.show_ready)
        else:
            error_msg = f"❌ System not ready\nHardware: {status['hardware']['status']}\nImports: {'✅' if status['imports_ok'] else '❌'}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def show_ready(self):
        """Show ready UI with mode selection"""
        self.status_label.config(
            text="🎉 Bi-Manual System Ready!\nSelect coordination mode:",
            fg='#2ecc71'
        )
        self.button_frame.pack(expand=True, fill='both', padx=50)
    
    def show_error(self, error_msg):
        """Show error status"""
        self.status_label.config(text=error_msg, fg='#e74c3c')
    
    def start_coordinated(self):
        """Start coordinated mode - 1 leader controls 2 followers together"""
        self.status_label.config(text="🤝 Connecting COORDINATED mode...", fg='#27ae60')
        threading.Thread(target=self._start_coordinated_control, daemon=True).start()
        
    def start_independent(self):
        """Start independent mode - 2 leaders control 2 followers separately"""
        self.status_label.config(text="🆓 Connecting INDEPENDENT mode...", fg='#3498db')
        threading.Thread(target=self._start_independent_control, daemon=True).start()
        
    def start_mirror(self):
        """Start mirror mode - 1 leader mirrors to both followers"""
        self.status_label.config(text="🪞 Connecting MIRROR mode...", fg='#9b59b6')
        threading.Thread(target=self._start_mirror_control, daemon=True).start()
    
    def _start_coordinated_control(self):
        """COORDINATED: Use left leader for both arms with EOF protection"""
        try:
            status = self.api.get_system_status()
            if not status['ready']:
                self.root.after(0, lambda: self.show_error("System not ready"))
                return
            
            ports = status['hardware']['mapping']
            
            # Create configs - COORDINATED: Use left leader port for both arms
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],
                right_arm_port=ports['right_follower'],
                id="bimanual_follower"
            )
            
            # COORDINATED: Use BOTH leader ports (left controls both, right ignored in loop)
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],
                right_arm_port=ports['right_leader'],  # ✅ FIXED - use distinct port
                id="coordinated_leader"
            )
            
            # Connect with error handling
            self.robot = BiSO100Follower(robot_config)
            self.teleop = BiSO100Leader(teleop_config)
            
            self.root.after(0, lambda: self.status_label.config(text="🔗 Connecting robots...", fg='#f39c12'))
            
            self.robot.connect()
            self.teleop.connect()
            
            # Start control loop
            self.teleoperation_active = True
            self.control_thread = threading.Thread(target=self._control_loop, args=("COORDINATED",), daemon=True)
            self.control_thread.start()
            
            self.root.after(0, lambda: self.show_control_interface("COORDINATED"))
            
        except Exception as e:
            error_msg = f"❌ COORDINATED connection failed:\n{str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def _start_independent_control(self):
        """INDEPENDENT: Use both leaders to control respective followers"""
        try:
            status = self.api.get_system_status()
            if not status['ready']:
                self.root.after(0, lambda: self.show_error("System not ready"))
                return
            
            ports = status['hardware']['mapping']
            
            # Create configs - Both leaders active
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],
                right_arm_port=ports['right_follower'],
                id="bimanual_follower"
            )
            
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],
                right_arm_port=ports['right_leader'],
                id="bimanual_leader"
            )
            
            # Connect
            self.robot = BiSO100Follower(robot_config)
            self.teleop = BiSO100Leader(teleop_config)
            
            self.root.after(0, lambda: self.status_label.config(text="🔗 Connecting robots...", fg='#f39c12'))
            
            self.robot.connect()
            self.teleop.connect()
            
            # Start control loop
            self.teleoperation_active = True
            self.control_thread = threading.Thread(target=self._control_loop, args=("INDEPENDENT",), daemon=True)
            self.control_thread.start()
            
            self.root.after(0, lambda: self.show_control_interface("INDEPENDENT"))
            
        except Exception as e:
            error_msg = f"❌ INDEPENDENT connection failed:\n{str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def _start_mirror_control(self):
        """MIRROR: Left leader controls left follower, right mirrors left"""
        try:
            status = self.api.get_system_status()
            if not status['ready']:
                self.root.after(0, lambda: self.show_error("System not ready"))
                return
            
            ports = status['hardware']['mapping']
            
            # Create configs - MIRROR: Use left leader for left arm, mirror to right
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],
                right_arm_port=ports['right_follower'],
                id="bimanual_follower"
            )
            
            # MIRROR: Use only left leader port, right_arm_port=None for mirroring
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],
                right_arm_port=None,  # No right leader - mirror left to right
                id="mirror_leader"
            )
            
            # Connect with error handling
            self.robot = BiSO100Follower(robot_config)
            self.teleop = BiSO100Leader(teleop_config)
            
            self.root.after(0, lambda: self.status_label.config(text="🔗 Connecting robots...", fg='#f39c12'))
            
            self.robot.connect()
            self.teleop.connect()
            
            # Start control loop
            self.teleoperation_active = True
            self.control_thread = threading.Thread(target=self._control_loop, args=("MIRROR",), daemon=True)
            self.control_thread.start()
            
            self.root.after(0, lambda: self.show_control_interface("MIRROR"))
            
        except Exception as e:
            error_msg = f"❌ MIRROR connection failed:\n{str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def _control_loop(self, mode):
        """Main teleoperation control loop"""
        import time
        
        loop_count = 0
        start_time = time.time()
        
        try:
            while self.teleoperation_active:
                # Get action from leader
                action = self.teleop.get_action()
                
                # Handle coordinated mode - LEFT leader controls both followers
                if mode == "COORDINATED":
                    # Extract left leader actions only
                    left_actions = {k: v for k, v in action.items() if k.startswith('left_')}
                    
                    # Create coordinated action: left leader → both followers
                    coordinated_action = {}
                    for left_key, left_val in left_actions.items():
                        # Send to left follower
                        coordinated_action[left_key] = left_val
                        # Mirror to right follower
                        right_key = left_key.replace('left_', 'right_')
                        coordinated_action[right_key] = left_val
                    
                    action = coordinated_action
                
                # Send to followers
                self.robot.send_action(action)
                
                # Update status every 100 loops
                loop_count += 1
                if loop_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed if elapsed > 0 else 0
                    
                    status_text = f"🎮 {mode} Active | Rate: {rate:.1f} Hz | Loops: {loop_count}"
                    self.root.after(0, lambda t=status_text: self.status_label.config(text=t, fg='#27ae60'))
                
                time.sleep(0.01)  # 100Hz target
                
        except Exception as e:
            error_msg = f"❌ Control error: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
            
        finally:
            self._cleanup_robots()
    
    def show_control_interface(self, mode):
        """Show active control interface"""
        # Clear existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
            
        # Show active status
        self.status_label.config(
            text=f"🎮 {mode} MODE ACTIVE!\nMove the leader arms to control robots",
            fg='#27ae60'
        )
        
        # Add stop button with semi-transparent background
        stop_frame = tk.Frame(self.button_frame, bg='black', relief='solid', bd=2)
        stop_frame.pack(pady=20, padx=50, fill='x')
        
        stop_btn = tk.Button(
            stop_frame,
            text="⏹️ STOP",
            font=('Arial', 24, 'bold'),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            pady=15,
            command=self.stop_control
        )
        stop_btn.pack(fill='x', padx=5, pady=5)
        
        # Show mode info
        mode_info = {
            'COORDINATED': '🤝 Left leader controls both followers',
            'INDEPENDENT': '🆓 Left→Left, Right→Right control',
            'MIRROR': '🪞 Left leader mirrors to both'
        }
        
        info_frame = tk.Frame(self.button_frame, bg='black', relief='solid', bd=1)
        info_frame.pack(pady=10, padx=50, fill='x')
        
        info_label = tk.Label(
            info_frame,
            text=mode_info.get(mode, ''),
            font=('Arial', 14),
            bg='black',
            fg='#bdc3c7',
            pady=5
        )
        info_label.pack()
        
        self.button_frame.pack(expand=True, fill='both', padx=50)
    
    def stop_control(self):
        """Stop teleoperation"""
        self.teleoperation_active = False
        self.status_label.config(text="⏹️ Stopping control...", fg='#f39c12')
        
        # Wait for control thread to finish
        if self.control_thread and self.control_thread.is_alive():
            self.control_thread.join(timeout=2.0)
        
        self.status_label.config(text="✅ Control stopped", fg='#27ae60')
        
        # Return to mode selection after delay
        self.root.after(2000, self.return_to_mode_selection)
    
    def return_to_mode_selection(self):
        """Return to mode selection interface"""
        # Clear the button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Recreate mode buttons
        modes = [
            ("🤝 COORDINATED", "#27ae60", self.start_coordinated),
            ("🆓 INDEPENDENT", "#3498db", self.start_independent),
            ("🪞 MIRROR", "#9b59b6", self.start_mirror)
        ]
        
        for text, color, command in modes:
            btn = tk.Button(
                self.button_frame,
                text=text,
                font=('Arial', 20, 'bold'),
                bg=color,
                fg='white',
                activebackground=color,
                activeforeground='white',
                relief='flat',
                bd=0,
                pady=20,
                command=command
            )
            btn.pack(pady=10, padx=50, fill='x')
        
        self.status_label.config(text="🎉 Select coordination mode:", fg='#2ecc71')
    
    def _cleanup_robots(self):
        """Cleanup robot connections"""
        try:
            if self.robot:
                self.robot.disconnect()
                self.robot = None
            if self.teleop:
                self.teleop.disconnect()
                self.teleop = None
        except Exception as e:
            print(f"Cleanup error: {e}")
        
    def exit_app(self):
        """Exit application"""
        self.teleoperation_active = False
        self.stop_camera()  # Stop camera if running
        self._cleanup_robots()
        self.root.quit()
        
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleTouchUI()
    app.run()