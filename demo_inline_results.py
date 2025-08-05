#!/usr/bin/env python3
"""
Demo script to show inline results functionality
Adds some sample results to demonstrate the new inline display feature
"""

from ui_manager import NetworkToolsUI
import curses
import time

def demo_inline_results(stdscr):
    """Demo the inline results display"""
    ui = NetworkToolsUI(stdscr)
    
    # Add some sample results for each tool
    ui.add_scan_result("PORT", "127.0.0.1:22 - OPEN")
    ui.add_scan_result("PORT", "127.0.0.1:80 - CLOSED")
    ui.add_scan_result("PORT", "127.0.0.1:443 - OPEN")
    ui.add_scan_result("PORT", "Port scan complete. Found 2 open ports")
    
    ui.add_scan_result("DIR", "Found: http://example.com/admin (Status: 200)")
    ui.add_scan_result("DIR", "Found: http://example.com/login (Status: 200)")
    ui.add_scan_result("DIR", "Found: http://example.com/backup (Status: 403)")
    ui.add_scan_result("DIR", "Directory scan complete")
    
    ui.add_scan_result("VHOST", "Found virtual host: api.example.com (Status: 200)")
    ui.add_scan_result("VHOST", "Found virtual host: www.example.com (Status: 403)")
    ui.add_scan_result("VHOST", "Virtual host scan complete")
    
    ui.add_scan_result("HOST", "Host 192.168.1.1 is alive")
    ui.add_scan_result("HOST", "Host 192.168.1.5 is alive")
    ui.add_scan_result("HOST", "Host discovery complete. Found 2 alive hosts")
    
    # Show message about new feature
    ui.show_message("Demo: Results now display inline within each tool window!")
    
    # Run the main interface
    ui.run()

if __name__ == "__main__":
    curses.wrapper(demo_inline_results)