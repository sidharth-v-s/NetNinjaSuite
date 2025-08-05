"""
UI Manager for the Interactive Terminal Networking Utility
Handles all curses-based user interface operations
"""

import curses
import threading
import time
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
        """Draw the port scanner interface"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Port Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Input fields
        y = 8
        self.stdscr.addstr(y, 4, "Target Host/IP:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "[Enter target] ", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Port Range:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "1-1000 (default)", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Threads:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, f"{self.config.DEFAULT_THREADS} (default)", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        # Show scan progress if running
        if self.scan_in_progress:
            self.draw_scan_progress("Port scanning in progress...", y + len(menu_items) + 2)
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "b: Back"])

    def draw_directory_buster_menu(self):
        """Draw the directory buster interface"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Directory Buster", curses.color_pair(5) | curses.A_BOLD)
        
        # Input fields
        y = 8
        self.stdscr.addstr(y, 4, "Target URL:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "[Enter URL] ", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Wordlist:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "common_dirs.txt (default)", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Extensions:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "php,html,txt,js (default)", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Directory busting in progress...", y + len(menu_items) + 2)
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "b: Back"])

    def draw_vhost_scanner_menu(self):
        """Draw the virtual host scanner interface"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Virtual Host Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Input fields
        y = 8
        self.stdscr.addstr(y, 4, "Target IP:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "[Enter IP] ", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Domain:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "[Enter domain] ", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Wordlist:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "common_vhosts.txt (default)", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Virtual host scanning in progress...", y + len(menu_items) + 2)
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "b: Back"])

    def draw_host_scanner_menu(self):
        """Draw the host scanner interface"""
        self.draw_header()
        
        self.stdscr.addstr(6, 4, "Host Scanner", curses.color_pair(5) | curses.A_BOLD)
        
        # Input fields
        y = 8
        self.stdscr.addstr(y, 4, "Network Range:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "[Enter CIDR] ", curses.color_pair(3))
        
        y += 2
        self.stdscr.addstr(y, 4, "Scan Type:", curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 6, "Ping + ARP (default)", curses.color_pair(3))
        
        # Menu options
        menu_items = ["Start Scan", "Configure Settings", "Back to Main Menu"]
        
        y += 3
        for i, item in enumerate(menu_items):
            if i == self.selected_option:
                self.stdscr.addstr(y + i, 4, f"→ {item}", curses.color_pair(6) | curses.A_BOLD)
            else:
                self.stdscr.addstr(y + i, 4, f"  {item}", curses.color_pair(4))
        
        if self.scan_in_progress:
            self.draw_scan_progress("Host discovery in progress...", y + len(menu_items) + 2)
        
        self.draw_instructions(["↑↓: Navigate", "Enter: Select", "b: Back"])

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
        
        menu_items = ["Clear Results", "Export Results", "Back to Main Menu"]
        
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
            return 3
        elif self.current_menu == "results":
            return 3
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
                self.show_message("Configuration not implemented in this demo")
            elif self.selected_option == 2:  # Back
                self.current_menu = "main"
                self.selected_option = 0
        
        elif self.current_menu == "results":
            if self.selected_option == 0:  # Clear Results
                self.results.clear()
                self.show_message("Results cleared")
            elif self.selected_option == 1:  # Export Results
                self.export_results()
            elif self.selected_option == 2:  # Back
                self.current_menu = "main"
                self.selected_option = 0

    def start_scan(self):
        """Start the appropriate scan based on current menu"""
        if self.scan_in_progress:
            self.show_message("Scan already in progress")
            return
        
        # Get target from user input (simplified for demo)
        target = self.get_user_input("Enter target: ")
        if not target:
            return
        
        self.scan_in_progress = True
        
        if self.current_menu == "port_scanner":
            self.scan_thread = threading.Thread(
                target=self.run_port_scan, 
                args=(target, "1-1000")
            )
        elif self.current_menu == "directory_buster":
            self.scan_thread = threading.Thread(
                target=self.run_directory_scan, 
                args=(target,)
            )
        elif self.current_menu == "vhost_scanner":
            domain = self.get_user_input("Enter domain: ")
            if not domain:
                self.scan_in_progress = False
                return
            self.scan_thread = threading.Thread(
                target=self.run_vhost_scan, 
                args=(target, domain)
            )
        elif self.current_menu == "host_scanner":
            self.scan_thread = threading.Thread(
                target=self.run_host_scan, 
                args=(target,)
            )
        
        if self.scan_thread:
            self.scan_thread.daemon = True
            self.scan_thread.start()
        else:
            self.scan_in_progress = False

    def run_port_scan(self, target, port_range):
        """Run port scan in separate thread"""
        try:
            results = self.port_scanner.scan(target, port_range, self.config.DEFAULT_THREADS)
            for result in results:
                self.results.append(f"[PORT] {result}")
        except Exception as e:
            self.results.append(f"[PORT] ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False

    def run_directory_scan(self, target):
        """Run directory scan in separate thread"""
        try:
            results = self.directory_buster.scan(target, "wordlists/common_dirs.txt")
            for result in results:
                self.results.append(f"[DIR] {result}")
        except Exception as e:
            self.results.append(f"[DIR] ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False

    def run_vhost_scan(self, target, domain):
        """Run virtual host scan in separate thread"""
        try:
            results = self.vhost_scanner.scan(target, domain, "wordlists/common_vhosts.txt")
            for result in results:
                self.results.append(f"[VHOST] {result}")
        except Exception as e:
            self.results.append(f"[VHOST] ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False

    def run_host_scan(self, target):
        """Run host scan in separate thread"""
        try:
            results = self.host_scanner.scan(target)
            for result in results:
                self.results.append(f"[HOST] {result}")
        except Exception as e:
            self.results.append(f"[HOST] ERROR: {str(e)}")
        finally:
            self.scan_in_progress = False

    def stop_scan(self):
        """Stop current scan"""
        if self.scan_in_progress and self.scan_thread:
            self.scan_in_progress = False
            self.show_message("Scan stopped")

    def get_user_input(self, prompt):
        """Get user input (simplified implementation)"""
        # In a full implementation, this would create an input dialog
        # For now, return a placeholder
        return "127.0.0.1"  # Default for demo

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
        """Export results to file"""
        try:
            with open("scan_results.txt", "w") as f:
                for result in self.results:
                    f.write(result + "\n")
            self.show_message("Results exported to scan_results.txt")
        except Exception as e:
            self.show_error(f"Export failed: {str(e)}")
