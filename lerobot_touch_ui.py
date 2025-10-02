#!/usr/bin/env python3
"""
🤖 LeRobot Touch UI - Optimized for 7" touchscreens!
Perfect for Coofun Mini-PC setups - No keyboard/mouse needed!
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
from typing import Optional, Dict
import serial.tools.list_ports

# Try to import LeRobot components - Focus on SO101 bi-manual
try:
    from lerobot.robots.so101_follower import SO101FollowerConfig, SO101Follower
    from lerobot.teleoperators.so101_leader import SO101LeaderConfig, SO101Leader
    # Use SO101 for bi-manual (adapt SO100 classes to SO101)
    from lerobot.robots.bi_so100_follower import BiSO100FollowerConfig, BiSO100Follower
    from lerobot.teleoperators.bi_so100_leader import BiSO100LeaderConfig, BiSO100Leader
    from lerobot.motors.feetech import FeetechMotorsBus
except ImportError as e:
    print(f"❌ LeRobot SO101 components missing: {e}")
    sys.exit(1)

class TouchUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        
        # Robot state
        self.current_robot = None
        self.current_teleop = None
        self.teleoperation_active = False
        
        # Create main interface
        self.create_main_screen()
        
    def setup_window(self):
        """Setup window for 7-inch touchscreen (800x480 typical)"""
        self.root.title("🤖🤖 LeRobot Bi-Manual Control")
        self.root.geometry("800x480")
        self.root.configure(bg='#2c3e50')
        
        # Optimize for touch - start fullscreen for kiosk mode
        self.root.attributes('-fullscreen', True)
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)
        
        # Touch-friendly settings
        self.root.configure(cursor="none")  # Hide cursor for touch-only use
        
    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        
    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)
        
    def setup_styles(self):
        """Setup touch-friendly styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Large button style for touch - optimized for 7" screen
        self.style.configure('Touch.TButton',
                           font=('Arial', 16, 'bold'),
                           padding=(25, 20))
        
        # Huge button for main actions - perfect for touch
        self.style.configure('BigTouch.TButton',
                           font=('Arial', 20, 'bold'),
                           padding=(35, 25))
        
        # Mode button style with colors
        self.style.configure('Coordinated.TButton',
                           font=('Arial', 18, 'bold'),
                           padding=(30, 20),
                           background='#27ae60')
        
        self.style.configure('Independent.TButton',
                           font=('Arial', 18, 'bold'),
                           padding=(30, 20),
                           background='#3498db')
        
        self.style.configure('Mirror.TButton',
                           font=('Arial', 18, 'bold'),
                           padding=(30, 20),
                           background='#9b59b6')
        
        # Title style
        self.style.configure('Title.TLabel',
                           font=('Arial', 20, 'bold'),
                           foreground='white',
                           background='#2c3e50')
        
        # Status style
        self.style.configure('Status.TLabel',
                           font=('Arial', 12),
                           foreground='#ecf0f1',
                           background='#2c3e50')
    
    def clear_screen(self):
        """Clear all widgets"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def create_main_screen(self):
        """Create main robot selection screen"""
        self.clear_screen()
        
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=20, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = ttk.Label(title_frame, 
                               text="🤖 LeRobot Touch Control", 
                               style='Title.TLabel')
        title_label.pack(expand=True)
        
        # Auto-detect setup
        setup_type = self.detect_robot_setup()
        
        # Main buttons frame
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(expand=True, fill='both', padx=40, pady=20)
        
        if setup_type == "bimanual":
            self.create_bimanual_buttons(button_frame)
        elif setup_type == "single":
            self.create_single_arm_buttons(button_frame)
        elif setup_type == "lekiwi":
            self.create_lekiwi_buttons(button_frame)
        else:
            self.create_setup_buttons(button_frame)
    
    def detect_robot_setup(self):
        """Auto-detect connected robot setup"""
        ports = self.find_usb_ports()
        
        # Focus on SO101 bi-manual detection
        if len(ports) == 4:
            # Check if it's bimanual SO101 setup
            bimanual_config = self.detect_bimanual_setup()
            if bimanual_config:
                return "bimanual"
            else:
                return "unknown_4port"
        elif len(ports) == 2:
            return "single"
        elif len(ports) == 1:
            return "single"
        elif len(ports) == 0:
            return "no_robots"
        else:
            return "unknown"
    
    def find_usb_ports(self):
        """Find USB ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            device_lower = port.device.lower()
            if any(pattern in device_lower for pattern in ['usb', 'usbmodem', 'usbserial', 'acm']):
                ports.append(port.device)
        return sorted(ports)
    
    def detect_bimanual_setup(self):
        """Quick bimanual detection"""
        try:
            ports = self.find_usb_ports()
            if len(ports) != 4:
                return None
                
            leaders = []
            followers = []
            
            for port in ports:
                try:
                    bus = FeetechMotorsBus(port=port, motors={})
                    bus.connect()
                    found_ids = bus.scan()
                    
                    if found_ids:
                        voltage = bus.read("Present_Voltage", found_ids[0]) / 10.0
                        if voltage < 8.0:  # Leader arm (low voltage)
                            leaders.append(port)
                        elif voltage > 10.0:  # Follower arm (12V)
                            followers.append(port)
                    bus.disconnect()
                except Exception:
                    # Ignore connection errors during detection
                    pass
            
            if len(leaders) == 2 and len(followers) == 2:
                return {
                    "left_leader": leaders[0], "left_follower": followers[0],
                    "right_leader": leaders[1], "right_follower": followers[1]
                }
        except:
            pass
        return None
    
    def create_bimanual_buttons(self, parent):
        """Create bimanual control buttons"""
        # Status
        status_label = ttk.Label(parent, 
                                text="🎉 Bi-Manual Setup Detected!", 
                                style='Status.TLabel')
        status_label.pack(pady=(0, 20))
        
        # Mode selection buttons (3x2 grid)
        modes_frame = tk.Frame(parent, bg='#2c3e50')
        modes_frame.pack(expand=True, fill='both')
        
        # Row 1: Beautiful mode buttons with colors
        coord_btn = ttk.Button(modes_frame, text="🤝 COORDINATED\nJoint Control",
                              style='Coordinated.TButton',
                              command=lambda: self.start_bimanual("coordinated"))
        coord_btn.grid(row=0, column=0, padx=8, pady=8, sticky='nsew')
                  
        indep_btn = ttk.Button(modes_frame, text="🆓 INDEPENDENT\nSeparate Control",
                              style='Independent.TButton',
                              command=lambda: self.start_bimanual("independent"))
        indep_btn.grid(row=0, column=1, padx=8, pady=8, sticky='nsew')
                  
        mirror_btn = ttk.Button(modes_frame, text="🪞 MIRROR\nLeft→Both Arms",
                               style='Mirror.TButton',
                               command=lambda: self.start_bimanual("mirror"))
        mirror_btn.grid(row=0, column=2, padx=8, pady=8, sticky='nsew')
        
        # Row 2: Utility buttons
        ttk.Button(modes_frame, text="🔧 CALIBRATE\nBoth Arms", 
                  style='Touch.TButton',
                  command=self.calibrate_bimanual).grid(
                  row=1, column=0, padx=10, pady=10, sticky='nsew')
                  
        ttk.Button(modes_frame, text="🔍 DIAGNOSTICS\nCheck Motors", 
                  style='Touch.TButton',
                  command=self.run_diagnostics).grid(
                  row=1, column=1, padx=10, pady=10, sticky='nsew')
                  
        ttk.Button(modes_frame, text="⚙️ SETTINGS\nConfiguration", 
                  style='Touch.TButton',
                  command=self.show_settings).grid(
                  row=1, column=2, padx=10, pady=10, sticky='nsew')
        
        # Configure grid weights
        for i in range(3):
            modes_frame.columnconfigure(i, weight=1)
        for i in range(2):
            modes_frame.rowconfigure(i, weight=1)
    
    def create_single_arm_buttons(self, parent):
        """Create single arm control buttons"""
        status_label = ttk.Label(parent, 
                                text="🤖 Single Arm Setup", 
                                style='Status.TLabel')
        status_label.pack(pady=(0, 20))
        
        # Single arm buttons
        ttk.Button(parent, text="🚀 QUICK START\nAuto Setup & Go", 
                  style='BigTouch.TButton',
                  command=self.quick_start_single).pack(pady=15, fill='x')
                  
        ttk.Button(parent, text="🔧 CALIBRATE ARM\nSetup Motors", 
                  style='Touch.TButton',
                  command=self.calibrate_single).pack(pady=10, fill='x')
                  
        ttk.Button(parent, text="🎮 TELEOPERATION\nStart Control", 
                  style='Touch.TButton',
                  command=self.start_single_teleop).pack(pady=10, fill='x')
    
    def create_lekiwi_buttons(self, parent):
        """Create LeKiwi control buttons"""
        status_label = ttk.Label(parent, 
                                text="📱 LeKiwi Robot Detected", 
                                style='Status.TLabel')
        status_label.pack(pady=(0, 20))
        
        ttk.Button(parent, text="🏠 HOST MODE\nDirect Control", 
                  style='BigTouch.TButton',
                  command=self.start_lekiwi_host).pack(pady=15, fill='x')
                  
        ttk.Button(parent, text="📱 CLIENT MODE\nRemote Control", 
                  style='Touch.TButton',
                  command=self.start_lekiwi_client).pack(pady=10, fill='x')
    
    def create_setup_buttons(self, parent):
        """Create setup/detection buttons"""
        status_label = ttk.Label(parent, 
                                text="🔍 Auto-Detecting Setup...", 
                                style='Status.TLabel')
        status_label.pack(pady=(0, 20))
        
        ttk.Button(parent, text="🔄 REFRESH\nScan Again", 
                  style='BigTouch.TButton',
                  command=self.create_main_screen).pack(pady=15, fill='x')
                  
        ttk.Button(parent, text="🔧 MANUAL SETUP\nChoose Robot Type", 
                  style='Touch.TButton',
                  command=self.manual_setup).pack(pady=10, fill='x')
    
    def start_bimanual(self, mode):
        """Start bimanual teleoperation"""
        self.show_loading(f"Starting {mode.upper()} mode...")
        
        # Setup bimanual in background
        threading.Thread(target=self._start_bimanual_thread, 
                        args=(mode,), daemon=True).start()
    
    def _start_bimanual_thread(self, mode):
        """Background bimanual setup"""
        try:
            setup = self.detect_bimanual_setup()
            if not setup:
                self.show_error("Could not detect bimanual setup")
                return
            
            # Create configs
            robot_config = BiSO100FollowerConfig(
                left_arm_port=setup['left_follower'],
                right_arm_port=setup['right_follower'],
                id="bimanual_follower"
            )
            
            teleop_config = BiSO100LeaderConfig(
                left_arm_port=setup['left_leader'],
                right_arm_port=setup['right_leader'],
                id="bimanual_leader"
            )
            
            # Connect
            self.current_robot = BiSO100Follower(robot_config)
            self.current_teleop = BiSO100Leader(teleop_config)
            
            self.current_robot.connect()
            self.current_teleop.connect()
            
            # Switch to control screen
            self.root.after(0, lambda: self.show_bimanual_control(mode, setup))
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Failed to start: {e}"))
    
    def show_bimanual_control(self, mode, setup):
        """Show bimanual control interface"""
        self.clear_screen()
        
        # Header with mode and status
        header_frame = tk.Frame(self.root, bg='#27ae60', height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        mode_label = ttk.Label(header_frame,
                              text=f"🤖🤖 BI-MANUAL {mode.upper()} ACTIVE",
                              font=('Arial', 16, 'bold'),
                              foreground='white',
                              background='#27ae60')
        mode_label.pack(expand=True)
        
        # Control info
        info_frame = tk.Frame(self.root, bg='#2c3e50', height=120)
        info_frame.pack(fill='x', padx=20, pady=10)
        
        if mode == "coordinated":
            info_text = "🤝 Arms working together\nMove both leaders for coordination"
        elif mode == "independent":  
            info_text = "🆓 Left leader → Left arm\nRight leader → Right arm"
        else:  # mirror
            info_text = "🪞 Left leader controls BOTH arms\nRight arm mirrors left"
            
        ttk.Label(info_frame, text=info_text, 
                 font=('Arial', 12), 
                 foreground='#ecf0f1',
                 background='#2c3e50').pack(expand=True)
        
        # Status display
        self.status_frame = tk.Frame(self.root, bg='#34495e', height=80)
        self.status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_label = ttk.Label(self.status_frame,
                                     text="Rate: -- Hz | Time: 0s",
                                     font=('Arial', 14),
                                     foreground='#ecf0f1',
                                     background='#34495e')
        self.status_label.pack(expand=True)
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(expand=True, fill='both', padx=40, pady=20)
        
        ttk.Button(control_frame, text="⏸️ PAUSE\nTeleoperation", 
                  style='Touch.TButton',
                  command=self.pause_teleoperation).grid(
                  row=0, column=0, padx=10, pady=10, sticky='nsew')
                  
        ttk.Button(control_frame, text="🔄 CHANGE MODE\nSwitch Control", 
                  style='Touch.TButton',
                  command=self.change_mode).grid(
                  row=0, column=1, padx=10, pady=10, sticky='nsew')
                  
        ttk.Button(control_frame, text="❌ STOP\nReturn to Menu", 
                  style='Touch.TButton',
                  command=self.stop_teleoperation).grid(
                  row=0, column=2, padx=10, pady=10, sticky='nsew')
        
        for i in range(3):
            control_frame.columnconfigure(i, weight=1)
        control_frame.rowconfigure(0, weight=1)
        
        # Start teleoperation thread
        self.teleoperation_active = True
        threading.Thread(target=self._bimanual_teleop_loop, 
                        args=(mode,), daemon=True).start()
    
    def _bimanual_teleop_loop(self, mode):
        """Bimanual teleoperation loop"""
        loop_count = 0
        start_time = time.time()
        
        while self.teleoperation_active:
            try:
                # Get actions
                actions = self.current_teleop.get_action()
                
                # Apply mode logic
                if mode == "mirror":
                    left_actions = {k: v for k, v in actions.items() if k.startswith('left_')}
                    right_actions = {k.replace('left_', 'right_'): v for k, v in left_actions.items()}
                    final_actions = {**left_actions, **right_actions}
                elif mode == "coordinated":
                    # Coordinated mode: LEFT leader controls BOTH followers
                    left_actions = {k: v for k, v in actions.items() if k.startswith('left_')}
                    
                    # Mirror left leader actions to both followers for coordinated movement
                    final_actions = {}
                    
                    # Apply left leader action to both left and right followers
                    for left_key, left_val in left_actions.items():
                        # Send left leader action to left follower
                        final_actions[left_key] = left_val
                        
                        # Mirror left leader action to right follower
                        right_key = left_key.replace('left_', 'right_')
                        final_actions[right_key] = left_val
                else:
                    # Independent mode (default)
                    final_actions = actions
                
                # Send to robot
                self.current_robot.send_action(final_actions)
                
                # Update status
                loop_count += 1
                if loop_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = loop_count / elapsed
                    
                    status_text = f"Rate: {rate:.1f} Hz | Time: {elapsed:.1f}s | Loops: {loop_count}"
                    self.root.after(0, lambda: setattr(self.status_label, 'text', status_text))
                
                time.sleep(0.01)  # ~100Hz
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Teleoperation error: {e}"))
                break
    
    def show_loading(self, message):
        """Show loading screen"""
        self.clear_screen()
        
        loading_frame = tk.Frame(self.root, bg='#2c3e50')
        loading_frame.pack(expand=True, fill='both')
        
        ttk.Label(loading_frame, text="🔄", 
                 font=('Arial', 48), 
                 foreground='#3498db',
                 background='#2c3e50').pack(expand=True)
                 
        ttk.Label(loading_frame, text=message, 
                 font=('Arial', 16), 
                 foreground='#ecf0f1',
                 background='#2c3e50').pack()
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.create_main_screen()
    
    def pause_teleoperation(self):
        """Pause/resume teleoperation"""
        self.teleoperation_active = not self.teleoperation_active
        # Update button text based on state
    
    def change_mode(self):
        """Change coordination mode"""
        # Show mode selection dialog
        pass
    
    def stop_teleoperation(self):
        """Stop teleoperation and return to main menu"""
        self.teleoperation_active = False
        
        if self.current_robot:
            self.current_robot.disconnect()
        if self.current_teleop:
            self.current_teleop.disconnect()
            
        self.create_main_screen()
    
    # Placeholder methods for other functionality
    def calibrate_bimanual(self): pass
    def run_diagnostics(self): pass
    def show_settings(self): pass
    def quick_start_single(self): pass
    def calibrate_single(self): pass
    def start_single_teleop(self): pass
    def start_lekiwi_host(self): pass
    def start_lekiwi_client(self): pass
    def manual_setup(self): pass
    
    def run(self):
        """Start the touch UI"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TouchUI()
    app.run()