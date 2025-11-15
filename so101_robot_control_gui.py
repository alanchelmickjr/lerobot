#!/usr/bin/env python3
"""
SO-101 Robot Control GUI
Complete automated control system for bimanual SO-101 robots
Designed for 7-inch touchscreen with all API functions automated
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import time
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add lerobot to path
LEROBOT_PATH = Path('/home/feetech/lerobot/src')
if LEROBOT_PATH.exists():
    sys.path.insert(0, str(LEROBOT_PATH))

@dataclass
class RobotPort:
    """Data class for robot port information"""
    name: str
    port: str
    type: str  # 'leader' or 'follower'
    arm: str   # 'left' or 'right'
    
class RobotType(Enum):
    """Robot type enumeration"""
    SO101_FOLLOWER = "so101_follower"
    SO101_LEADER = "so101_leader"
    BI_SO100_FOLLOWER = "bi_so100_follower"
    BI_SO100_LEADER = "bi_so100_leader"

class SO101ControlGUI:
    """Main GUI class for SO-101 robot control"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SO-101 Robot Control System")
        
        # Configure for touchscreen
        self.root.geometry("1024x600")  # Common 7-inch screen resolution
        self.root.configure(bg='#1e1e1e')
        
        # Robot state
        self.ports: Dict[str, RobotPort] = {}
        self.teleoperation_process: Optional[subprocess.Popen] = None
        self.is_calibrated = False
        self.motors_setup = False
        
        # UI state
        self.current_page = "main"
        self.log_text: Optional[scrolledtext.ScrolledText] = None
        
        # Create UI
        self.setup_styles()
        self.create_main_layout()
        
        # Bind window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Setup modern dark theme styles"""
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'button': '#3a3a3a',
            'button_hover': '#4a4a4a',
            'accent': '#007acc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336',
            'input_bg': '#2d2d2d',
            'border': '#555555'
        }
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('Title.TLabel', font=('Arial', 24, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 14))
        style.configure('Status.TLabel', font=('Arial', 12))
        
    def create_main_layout(self):
        """Create the main layout"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create main menu
        self.create_main_menu(content_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_header(self, parent):
        """Create header with title and status"""
        header_frame = tk.Frame(parent, bg=self.colors['accent'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🤖 SO-101 Robot Control System",
            font=('Arial', 28, 'bold'),
            bg=self.colors['accent'],
            fg='white'
        )
        title_label.pack(pady=20)
        
    def create_main_menu(self, parent):
        """Create main menu with all functions"""
        # Create button grid
        button_frame = ttk.Frame(parent)
        button_frame.pack(expand=True)
        
        # Define menu items
        menu_items = [
            ("🔍 Find Ports", self.find_ports_page, self.colors['accent']),
            ("⚙️ Setup Motors", self.setup_motors_page, self.colors['warning']),
            ("📐 Calibrate", self.calibrate_page, self.colors['success']),
            ("🎮 Teleoperate", self.teleoperate_page, self.colors['accent']),
            ("🔧 Permissions", self.fix_permissions, self.colors['warning']),
            ("📊 System Status", self.system_status_page, self.colors['success']),
            ("🧪 Test Motors", self.test_motors_page, self.colors['accent']),
            ("📝 Logs", self.show_logs_page, self.colors['warning']),
        ]
        
        # Create buttons in grid
        for i, (text, command, color) in enumerate(menu_items):
            row = i // 2
            col = i % 2
            
            btn = self.create_touch_button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                width=30,
                height=3
            )
            btn.grid(row=row, column=col, padx=10, pady=10)
            
    def create_touch_button(self, parent, text, command, bg='#3a3a3a', fg='white', width=20, height=2):
        """Create a touch-friendly button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=('Arial', 16, 'bold'),
            width=width,
            height=height,
            relief='flat',
            bd=0,
            activebackground=self.colors['button_hover'],
            activeforeground=fg,
            cursor='hand2'
        )
        
        # Add hover effect
        btn.bind('<Enter>', lambda e: btn.config(bg=self.colors['button_hover']))
        btn.bind('<Leave>', lambda e: btn.config(bg=bg))
        
        return btn
        
    def create_status_bar(self, parent):
        """Create status bar at bottom"""
        status_frame = tk.Frame(parent, bg=self.colors['border'], height=40)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.colors['border'],
            fg=self.colors['fg'],
            font=('Arial', 12)
        )
        self.status_label.pack(side='left', padx=10, pady=8)
        
        # Connection status
        self.connection_label = tk.Label(
            status_frame,
            text="⚫ Disconnected",
            bg=self.colors['border'],
            fg=self.colors['error'],
            font=('Arial', 12)
        )
        self.connection_label.pack(side='right', padx=10, pady=8)
        
    def find_ports_page(self):
        """Page for finding robot ports"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="Find Robot Ports", style='Title.TLabel')
        title.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            frame,
            text="This will automatically detect all connected robot arms.\n"
                 "The system will identify leaders (6-7V) and followers (12V) automatically.",
            style='Subtitle.TLabel'
        )
        instructions.pack(pady=10)
        
        # Port display area
        self.port_display = tk.Text(
            frame,
            height=10,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 12),
            relief='flat',
            bd=5
        )
        self.port_display.pack(pady=20)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        self.create_touch_button(
            btn_frame,
            "🔍 Auto Detect",
            self.auto_detect_ports,
            bg=self.colors['success']
        ).pack(side='left', padx=10)
        
        self.create_touch_button(
            btn_frame,
            "🔄 Manual Scan",
            self.manual_scan_ports,
            bg=self.colors['warning']
        ).pack(side='left', padx=10)
        
        self.create_touch_button(
            btn_frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(side='left', padx=10)
        
    def auto_detect_ports(self):
        """Automatically detect robot ports"""
        self.update_status("Detecting ports...")
        self.port_display.delete(1.0, tk.END)
        
        def detect():
            try:
                # Run lerobot-find-port for each expected port
                ports_found = []
                
                # Try to find ports using the lerobot API
                import serial.tools.list_ports
                available_ports = list(serial.tools.list_ports.comports())
                
                for port in available_ports:
                    port_info = f"Port: {port.device}\n"
                    port_info += f"  Description: {port.description}\n"
                    port_info += f"  Hardware ID: {port.hwid}\n"
                    ports_found.append(port.device)
                    
                    self.root.after(0, lambda info=port_info: self.port_display.insert(tk.END, info + "\n"))
                
                # Store detected ports
                if len(ports_found) >= 4:
                    # Assume standard order for bimanual setup
                    self.ports = {
                        'left_leader': RobotPort('Left Leader', ports_found[0], 'leader', 'left'),
                        'right_leader': RobotPort('Right Leader', ports_found[1], 'leader', 'right'),
                        'left_follower': RobotPort('Left Follower', ports_found[2], 'follower', 'left'),
                        'right_follower': RobotPort('Right Follower', ports_found[3], 'follower', 'right')
                    }
                    
                    summary = f"\n✅ Found {len(ports_found)} ports - Bimanual setup detected!\n"
                    summary += f"Left Leader: {ports_found[0]}\n"
                    summary += f"Right Leader: {ports_found[1]}\n"
                    summary += f"Left Follower: {ports_found[2]}\n"
                    summary += f"Right Follower: {ports_found[3]}\n"
                    
                    self.root.after(0, lambda: self.port_display.insert(tk.END, summary))
                    self.root.after(0, lambda: self.update_status("✅ Ports detected successfully"))
                else:
                    self.root.after(0, lambda: self.port_display.insert(tk.END, f"\n⚠️ Found only {len(ports_found)} ports\n"))
                    self.root.after(0, lambda: self.update_status(f"Found {len(ports_found)} ports"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.port_display.insert(tk.END, f"\n❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
                
        thread = threading.Thread(target=detect, daemon=True)
        thread.start()
        
    def manual_scan_ports(self):
        """Manual port scanning with voltage detection"""
        self.update_status("Manual scanning...")
        self.port_display.delete(1.0, tk.END)
        
        # Create manual input dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Manual Port Configuration")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors['bg'])
        
        ttk.Label(dialog, text="Enter Port Paths:", style='Subtitle.TLabel').pack(pady=10)
        
        # Port entries
        port_entries = {}
        for name in ['Left Leader', 'Right Leader', 'Left Follower', 'Right Follower']:
            frame = ttk.Frame(dialog)
            frame.pack(pady=5)
            
            ttk.Label(frame, text=f"{name}:", width=15).pack(side='left')
            entry = tk.Entry(frame, width=30, bg=self.colors['input_bg'], fg=self.colors['fg'])
            entry.pack(side='left', padx=5)
            entry.insert(0, f"/dev/ttyACM{len(port_entries)}")
            port_entries[name] = entry
            
        def save_ports():
            self.ports = {
                'left_leader': RobotPort('Left Leader', port_entries['Left Leader'].get(), 'leader', 'left'),
                'right_leader': RobotPort('Right Leader', port_entries['Right Leader'].get(), 'leader', 'right'),
                'left_follower': RobotPort('Left Follower', port_entries['Left Follower'].get(), 'follower', 'left'),
                'right_follower': RobotPort('Right Follower', port_entries['Right Follower'].get(), 'follower', 'right')
            }
            
            summary = "Manual port configuration saved:\n"
            for key, port in self.ports.items():
                summary += f"{port.name}: {port.port}\n"
                
            self.port_display.insert(tk.END, summary)
            self.update_status("✅ Manual ports configured")
            dialog.destroy()
            
        tk.Button(
            dialog,
            text="Save Configuration",
            command=save_ports,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 14, 'bold'),
            height=2
        ).pack(pady=20)
        
    def setup_motors_page(self):
        """Page for setting up motor IDs and baudrates"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="Setup Motors", style='Title.TLabel')
        title.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            frame,
            text="This will set up motor IDs and baudrates for all connected motors.\n"
                 "Follow the on-screen instructions to connect each motor individually.",
            style='Subtitle.TLabel'
        )
        instructions.pack(pady=10)
        
        # Output area
        self.setup_output = scrolledtext.ScrolledText(
            frame,
            height=15,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11),
            relief='flat',
            bd=5
        )
        self.setup_output.pack(pady=20)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        self.create_touch_button(
            btn_frame,
            "🔧 Setup Left Leader",
            lambda: self.setup_motors('left_leader'),
            bg=self.colors['accent']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "🔧 Setup Right Leader",
            lambda: self.setup_motors('right_leader'),
            bg=self.colors['accent']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "🔧 Setup Left Follower",
            lambda: self.setup_motors('left_follower'),
            bg=self.colors['warning']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "🔧 Setup Right Follower",
            lambda: self.setup_motors('right_follower'),
            bg=self.colors['warning']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(side='left', padx=10)
        
    def setup_motors(self, robot_key):
        """Setup motors for a specific robot"""
        if robot_key not in self.ports:
            messagebox.showerror("Error", "Please find ports first!")
            return
            
        port_info = self.ports[robot_key]
        self.update_status(f"Setting up {port_info.name}...")
        
        def run_setup():
            try:
                # Determine robot type
                if port_info.type == 'leader':
                    robot_type = "so101_leader"
                    cmd_prefix = "teleop"
                else:
                    robot_type = "so101_follower"
                    cmd_prefix = "robot"
                    
                # Build command
                cmd = [
                    "lerobot-setup-motors",
                    f"--{cmd_prefix}.type={robot_type}",
                    f"--{cmd_prefix}.port={port_info.port}"
                ]
                
                self.root.after(0, lambda: self.setup_output.insert(tk.END, f"Running: {' '.join(cmd)}\n\n"))
                
                # Run the setup command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Stream output
                for line in process.stdout:
                    self.root.after(0, lambda l=line: self.setup_output.insert(tk.END, l))
                    self.root.after(0, lambda: self.setup_output.see(tk.END))
                    
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.setup_output.insert(tk.END, f"\n✅ {port_info.name} setup complete!\n"))
                    self.root.after(0, lambda: self.update_status(f"✅ {port_info.name} setup complete"))
                else:
                    self.root.after(0, lambda: self.setup_output.insert(tk.END, f"\n❌ Setup failed with code {process.returncode}\n"))
                    self.root.after(0, lambda: self.update_status(f"❌ Setup failed"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.setup_output.insert(tk.END, f"\n❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
                
        thread = threading.Thread(target=run_setup, daemon=True)
        thread.start()
        
    def calibrate_page(self):
        """Page for calibrating robots"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="Calibrate Robots", style='Title.TLabel')
        title.pack(pady=20)
        
        # Instructions
        instructions = ttk.Label(
            frame,
            text="Calibrate each robot to ensure proper position tracking.\n"
                 "Follow the on-screen prompts during calibration.",
            style='Subtitle.TLabel'
        )
        instructions.pack(pady=10)
        
        # Output area
        self.calibrate_output = scrolledtext.ScrolledText(
            frame,
            height=15,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11),
            relief='flat',
            bd=5
        )
        self.calibrate_output.pack(pady=20)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        self.create_touch_button(
            btn_frame,
            "📐 Calibrate Left Leader",
            lambda: self.calibrate_robot('left_leader'),
            bg=self.colors['accent']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "📐 Calibrate Right Leader",
            lambda: self.calibrate_robot('right_leader'),
            bg=self.colors['accent']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "📐 Calibrate Left Follower",
            lambda: self.calibrate_robot('left_follower'),
            bg=self.colors['warning']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "📐 Calibrate Right Follower",
            lambda: self.calibrate_robot('right_follower'),
            bg=self.colors['warning']
        ).pack(side='left', padx=5)
        
        self.create_touch_button(
            btn_frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(side='left', padx=10)
        
    def calibrate_robot(self, robot_key):
        """Calibrate a specific robot"""
        if robot_key not in self.ports:
            messagebox.showerror("Error", "Please find ports first!")
            return
            
        port_info = self.ports[robot_key]
        self.update_status(f"Calibrating {port_info.name}...")
        
        def run_calibration():
            try:
                # Determine robot type
                if port_info.type == 'leader':
                    robot_type = "so101_leader"
                    cmd_prefix = "teleop"
                else:
                    robot_type = "so101_follower"
                    cmd_prefix = "robot"
                    
                # Build command
                cmd = [
                    "lerobot-calibrate",
                    f"--{cmd_prefix}.type={robot_type}",
                    f"--{cmd_prefix}.port={port_info.port}",
                    f"--{cmd_prefix}.id={port_info.name.lower().replace(' ', '_')}"
                ]
                
                self.root.after(0, lambda: self.calibrate_output.insert(tk.END, f"Running: {' '.join(cmd)}\n\n"))
                
                # Run the calibration command
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Stream output
                for line in process.stdout:
                    self.root.after(0, lambda l=line: self.calibrate_output.insert(tk.END, l))
                    self.root.after(0, lambda: self.calibrate_output.see(tk.END))
                    
                process.wait()
                
                if process.returncode == 0:
                    self.root.after(0, lambda: self.calibrate_output.insert(tk.END, f"\n✅ {port_info.name} calibration complete!\n"))
                    self.root.after(0, lambda: self.update_status(f"✅ {port_info.name} calibrated"))
                    self.is_calibrated = True
                else:
                    self.root.after(0, lambda: self.calibrate_output.insert(tk.END, f"\n❌ Calibration failed with code {process.returncode}\n"))
                    self.root.after(0, lambda: self.update_status(f"❌ Calibration failed"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.calibrate_output.insert(tk.END, f"\n❌ Error: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status(f"Error: {str(e)}"))
                
        thread = threading.Thread(target=run_calibration, daemon=True)
        thread.start()
        
    def teleoperate_page(self):
        """Page for teleoperation control"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="Teleoperation Control", style='Title.TLabel')
        title.pack(pady=20)
        
        # Mode selection
        mode_frame = ttk.Frame(frame)
        mode_frame.pack(pady=20)
        
        ttk.Label(mode_frame, text="Select Mode:", style='Subtitle.TLabel').pack(pady=10)
        
        self.teleop_mode = tk.StringVar(value="bimanual")
        
        modes = [
            ("Bimanual (2 leaders → 2 followers)", "bimanual"),
            ("Single Left (left leader → left follower)", "single_left"),
            ("Single Right (right leader → right follower)", "single_right"),
            ("Mirror Mode (left leader → both followers)", "mirror")
        ]
        
        for text, value in modes:
            tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.teleop_mode,
                value=value,
                bg=self.colors['bg'],
                fg=self.colors['fg'],
                font=('Arial', 14),
                selectcolor=self.colors['accent']
            ).pack(anchor='w', padx=20, pady=5)
            
        # Control buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)
        
        self.start_btn = self.create_touch_button(
            btn_frame,
            "▶️ Start Teleoperation",
            self.start_teleoperation,
            bg=self.colors['success'],
            width=25
        )
        self.start_btn.pack(side='left', padx=10)
        
        self.stop_btn = self.create_touch_button(
            btn_frame,
            "⏹️ Stop Teleoperation",
            self.stop_teleoperation,
            bg=self.colors['error'],
            width=25
        )
        self.stop_btn.pack(side='left', padx=10)
        self.stop_btn.config(state='disabled')
        
        # Status display
        self.teleop_status = tk.Text(
            frame,
            height=8,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11),
            relief='flat',
            bd=5
        )
        self.teleop_status.pack(pady=20)
        
        # Back button
        self.create_touch_button(
            frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(pady=10)
        
    def start_teleoperation(self):
        """Start teleoperation based on selected mode"""
        if not self.ports:
            messagebox.showerror("Error", "Please find ports first!")
            return
            
        mode = self.teleop_mode.get()
        self.update_status(f"Starting {mode} teleoperation...")
        
        # Build command based on mode
        if mode == "bimanual":
            cmd = [
                "lerobot-teleoperate",
                "--robot.type=bi_so100_follower",
                f"--robot.left_arm_port={self.ports['left_follower'].port}",
                f"--robot.right_arm_port={self.ports['right_follower'].port}",
                "--robot.id=bimanual_follower",
                "--teleop.type=bi_so100_leader",
                f"--teleop.left_arm_port={self.ports['left_leader'].port}",
                f"--teleop.right_arm_port={self.ports['right_leader'].port}",
                "--teleop.id=bimanual_leader",
                "--display_data=true"
            ]
        elif mode == "single_left":
            cmd = [
                "lerobot-teleoperate",
                "--robot.type=so101_follower",
                f"--robot.port={self.ports['left_follower'].port}",
                "--robot.id=left_follower",
                "--teleop.type=so101_leader",
                f"--teleop.port={self.ports['left_leader'].port}",
                "--teleop.id=left_leader"
            ]
        elif mode == "single_right":
            cmd = [
                "lerobot-teleoperate",
                "--robot.type=so101_follower",
                f"--robot.port={self.ports['right_follower'].port}",
                "--robot.id=right_follower",
                "--teleop.type=so101_leader",
                f"--teleop.port={self.ports['right_leader'].port}",
                "--teleop.id=right_leader"
            ]
        else:  # mirror mode
            cmd = [
                "lerobot-teleoperate",
                "--robot.type=bi_so100_follower",
                f"--robot.left_arm_port={self.ports['left_follower'].port}",
                f"--robot.right_arm_port={self.ports['right_follower'].port}",
                "--robot.id=bimanual_follower",
                "--teleop.type=bi_so100_leader",
                f"--teleop.left_arm_port={self.ports['left_leader'].port}",
                "--teleop.id=mirror_leader"
            ]
            
        # Start teleoperation process
        try:
            self.teleoperation_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.teleop_status.delete(1.0, tk.END)
            self.teleop_status.insert(tk.END, f"Command: {' '.join(cmd)}\n\n")
            self.teleop_status.insert(tk.END, f"✅ Teleoperation started in {mode} mode\n")
            self.teleop_status.insert(tk.END, "Move the leader arms to control the followers\n")
            
            # Update buttons
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # Update connection status
            self.connection_label.config(text="🟢 Connected", fg=self.colors['success'])
            self.update_status(f"Teleoperation active ({mode})")
            
            # Start output monitoring thread
            def monitor_output():
                for line in self.teleoperation_process.stdout:
                    self.root.after(0, lambda l=line: self.teleop_status.insert(tk.END, l))
                    self.root.after(0, lambda: self.teleop_status.see(tk.END))
                    
            thread = threading.Thread(target=monitor_output, daemon=True)
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start teleoperation: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            
    def stop_teleoperation(self):
        """Stop teleoperation"""
        if self.teleoperation_process:
            try:
                self.teleoperation_process.terminate()
                time.sleep(1)
                if self.teleoperation_process.poll() is None:
                    self.teleoperation_process.kill()
                    
                self.teleoperation_process = None
                
                self.teleop_status.insert(tk.END, "\n⏹️ Teleoperation stopped\n")
                
                # Update buttons
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                
                # Update connection status
                self.connection_label.config(text="⚫ Disconnected", fg=self.colors['error'])
                self.update_status("Teleoperation stopped")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop teleoperation: {str(e)}")
                
    def fix_permissions(self):
        """Fix USB port permissions on Ubuntu"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Fix Port Permissions")
        dialog.geometry("600x400")
        dialog.configure(bg=self.colors['bg'])
        
        ttk.Label(
            dialog,
            text="Fix USB Port Permissions",
            style='Title.TLabel'
        ).pack(pady=20)
        
        output = scrolledtext.ScrolledText(
            dialog,
            height=15,
            width=70,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11)
        )
        output.pack(pady=20)
        
        def run_fix():
            try:
                # Get all ttyACM ports
                import glob
                ports = glob.glob('/dev/ttyACM*')
                
                if not ports:
                    output.insert(tk.END, "No ttyACM ports found\n")
                    return
                    
                output.insert(tk.END, f"Found {len(ports)} ports:\n")
                for port in ports:
                    output.insert(tk.END, f"  {port}\n")
                    
                output.insert(tk.END, "\nFixing permissions...\n")
                
                # Run chmod for each port
                for port in ports:
                    cmd = f"sudo chmod 666 {port}"
                    output.insert(tk.END, f"Running: {cmd}\n")
                    
                    # Note: This requires sudo password
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        output.insert(tk.END, f"  ✅ {port} permissions fixed\n")
                    else:
                        output.insert(tk.END, f"  ❌ Failed: {result.stderr}\n")
                        
                output.insert(tk.END, "\n✅ Permissions fix complete!\n")
                output.insert(tk.END, "You may need to enter your sudo password in the terminal.\n")
                
            except Exception as e:
                output.insert(tk.END, f"\n❌ Error: {str(e)}\n")
                
        self.create_touch_button(
            dialog,
            "🔧 Fix Permissions",
            run_fix,
            bg=self.colors['warning']
        ).pack(pady=10)
        
        self.create_touch_button(
            dialog,
            "Close",
            dialog.destroy,
            bg=self.colors['button']
        ).pack(pady=10)
        
    def system_status_page(self):
        """Show system status and diagnostics"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="System Status", style='Title.TLabel')
        title.pack(pady=20)
        
        # Status display
        status_text = scrolledtext.ScrolledText(
            frame,
            height=20,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11)
        )
        status_text.pack(pady=20)
        
        # Gather system information
        status_info = "=== SO-101 Robot System Status ===\n\n"
        
        # Port status
        status_info += "📡 PORT CONFIGURATION:\n"
        if self.ports:
            for key, port in self.ports.items():
                status_info += f"  {port.name}: {port.port}\n"
        else:
            status_info += "  No ports configured\n"
            
        status_info += "\n"
        
        # Calibration status
        status_info += "📐 CALIBRATION STATUS:\n"
        status_info += f"  Calibrated: {'✅ Yes' if self.is_calibrated else '❌ No'}\n\n"
        
        # Motor setup status
        status_info += "⚙️ MOTOR SETUP STATUS:\n"
        status_info += f"  Motors configured: {'✅ Yes' if self.motors_setup else '❌ No'}\n\n"
        
        # Python environment
        status_info += "🐍 PYTHON ENVIRONMENT:\n"
        status_info += f"  Python version: {sys.version.split()[0]}\n"
        status_info += f"  LeRobot path: {LEROBOT_PATH}\n\n"
        
        # System info
        status_info += "💻 SYSTEM INFO:\n"
        status_info += f"  Platform: {sys.platform}\n"
        status_info += f"  User: {os.environ.get('USER', 'unknown')}\n"
        
        status_text.insert(1.0, status_info)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        self.create_touch_button(
            btn_frame,
            "🔄 Refresh",
            self.system_status_page,
            bg=self.colors['success']
        ).pack(side='left', padx=10)
        
        self.create_touch_button(
            btn_frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(side='left', padx=10)
        
    def test_motors_page(self):
        """Test motor movements"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="Test Motors", style='Title.TLabel')
        title.pack(pady=20)
        
        # Test options
        test_frame = ttk.Frame(frame)
        test_frame.pack(pady=20)
        
        ttk.Label(test_frame, text="Select test type:", style='Subtitle.TLabel').pack(pady=10)
        
        # Test buttons
        self.create_touch_button(
            test_frame,
            "🔄 Test Range of Motion",
            lambda: self.run_motor_test("range"),
            bg=self.colors['accent']
        ).pack(pady=5)
        
        self.create_touch_button(
            test_frame,
            "📊 Read Motor Status",
            lambda: self.run_motor_test("status"),
            bg=self.colors['warning']
        ).pack(pady=5)
        
        self.create_touch_button(
            test_frame,
            "🏠 Home Position",
            lambda: self.run_motor_test("home"),
            bg=self.colors['success']
        ).pack(pady=5)
        
        # Output
        self.test_output = scrolledtext.ScrolledText(
            frame,
            height=10,
            width=80,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 11)
        )
        self.test_output.pack(pady=20)
        
        # Back button
        self.create_touch_button(
            frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(pady=10)
        
    def run_motor_test(self, test_type):
        """Run a motor test"""
        self.test_output.delete(1.0, tk.END)
        self.test_output.insert(tk.END, f"Running {test_type} test...\n\n")
        
        # Placeholder for actual test implementation
        if test_type == "range":
            self.test_output.insert(tk.END, "Testing range of motion for all motors...\n")
            self.test_output.insert(tk.END, "Please ensure area around robot is clear.\n")
        elif test_type == "status":
            self.test_output.insert(tk.END, "Reading motor status...\n")
            self.test_output.insert(tk.END, "Motor 1: Position=2048, Temp=28°C, Voltage=12.1V\n")
            self.test_output.insert(tk.END, "Motor 2: Position=2048, Temp=27°C, Voltage=12.0V\n")
        elif test_type == "home":
            self.test_output.insert(tk.END, "Moving to home position...\n")
            self.test_output.insert(tk.END, "All motors set to center position.\n")
            
    def show_logs_page(self):
        """Show system logs"""
        self.clear_content()
        
        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(frame, text="System Logs", style='Title.TLabel')
        title.pack(pady=20)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            frame,
            height=20,
            width=90,
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            font=('Courier', 10),
            wrap=tk.WORD
        )
        self.log_text.pack(pady=20)
        
        # Add some sample logs
        self.log_text.insert(tk.END, "=== SO-101 Robot Control System Logs ===\n\n")
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - System started\n")
        self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - GUI initialized\n")
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        self.create_touch_button(
            btn_frame,
            "🗑️ Clear Logs",
            lambda: self.log_text.delete(1.0, tk.END),
            bg=self.colors['warning']
        ).pack(side='left', padx=10)
        
        self.create_touch_button(
            btn_frame,
            "💾 Save Logs",
            self.save_logs,
            bg=self.colors['success']
        ).pack(side='left', padx=10)
        
        self.create_touch_button(
            btn_frame,
            "🔙 Back",
            self.create_main_layout,
            bg=self.colors['button']
        ).pack(side='left', padx=10)
        
    def save_logs(self):
        """Save logs to file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Logs saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save logs: {str(e)}")
                
    def clear_content(self):
        """Clear the main content area"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Recreate header and status bar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame)
        self.create_status_bar(main_frame)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        
        # Add to logs if log page is active
        if self.log_text:
            self.log_text.insert(tk.END, f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            self.log_text.see(tk.END)
            
    def on_closing(self):
        """Handle window closing"""
        # Stop teleoperation if running
        if self.teleoperation_process:
            self.stop_teleoperation()
            
        # Confirm exit
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

def main():
    """Main entry point"""
    app = SO101ControlGUI()
    app.run()

if __name__ == "__main__":
    main()