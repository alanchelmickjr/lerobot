#!/usr/bin/env python3
"""
Working Touch UI - Uses proven robot control logic
Based on successful test_independent_mode.py
"""
import tkinter as tk
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

class WorkingTouchUI:
    def __init__(self):
        self.api = BiManualAPI()
        self.robot = None
        self.teleop = None
        self.teleoperation_active = False
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Bi-Manual Robot Control")
        self.root.geometry("800x480")
        self.root.configure(bg='#2c3e50')
        
        # Fullscreen for touch
        try:
            self.root.attributes('-fullscreen', True)
        except:
            pass
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple touch UI"""
        # Title
        title = tk.Label(
            self.root,
            text="🤖🤖 BI-MANUAL CONTROL",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="🔍 Checking system...",
            font=('Arial', 16),
            bg='#2c3e50',
            fg='white'
        )
        self.status_label.pack(pady=10)
        
        # Buttons frame
        self.button_frame = tk.Frame(self.root, bg='#2c3e50')
        self.button_frame.pack(expand=True, pady=20)
        
        # Exit button (always visible)
        exit_btn = tk.Button(
            self.root,
            text="❌ EXIT",
            font=('Arial', 16),
            bg='#e74c3c',
            fg='white',
            command=self.exit_app,
            relief='flat',
            pady=10
        )
        exit_btn.pack(side='bottom', pady=10)
        
        # Check system
        threading.Thread(target=self.check_system, daemon=True).start()
    
    def check_system(self):
        """Check if system is ready"""
        try:
            status = self.api.get_system_status()
            if status['ready']:
                # Store system info for UI adaptation
                self.system_status = status
                self.root.after(0, self.show_ready_ui)
            else:
                error_msg = f"❌ System not ready\nHardware: {status['hardware']['status']}"
                self.root.after(0, lambda: self.show_status(error_msg, '#e74c3c'))
        except Exception as e:
            self.root.after(0, lambda: self.show_status(f"❌ Error: {str(e)}", '#e74c3c'))
    
    def show_ready_ui(self):
        """Show ready UI adapted to detected hardware configuration"""
        hardware = self.system_status['hardware']
        status = hardware['status']
        arm_count = hardware.get('arm_count', 0)
        
        self.show_status(f"🎉 {status.upper()} System Ready!\n{arm_count} arm(s) detected", '#27ae60')
        
        # Dynamic modes based on detected hardware
        if status == 'single_arm':
            modes = [
                ("🤖 SINGLE ARM\n(Leader → Follower)", "#3498db", self.start_single_arm_mode),
            ]
        elif status == 'bi_manual':
            # Keep our working bi-manual modes!
            modes = [
                ("🤝 COORDINATED\n(Left Leader → Both Followers)", "#27ae60", self.start_coordinated_mode),
                ("🆓 INDEPENDENT\n(2 Leaders → 2 Followers)", "#3498db", self.start_independent_mode),
                ("🪞 MIRROR\n(Left Leader → Mirror Both)", "#9b59b6", self.start_mirror_mode)
            ]
        elif status == 'tri_manual':
            modes = [
                ("🔺 TRI-MANUAL\n(3 Leaders → 3 Followers)", "#e67e22", self.start_tri_manual_mode),
            ]
        elif status == 'quad_manual':
            modes = [
                ("🔲 QUAD-MANUAL\n(4 Leaders → 4 Followers)", "#8e44ad", self.start_quad_manual_mode),
            ]
        else:
            # Fallback for unsupported configurations
            modes = [
                (f"⚠️ {status.upper()}\n(Configuration not supported yet)", "#95a5a6", None),
            ]
        
        # Create buttons dynamically
        for text, color, command in modes:
            btn = tk.Button(
                self.button_frame,
                text=text,
                font=('Arial', 16, 'bold'),
                bg=color,
                fg='white',
                activebackground=color,
                relief='flat',
                pady=25,
                command=command,
                state='normal' if command else 'disabled'
            )
            btn.pack(pady=12, padx=50, fill='x')
    
    def start_coordinated_mode(self):
        """Start COORDINATED mode using proven logic"""
        self.show_status("🔗 Starting COORDINATED mode...", '#f39c12')
        threading.Thread(target=self.run_coordinated_control, daemon=True).start()
    
    def start_independent_mode(self):
        """Start INDEPENDENT mode using proven logic"""
        self.show_status("🔗 Starting INDEPENDENT mode...", '#f39c12')
        threading.Thread(target=self.run_independent_control, daemon=True).start()
    
    def start_mirror_mode(self):
        """Start MIRROR mode using proven logic"""
        self.show_status("🔗 Starting MIRROR mode...", '#f39c12')
        threading.Thread(target=self.run_mirror_control, daemon=True).start()
    
    def run_independent_control(self):
        """Run INDEPENDENT control (same logic as test script)"""
        try:
            # Get ports using API
            status = self.api.get_system_status()
            ports = status['hardware']['mapping']
            
            self.root.after(0, lambda: self.show_status("🤖 Connecting robots...", '#f39c12'))
            
            # Create configs (proven working setup)
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],    # ACM2
                right_arm_port=ports['right_follower'],  # ACM3
                id="bimanual_follower"
            )
            
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],     # ACM0
                right_arm_port=ports['right_leader'],   # ACM1
                id="bimanual_leader"
            )
            
            # Connect (same as working test)
            self.robot = BiSO100Follower(robot_config)
            self.robot.connect()
            
            self.teleop = BiSO100Leader(teleop_config)
            self.teleop.connect()
            
            # Show control interface
            self.root.after(0, self.show_control_interface)
            
            # Start control loop (proven working)
            self.teleoperation_active = True
            loop_count = 0
            start_time = time.time()
            
            while self.teleoperation_active:
                # Same proven control logic
                action = self.teleop.get_action()
                self.robot.send_action(action)
                
                # Update status
                loop_count += 1
                if loop_count % 200 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed if elapsed > 0 else 0
                    status_text = f"🎮 INDEPENDENT Active | {rate:.1f} Hz | Loops: {loop_count}"
                    self.root.after(0, lambda t=status_text: self.show_status(t, '#27ae60'))
                
        except Exception as e:
            error_msg = f"❌ Control error: {str(e)}"
            self.root.after(0, lambda: self.show_status(error_msg, '#e74c3c'))
        finally:
            self.cleanup_robots()
    
    def run_coordinated_control(self):
        """Run COORDINATED control - LEFT leader controls BOTH followers"""
        try:
            # Get ports using API (same as INDEPENDENT)
            status = self.api.get_system_status()
            ports = status['hardware']['mapping']
            
            self.root.after(0, lambda: self.show_status("🤖 Connecting robots...", '#f39c12'))
            
            # COORDINATED config: Use ONLY left leader (avoid port duplication!)
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],    # ACM2
                right_arm_port=ports['right_follower'],  # ACM3
                id="bimanual_follower"
            )
            
            # FIX: Use separate unused port to avoid EOF error
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],     # ACM0 (left leader)
                right_arm_port=ports['right_leader'],   # ACM1 (but ignore right input)
                id="coordinated_leader"
            )
            
            # Connect (same proven logic)
            self.robot = BiSO100Follower(robot_config)
            self.robot.connect()
            
            self.teleop = BiSO100Leader(teleop_config)
            self.teleop.connect()
            
            # Show control interface
            self.root.after(0, lambda: self.show_control_interface("COORDINATED"))
            
            # Start control loop (same proven pattern)
            self.teleoperation_active = True
            loop_count = 0
            start_time = time.time()
            
            while self.teleoperation_active:
                # Same proven control logic
                action = self.teleop.get_action()
                self.robot.send_action(action)
                
                # Update status
                loop_count += 1
                if loop_count % 200 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed if elapsed > 0 else 0
                    status_text = f"🎮 COORDINATED Active | {rate:.1f} Hz | Loops: {loop_count}"
                    self.root.after(0, lambda t=status_text: self.show_status(t, '#27ae60'))
                
        except Exception as e:
            error_msg = f"❌ Control error: {str(e)}"
            self.root.after(0, lambda: self.show_status(error_msg, '#e74c3c'))
        finally:
            self.cleanup_robots()
    
    def run_mirror_control(self):
        """Run MIRROR control - Same as COORDINATED (LEFT leader mirrors to both)"""
        try:
            # Get ports using API (same as others)
            status = self.api.get_system_status()
            ports = status['hardware']['mapping']
            
            self.root.after(0, lambda: self.show_status("🤖 Connecting robots...", '#f39c12'))
            
            # MIRROR config: Fix port duplication to avoid EOF error
            robot_config = BiSO100FollowerConfig(
                left_arm_port=ports['left_follower'],    # ACM2
                right_arm_port=ports['right_follower'],  # ACM3
                id="bimanual_follower"
            )
            
            # FIX: Use separate ports to avoid EOF error (same as COORDINATED fix)
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=ports['left_leader'],     # ACM0 (left leader - main control)
                right_arm_port=ports['right_leader'],   # ACM1 (but ignore right input)
                id="mirror_leader"
            )
            
            # Connect (same proven logic)
            self.robot = BiSO100Follower(robot_config)
            self.robot.connect()
            
            self.teleop = BiSO100Leader(teleop_config)
            self.teleop.connect()
            
            # Show control interface
            self.root.after(0, lambda: self.show_control_interface("MIRROR"))
            
            # Start control loop (same proven pattern)
            self.teleoperation_active = True
            loop_count = 0
            start_time = time.time()
            
            while self.teleoperation_active:
                # Same proven control logic
                action = self.teleop.get_action()
                self.robot.send_action(action)
                
                # Update status
                loop_count += 1
                if loop_count % 200 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed if elapsed > 0 else 0
                    status_text = f"🎮 MIRROR Active | {rate:.1f} Hz | Loops: {loop_count}"
                    self.root.after(0, lambda t=status_text: self.show_status(t, '#9b59b6'))
                
        except Exception as e:
            error_msg = f"❌ Control error: {str(e)}"
            self.root.after(0, lambda: self.show_status(error_msg, '#e74c3c'))
        finally:
            self.cleanup_robots()
    
    def show_control_interface(self, mode="INDEPENDENT"):
        """Show control interface for any mode"""
        # Clear buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Mode-specific status and info
        mode_config = {
            'COORDINATED': {
                'status': '🎮 COORDINATED MODE ACTIVE!\nMove LEFT leader arm',
                'color': '#27ae60',
                'info': 'Left Leader (ACM0) → BOTH Followers (ACM2+ACM3)'
            },
            'INDEPENDENT': {
                'status': '🎮 INDEPENDENT MODE ACTIVE!\nMove BOTH leader arms',
                'color': '#3498db',
                'info': 'Left Leader (ACM0) → Left Follower (ACM2)\nRight Leader (ACM1) → Right Follower (ACM3)'
            },
            'MIRROR': {
                'status': '🎮 MIRROR MODE ACTIVE!\nMove LEFT leader arm',
                'color': '#9b59b6',
                'info': 'Left Leader (ACM0) → Mirrors to BOTH Followers'
            }
        }
        
        config = mode_config.get(mode, mode_config['INDEPENDENT'])
        self.show_status(config['status'], config['color'])
        
        # Stop button
        stop_btn = tk.Button(
            self.button_frame,
            text="⏹️ STOP CONTROL",
            font=('Arial', 20, 'bold'),
            bg='#e74c3c',
            fg='white',
            relief='flat',
            pady=20,
            command=self.stop_control
        )
        stop_btn.pack(pady=30, padx=50, fill='x')
        
        # Mode-specific info
        info = tk.Label(
            self.button_frame,
            text=config['info'],
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        info.pack(pady=20)
    
    def stop_control(self):
        """Stop control"""
        self.teleoperation_active = False
        self.show_status("⏹️ Stopping...", '#f39c12')
        
        # Return to menu after delay
        self.root.after(2000, self.return_to_menu)
    
    def return_to_menu(self):
        """Return to main menu"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        self.show_ready_ui()
    
    def start_single_arm_mode(self):
        """Start single arm mode (placeholder)"""
        self.show_status("🤖 Single arm mode coming soon!", '#95a5a6')
        
    def start_tri_manual_mode(self):
        """Start tri-manual mode (placeholder)"""
        self.show_status("🔺 Tri-manual mode coming soon!", '#95a5a6')
        
    def start_quad_manual_mode(self):
        """Start quad-manual mode (placeholder)"""
        self.show_status("🔲 Quad-manual mode coming soon!", '#95a5a6')
    
    def cleanup_robots(self):
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
    
    def show_status(self, text, color):
        """Update status display"""
        self.status_label.config(text=text, fg=color)
    
    def exit_app(self):
        """Exit application"""
        self.teleoperation_active = False
        self.cleanup_robots()
        self.root.quit()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = WorkingTouchUI()
    app.run()