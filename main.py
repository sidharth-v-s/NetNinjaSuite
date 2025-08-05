#!/usr/bin/env python3
"""
Interactive Terminal-Based Networking Utility
Main entry point for the networking tools application
"""

import curses
import sys
import traceback
from ui_manager import NetworkToolsUI

def main():
    """Main function to initialize and run the application"""
    try:
        # Initialize curses and run the application
        curses.wrapper(run_app)
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

def run_app(stdscr):
    """Run the main application with curses"""
    # Initialize the UI manager
    ui = NetworkToolsUI(stdscr)
    
    # Run the main loop
    ui.run()

if __name__ == "__main__":
    main()
