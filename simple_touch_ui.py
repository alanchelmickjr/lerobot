#!/usr/bin/env python3
"""
Simple Touch UI - Thin layer over bimanual_api
Small, simple, elegant
"""
import tkinter as tk
from tkinter import ttk
import threading
import time
import sys
from pathlib import Path

# Add lerobot to path
lerobot_path = Path('/home/feetech/lerobot/src')
if lerobot_path.exists() and str(lerobot_path) not in sys.path:
    sys.path.insert(0, str(lerobot_path))

from bimanual_api import BiManualAPI
from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader

class SimpleTouchUI:
    def __init__(self):
        self.api = BiManualAPI()
        self.root = tk.Tk()
        
        # Robot control state
        self.robot = None
        self.teleop = None
        self.teleoperation_active = False
        self.control_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup touch-optimized UI"""
        self.root.title("Bi-Manual Robot Control")
        self.root.geometry("800x480")
        self.root.configure(bg='#2c3e50')
        
        # Make fullscreen on touch devices
        try:
            self.root.attributes('-fullscreen', True)
        except:
            pass
            
        # Status
        self.status_label = tk.Label(
            self.root, 
            text="🔍 Checking system...",
            font=('Arial', 16),
            bg='#2c3e50', 
            fg='white'
        )
        self.status_label.pack(pady=20)
        
        # Mode buttons (initially hidden)
        self.button_frame = tk.Frame(self.root, bg='#2c3e50')
        
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
            
        # Exit button
        exit_btn = tk.Button(
            self.root,
            text="❌ EXIT",
            font=('Arial', 16),
            bg='#e74c3c',
            fg='white',
            command=self.exit_app
        )
        exit_btn.pack(side='bottom', pady=20)
        
        # Check system in background
        threading.Thread(target=self.check_system, daemon=True).start()
    
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
        """COORDINATED: Use left leader to control both followers together"""
        try:
            status = self.api.get_system_status()
            if not status['ready']:
                self.root.after(0, lambda: self.show_error("System not ready"))
                return
            
            ports = status['hardware']['mapping']
            
            # Create configs - Use LEFT leader for coordinated control
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],
                right_arm_port=ports['right_follower'],
                id="bimanual_follower"
            )
            
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],
                right_arm_port=ports['left_leader'],  # Both use left leader
                id="coordinated_leader"
            )
            
            # Connect
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
        """MIRROR: Use left leader to mirror to both followers"""
        # Same as coordinated for now - both use left leader
        self._start_coordinated_control()
    
    def _control_loop(self, mode):
        """Main teleoperation control loop"""
        import time
        
        loop_count = 0
        start_time = time.time()
        
        try:
            while self.teleoperation_active:
                # Get action from leader
                action = self.teleop.get_action()
                
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
        
        # Add stop button
        stop_btn = tk.Button(
            self.button_frame,
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
        stop_btn.pack(pady=20, padx=50, fill='x')
        
        # Show mode info
        mode_info = {
            'COORDINATED': '🤝 Left leader controls both followers',
            'INDEPENDENT': '🆓 Left→Left, Right→Right control',
            'MIRROR': '🪞 Left leader mirrors to both'
        }
        
        info_label = tk.Label(
            self.button_frame,
            text=mode_info.get(mode, ''),
            font=('Arial', 14),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        info_label.pack(pady=10)
        
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
        self._cleanup_robots()
        self.root.quit()
        
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SimpleTouchUI()
    app.run()