"""
UI Manager for the Interactive Terminal Networking Utility
Handles all curses-based user interface operations
"""

import curses
import threading
import time
import datetime
import os
from network_tools import PortScanner, DirectoryBuster, VirtualHostScanner, HostScanner
from config import Config

class NetworkToolsUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.config = Config()
        
        # Initialize curses settings
        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)  # Enable special keys
        stdscr.timeout(100)  # Non-blocking input with 100ms timeout
        
        # Initialize color pairs
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Error
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Warning
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Info
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Highlight
        curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Selected
        
        # UI state
        self.current_menu = "main"
        self.selected_option = 0
        self.max_y, self.max_x = stdscr.getmaxyx()
        
        # Tool instances
        self.port_scanner = PortScanner()
        self.directory_buster = DirectoryBuster()
        self.vhost_scanner = VirtualHostScanner()
        self.host_scanner = HostScanner()
        
        # Results storage
        self.results = []
        self.scan_in_progress = False
        self.scan_thread = None
        
        # Tool settings
        self.tool_settings = {
            'port_scanner': {
                'port_range': '1-1000',
                'threads': self.config.DEFAULT_THREADS,
                'timeout': self.config.PORT_SCAN_TIMEOUT,
                'service_detection': True,
                'host_discovery': True
            },
            'directory_buster': {
                'wordlist': 'wordlists/common_dirs.txt',
                'extensions': 'php,html,txt,js,asp,aspx,jsp',
                'threads': self.config.DIR_SCAN_THREADS,
                'timeout': self.config.DIR_SCAN_TIMEOUT
            },
            'vhost_scanner': {
                'wordlist': 'wordlists/common_vhosts.txt',
                'threads': self.config.VHOST_SCAN_THREADS,
                'timeout': self.config.VHOST_SCAN_TIMEOUT
            },
            'host_scanner': {
                'method': 'ping+tcp',
                'threads': self.config.HOST_SCAN_THREADS,
                'timeout': self.config.HOST_SCAN_TIMEOUT
            }
        }

    def run(self):
        """Main application loop"""
        while True:
            try:
                self.stdscr.clear()
                
                if self.current_menu == "main":
                    self.draw_main_menu()
                elif self.current_menu == "port_scanner":
                    self.draw_port_scanner_menu()
                elif self.current_menu == "directory_buster":
                    self.draw_directory_buster_menu()
                elif self.current_menu == "vhost_scanner":
                    self.draw_vhost_scanner_menu()
                elif self.current_menu == "host_scanner":
                    self.draw_host_scanner_menu()
                elif self.current_menu == "results":
                    self.draw_results_menu()
                
                self.stdscr.refresh()
                
                # Handle input
                key = self.stdscr.getch()
                if key != -1:  # Key was pressed
                    if not self.handle_input(key):
                        break
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.show_error(f"UI Error: {str(e)}")

    def draw_header(self):
        """Draw the application header"""
        title = "Network Security Tools v1.0"
        subtitle = "Interactive Terminal-Based Networking Utility"
        
        # Draw title
        x = (self.max_x - len(title)) // 2
        self.stdscr.addstr(1, x, title, curses.color_pair(5) | curses.A_BOLD)
        
        # Draw subtitle
        x = (self.max_x - len(subtitle)) // 2
        self.stdscr.addstr(2, x, subtitle, curses.color_pair(4))
        
        # Draw separator
        self.stdscr.addstr(4, 2, "=" * (self.max_x - 4), curses.color_pair(4))

    def draw_main_menu(self):
        """Draw the main menu"""
        self.draw_header()
        
        menu_items = [
            "Port Scanner",
            "Directory Buster", 
            "Virtual Host Scanner",
            "Host Scanner",
            "View Results",
            "Exit"
        ]
        
        self.stdscr.addstr(6, 4, "Select a tool:", curses.color_pair(4) | curses.A_BOLD)
        
        for i, item in enumerate(menu_items):
            y = 8 + i
            x = 6
            
            if i == self.selected_option:
                self.stdscr.addstr(y, x, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y, x, f"  {item}", curses.color_pair(4))
        
        # Draw instructions
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "q: Quit"])

    def draw_port_scanner_menu(self):
        """Draw the port scanner interface with inline results"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Port Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Current settings
        settings = self.tool_settings['port_scanner']
        y = 8
        self.stdscr.addstr(y, 4, "Current Settings:", curses.color_pair(4) | curses.A_BOLD)
        y += 1
        self.stdscr.addstr(y, 6, f"Port Range: {settings['port_range']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Threads: {settings['threads']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Timeout: {settings['timeout']}s", curses.color_pair(3))
        y += 1
        service_status = "ON" if settings['service_detection'] else "OFF"
        self.stdscr.addstr(y, 6, f"Service Detection: {service_status}", curses.color_pair(3))
        y += 1
        host_status = "ON" if settings['host_discovery'] else "OFF"
        self.stdscr.addstr(y, 6, f"Host Discovery: {host_status}", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Clear Results", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        # Show scan progress if running
        if self.scan_in_progress:
            self.draw_scan_progress("Port scanning in progress...", y + len(menu_items) + 2)
            y += len(menu_items) + 4
        else:
            y += len(menu_items) + 2
        
        # Show port scanner results inline
        port_results = [r for r in self.results if "Port" in r or "OPEN" in r or "scan" in r.lower()]
        if port_results:
            self.stdscr.addstr(y, 4, "Scan Results:", curses.color_pair(4) | curses.A_BOLD)
            y += 1
            
            # Show last 10 results to fit in window
            for result in port_results[-10:]:
                if y >= self.max_y - 4:
                    break
                
                # Color code results
                if "OPEN" in result:
                    color = curses.color_pair(1)  # Green for open ports
                elif "ERROR" in result or "Failed" in result:
                    color = curses.color_pair(2)  # Red for errors
                else:
                    color = curses.color_pair(4)  # Cyan for info
                
                self.stdscr.addstr(y, 6, result[:self.max_x-8], color)
                y += 1
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "ESC: Stop Scan", "b: Back"])

    def draw_directory_buster_menu(self):
        """Draw the directory buster interface with inline results"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Directory Buster", curses.color_pair(5) | curses.A_BOLD)
        
        # Current settings  
        settings = self.tool_settings['directory_buster']
        y = 8
        self.stdscr.addstr(y, 4, "Current Settings:", curses.color_pair(4) | curses.A_BOLD)
        y += 1
        self.stdscr.addstr(y, 6, f"Wordlist: {settings['wordlist']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Extensions: {settings['extensions']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Threads: {settings['threads']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Timeout: {settings['timeout']}s", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Clear Results", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Directory busting in progress...", y + len(menu_items) + 2)
            y += len(menu_items) + 4
        else:
            y += len(menu_items) + 2
        
        # Show directory buster results inline
        dir_results = [r for r in self.results if "Found:" in r or "directory" in r.lower() or "Status:" in r]
        if dir_results:
            self.stdscr.addstr(y, 4, "Found Directories/Files:", curses.color_pair(4) | curses.A_BOLD)
            y += 1
            
            # Show last 10 results to fit in window
            for result in dir_results[-10:]:
                if y >= self.max_y - 4:
                    break
                
                # Color code results
                if "Status: 200" in result or "Found:" in result:
                    color = curses.color_pair(1)  # Green for found items
                elif "Status: 403" in result or "Status: 401" in result:
                    color = curses.color_pair(3)  # Yellow for restricted
                elif "ERROR" in result:
                    color = curses.color_pair(2)  # Red for errors
                else:
                    color = curses.color_pair(4)  # Cyan for info
                
                self.stdscr.addstr(y, 6, result[:self.max_x-8], color)
                y += 1
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "ESC: Stop Scan", "b: Back"])

    def draw_vhost_scanner_menu(self):
        """Draw the virtual host scanner interface with inline results"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Virtual Host Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Current settings
        settings = self.tool_settings['vhost_scanner']
        y = 8
        self.stdscr.addstr(y, 4, "Current Settings:", curses.color_pair(4) | curses.A_BOLD)
        y += 1
        self.stdscr.addstr(y, 6, f"Wordlist: {settings['wordlist']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Threads: {settings['threads']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Timeout: {settings['timeout']}s", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Clear Results", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Virtual host scanning in progress...", y + len(menu_items) + 2)
            y += len(menu_items) + 4
        else:
            y += len(menu_items) + 2
        
        # Show virtual host results inline
        vhost_results = [r for r in self.results if "virtual host" in r.lower() or "Found:" in r and ("Status:" in r)]
        if vhost_results:
            self.stdscr.addstr(y, 4, "Found Virtual Hosts:", curses.color_pair(4) | curses.A_BOLD)
            y += 1
            
            # Show last 10 results to fit in window
            for result in vhost_results[-10:]:
                if y >= self.max_y - 4:
                    break
                
                # Color code results
                if "Status: 200" in result:
                    color = curses.color_pair(1)  # Green for successful
                elif "Status: 403" in result or "Status: 401" in result:
                    color = curses.color_pair(3)  # Yellow for restricted
                elif "ERROR" in result:
                    color = curses.color_pair(2)  # Red for errors
                else:
                    color = curses.color_pair(4)  # Cyan for info
                
                self.stdscr.addstr(y, 6, result[:self.max_x-8], color)
                y += 1
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "ESC: Stop Scan", "b: Back"])

    def draw_host_scanner_menu(self):
        """Draw the host scanner interface with inline results"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Host Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Current settings
        settings = self.tool_settings['host_scanner']
        y = 8
        self.stdscr.addstr(y, 4, "Current Settings:", curses.color_pair(4) | curses.A_BOLD)
        y += 1
        self.stdscr.addstr(y, 6, f"Scan Method: {settings['method']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Threads: {settings['threads']}", curses.color_pair(3))
        y += 1
        self.stdscr.addstr(y, 6, f"Timeout: {settings['timeout']}s", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Clear Results", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Host discovery in progress...", y + len(menu_items) + 2)
            y += len(menu_items) + 4
        else:
            y += len(menu_items) + 2
        
        # Show host discovery results inline
        host_results = [r for r in self.results if "Host" in r and ("alive" in r or "up" in r.lower()) or "discovery" in r.lower()]
        if host_results:
            self.stdscr.addstr(y, 4, "Discovered Hosts:", curses.color_pair(4) | curses.A_BOLD)
            y += 1
            
            # Show last 15 results to fit in window
            for result in host_results[-15:]:
                if y >= self.max_y - 4:
                    break
                
                # Color code results
                if "alive" in result or "up" in result.lower():
                    color = curses.color_pair(1)  # Green for alive hosts
                elif "ERROR" in result or "Failed" in result:
                    color = curses.color_pair(2)  # Red for errors
                else:
                    color = curses.color_pair(4)  # Cyan for info
                
                self.stdscr.addstr(y, 6, result[:self.max_x-8], color)
                y += 1
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "ESC: Stop Scan", "b: Back"])

    def draw_results_menu(self):
        """Draw the results viewer"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Scan Results", curses.color_pair(5) | curses.A_BOLD)
        
        if not self.results:
            self.stdscr.addstr(8, 4, "No results available.", curses.color_pair(3))
        else:
            y = 8
            for i, result in enumerate(self.results[-20:]):  # Show last 20 results
                if y >= self.max_y - 4:
                    break
                
                # Color code based on result type
                if "OPEN" in result or "Found" in result:
                    color = curses.color_pair(1)  # Green for success
                elif "ERROR" in result or "Failed" in result:
                    color = curses.color_pair(2)  # Red for errors
                else:
                    color = curses.color_pair(4)  # Cyan for info
                
                self.stdscr.addstr(y, 4, result[:self.max_x-6], color)
                y += 1
        
        menu_items = ["Clear Results", "Export Results", "Save Configuration", "Filter Results", "Back to Main Menu"]
        
        y = self.max_y - 7
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "b: Back"])

    def draw_scan_progress(self, message, y):
        """Draw scan progress indicator"""
        self.stdscr.addstr(y, 4, message, curses.color_pair(3) | curses.A_BOLD)
        
        # Simple animated progress indicator
        progress_chars = ["|", "/", "-", "\\"]
        char_index = int(time.time() * 4) % len(progress_chars)
        self.stdscr.addstr(y, 4 + len(message) + 1, progress_chars[char_index], curses.color_pair(3))

    def draw_instructions(self, instructions):
        """Draw instruction bar at the bottom"""
        y = self.max_y - 2
        instruction_text = " | ".join(instructions)
        self.stdscr.addstr(y, 2, instruction_text, curses.color_pair(4))

    def handle_input(self, key):
        """Handle keyboard input"""
        if key == ord('q'):
            return False  # Exit application
        elif key == ord('b') and self.current_menu != "main":
            self.current_menu = "main"
            self.selected_option = 0
        elif key == curses.KEY_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == curses.KEY_DOWN:
            max_options = self.get_max_options()
            self.selected_option = min(max_options - 1, self.selected_option + 1)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.handle_selection()
        elif key == 27:  # ESC key
            if self.scan_in_progress:
                self.stop_scan()
            else:
                self.current_menu = "main"
                self.selected_option = 0
        
        return True

    def get_max_options(self):
        """Get maximum number of options for current menu"""
        if self.current_menu == "main":
            return 6
        elif self.current_menu in ["port_scanner", "directory_buster", "vhost_scanner", "host_scanner"]:
            return 4  # Now includes Clear Results option
        elif self.current_menu == "results":
            return 5
        return 1

    def handle_selection(self):
        """Handle menu selection"""
        if self.current_menu == "main":
            if self.selected_option == 0:
                self.current_menu = "port_scanner"
            elif self.selected_option == 1:
                self.current_menu = "directory_buster"
            elif self.selected_option == 2:
                self.current_menu = "vhost_scanner"
            elif self.selected_option == 3:
                self.current_menu = "host_scanner"
            elif self.selected_option == 4:
                self.current_menu = "results"
            elif self.selected_option == 5:
                return False
            self.selected_option = 0
        
        elif self.current_menu in ["port_scanner", "directory_buster", "vhost_scanner", "host_scanner"]:
            if self.selected_option == 0:  # Start Scan
                self.start_scan()
            elif self.selected_option == 1:  # Configure Settings
                self.configure_tool_settings()
            elif self.selected_option == 2:  # Clear Results
                self.clear_tool_results()
            elif self.selected_option == 3:  # Back
                self.current_menu = "main"
                self.selected_option = 0
        
        elif self.current_menu == "results":
            if self.selected_option == 0:  # Clear Results
                self.results.clear()
                self.show_message("Results cleared")
            elif self.selected_option == 1:  # Export Results
                self.export_results()
            elif self.selected_option == 2:  # Save Configuration
                self.save_configuration()
            elif self.selected_option == 3:  # Filter Results
                filter_term = self.get_user_input("Enter filter term (or leave empty to show all):")
                self.filter_results(filter_term)
            elif self.selected_option == 4:  # Back
                self.current_menu = "main"
                self.selected_option = 0

    def start_scan(self):
        """Start the appropriate scan based on current menu"""
        if self.scan_in_progress:
            self.show_message("Scan already in progress")
            return
        
        self.scan_in_progress = True
        
        if self.current_menu == "port_scanner":
            target = self.get_user_input("Enter target host/IP:")
            if not target:
                self.scan_in_progress = False
                return
            
            port_range = self.get_user_input(f"Port range (default: {self.tool_settings['port_scanner']['port_range']}):")
            if not port_range:
                port_range = self.tool_settings['port_scanner']['port_range']
                
            self.scan_thread = threading.Thread(
                target=self.run_port_scan, 
                args=(target, port_range)
            )
            
        elif self.current_menu == "directory_buster":
            target = self.get_user_input("Enter target URL:")
            if not target:
                self.scan_in_progress = False
                return
                
            wordlist = self.get_user_input(f"Wordlist file (default: {self.tool_settings['directory_buster']['wordlist']}):")
            if not wordlist:
                wordlist = self.tool_settings['directory_buster']['wordlist']
                
            extensions = self.get_user_input(f"Extensions (default: {self.tool_settings['directory_buster']['extensions']}):")
            if not extensions:
                extensions = self.tool_settings['directory_buster']['extensions']
                
            self.scan_thread = threading.Thread(
                target=self.run_directory_scan, 
                args=(target, wordlist, extensions)
            )
            
        elif self.current_menu == "vhost_scanner":
            target_ip = self.get_user_input("Enter target IP:")
            if not target_ip:
                self.scan_in_progress = False
                return
                
            domain = self.get_user_input("Enter domain:")
            if not domain:
                self.scan_in_progress = False
                return
                
            wordlist = self.get_user_input(f"Wordlist file (default: {self.tool_settings['vhost_scanner']['wordlist']}):")
            if not wordlist:
                wordlist = self.tool_settings['vhost_scanner']['wordlist']
                
            self.scan_thread = threading.Thread(
                target=self.run_vhost_scan, 
                args=(target_ip, domain, wordlist)
            )
            
        elif self.current_menu == "host_scanner":
            network = self.get_user_input("Enter network range (CIDR, e.g., 192.168.1.0/24):")
            if not network:
                self.scan_in_progress = False
                return
                
            self.scan_thread = threading.Thread(
                target=self.run_host_scan, 
                args=(network,)
            )
        
        if self.scan_thread:
            self.scan_thread.daemon = True
            self.scan_thread.start()
        else:
            self.scan_in_progress = False

    def run_port_scan(self, target, port_range):
        """Run port scan in separate thread"""
        try:
            self.add_scan_result("PORT", f"Starting port scan on {target} - Range: {port_range}")
            settings = self.tool_settings['port_scanner']
            
            # Configure port scanner with UI settings
            self.port_scanner.timeout = settings['timeout']
            self.port_scanner.service_detection = settings['service_detection']
            self.port_scanner.host_discovery = settings['host_discovery']
            results = self.port_scanner.scan(target, port_range, settings['threads'])
            for result in results:
                self.add_scan_result("PORT", result)
        except Exception as e:
            self.add_scan_result("PORT", f"ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False
            self.add_scan_result("PORT", "Scan completed")

    def run_directory_scan(self, target, wordlist, extensions):
        """Run directory scan in separate thread"""
        try:
            self.add_scan_result("DIR", f"Starting directory scan on {target}")
            ext_list = extensions.split(',') if extensions else None
            results = self.directory_buster.scan(target, wordlist, ext_list)
            for result in results:
                self.add_scan_result("DIR", result)
        except Exception as e:
            self.add_scan_result("DIR", f"ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False
            self.add_scan_result("DIR", "Scan completed")

    def run_vhost_scan(self, target_ip, domain, wordlist):
        """Run virtual host scan in separate thread"""
        try:
            self.add_scan_result("VHOST", f"Starting virtual host scan on {target_ip} for {domain}")
            results = self.vhost_scanner.scan(target_ip, domain, wordlist)
            for result in results:
                self.add_scan_result("VHOST", result)
        except Exception as e:
            self.add_scan_result("VHOST", f"ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False
            self.add_scan_result("VHOST", "Scan completed")

    def run_host_scan(self, target):
        """Run host scan in separate thread"""
        try:
            self.add_scan_result("HOST", f"Starting host discovery on {target}")
            results = self.host_scanner.scan(target)
            for result in results:
                self.add_scan_result("HOST", result)
        except Exception as e:
            self.add_scan_result("HOST", f"ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False
            self.add_scan_result("HOST", "Scan completed")

    def stop_scan(self):
        """Stop current scan"""
        if self.scan_in_progress and self.scan_thread:
            self.scan_in_progress = False
            self.show_message("Scan stopped")

    def get_user_input(self, prompt):
        """Get user input with a proper input dialog"""
        # Save current screen
        curses.curs_set(1)  # Show cursor
        
        # Draw input dialog
        dialog_y = self.max_y // 2 - 3
        dialog_x = 4
        dialog_width = self.max_x - 8
        
        # Clear area and draw dialog box
        for i in range(7):
            self.stdscr.addstr(dialog_y + i, dialog_x, " " * dialog_width, curses.color_pair(6))
        
        # Draw border
        self.stdscr.addstr(dialog_y, dialog_x, "+" + "-" * (dialog_width - 2) + "+", curses.color_pair(4))
        self.stdscr.addstr(dialog_y + 6, dialog_x, "+" + "-" * (dialog_width - 2) + "+", curses.color_pair(4))
        for i in range(1, 6):
            self.stdscr.addstr(dialog_y + i, dialog_x, "|", curses.color_pair(4))
            self.stdscr.addstr(dialog_y + i, dialog_x + dialog_width - 1, "|", curses.color_pair(4))
        
        # Draw prompt
        self.stdscr.addstr(dialog_y + 2, dialog_x + 2, prompt, curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(dialog_y + 4, dialog_x + 2, "Enter value (ESC to cancel): ", curses.color_pair(4))
        
        # Input field
        input_y = dialog_y + 4
        input_x = dialog_x + 28
        input_width = dialog_width - 30
        
        self.stdscr.addstr(input_y, input_x, "[" + " " * (input_width - 2) + "]", curses.color_pair(3))
        self.stdscr.move(input_y, input_x + 1)
        self.stdscr.refresh()
        
        # Get input
        user_input = ""
        while True:
            key = self.stdscr.getch()
            
            if key == 27:  # ESC
                curses.curs_set(0)
                return None
            elif key == 10 or key == 13:  # Enter
                curses.curs_set(0)
                return user_input.strip() if user_input.strip() else None
            elif key == 8 or key == 127 or key == curses.KEY_BACKSPACE:  # Backspace
                if user_input:
                    user_input = user_input[:-1]
                    self.stdscr.addstr(input_y, input_x + 1, user_input + " " * (input_width - len(user_input) - 2), curses.color_pair(3))
                    self.stdscr.move(input_y, input_x + 1 + len(user_input))
            elif 32 <= key <= 126 and len(user_input) < input_width - 3:  # Printable characters
                user_input += chr(key)
                self.stdscr.addstr(input_y, input_x + 1, user_input, curses.color_pair(3))
            
            self.stdscr.refresh()

    def configure_tool_settings(self):
        """Configure settings for the current tool"""
        tool_name = self.current_menu
        if tool_name not in self.tool_settings:
            return
            
        settings = self.tool_settings[tool_name]
        
        if tool_name == "port_scanner":
            new_range = self.get_user_input(f"Port range (current: {settings['port_range']}):")
            if new_range:
                settings['port_range'] = new_range
                
            new_threads = self.get_user_input(f"Thread count (current: {settings['threads']}):")
            if new_threads and new_threads.isdigit():
                settings['threads'] = int(new_threads)
                
            new_timeout = self.get_user_input(f"Timeout seconds (current: {settings['timeout']}):")
            if new_timeout and new_timeout.isdigit():
                settings['timeout'] = int(new_timeout)
                
        elif tool_name == "directory_buster":
            new_wordlist = self.get_user_input(f"Wordlist path (current: {settings['wordlist']}):")
            if new_wordlist:
                settings['wordlist'] = new_wordlist
                
            new_extensions = self.get_user_input(f"Extensions (current: {settings['extensions']}):")
            if new_extensions:
                settings['extensions'] = new_extensions
                
            new_threads = self.get_user_input(f"Thread count (current: {settings['threads']}):")
            if new_threads and new_threads.isdigit():
                settings['threads'] = int(new_threads)
                
        elif tool_name == "vhost_scanner":
            new_wordlist = self.get_user_input(f"Wordlist path (current: {settings['wordlist']}):")
            if new_wordlist:
                settings['wordlist'] = new_wordlist
                
            new_threads = self.get_user_input(f"Thread count (current: {settings['threads']}):")
            if new_threads and new_threads.isdigit():
                settings['threads'] = int(new_threads)
                
        elif tool_name == "host_scanner":
            new_method = self.get_user_input(f"Scan method (current: {settings['method']}):")
            if new_method:
                settings['method'] = new_method
                
            new_threads = self.get_user_input(f"Thread count (current: {settings['threads']}):")
            if new_threads and new_threads.isdigit():
                settings['threads'] = int(new_threads)
                
        self.show_message("Settings updated successfully")

    def show_message(self, message):
        """Show a temporary message"""
        y = self.max_y - 4
        self.stdscr.addstr(y, 4, message, curses.color_pair(3) | curses.A_BOLD)
        self.stdscr.refresh()
        time.sleep(1)

    def show_error(self, error):
        """Show error message"""
        y = self.max_y - 4
        self.stdscr.addstr(y, 4, f"ERROR: {error}", curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.refresh()
        time.sleep(2)

    def export_results(self):
        """Export results to file with timestamp"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scan_results_{timestamp}.txt"
            
            # Create results directory if it doesn't exist
            os.makedirs("results", exist_ok=True)
            filepath = os.path.join("results", filename)
            
            with open(filepath, "w") as f:
                f.write(f"Network Tools Scan Results\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                
                for result in self.results:
                    f.write(result + "\n")
                
                f.write(f"\nTotal results: {len(self.results)}\n")
                
            self.show_message(f"Results exported to {filepath}")
        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")
    
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config_file = "network_tools_config.txt"
            with open(config_file, "w") as f:
                f.write("Network Tools Configuration\n")
                f.write(f"Saved: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 40 + "\n\n")
                
                for tool, settings in self.tool_settings.items():
                    f.write(f"{tool.upper()}:\n")
                    for key, value in settings.items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                    
            self.show_message(f"Configuration saved to {config_file}")
        except Exception as e:
            self.show_error(f"Save failed: {str(e)}")
            
    def add_scan_result(self, result_type, message):
        """Add a scan result with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_result = f"[{timestamp}] [{result_type}] {message}"
        self.results.append(formatted_result)
        
    def filter_results(self, filter_term):
        """Filter results based on search term"""
        if not filter_term:
            self.show_message("Showing all results")
            return
            
        # Store original results
        if not hasattr(self, 'original_results'):
            self.original_results = self.results.copy()
        
        # Filter results
        filtered = [result for result in self.original_results if filter_term.lower() in result.lower()]
        self.results = filtered
        self.show_message(f"Showing {len(filtered)} results containing '{filter_term}'")
        
    def clear_tool_results(self):
        """Clear results for the current tool"""
        tool_keywords = {
            'port_scanner': ['port', 'OPEN', 'scan'],
            'directory_buster': ['Found:', 'directory', 'Status:'],
            'vhost_scanner': ['virtual host', 'Found:', 'Status:'],
            'host_scanner': ['Host', 'alive', 'discovery']
        }
        
        if self.current_menu in tool_keywords:
            keywords = tool_keywords[self.current_menu]
            # Remove results that contain any of the tool's keywords
            self.results = [r for r in self.results if not any(keyword.lower() in r.lower() for keyword in keywords)]
            self.show_message(f"{self.current_menu.replace('_', ' ').title()} results cleared")
