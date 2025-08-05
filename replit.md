# Network Tools Application

## Overview

This is a complete, production-ready interactive terminal-based networking utility application built in Python that provides four main network scanning and reconnaissance tools:

1. **Port Scanner** - TCP port scanning with multi-threading support and customizable ranges
2. **Directory Buster** - Web directory and file enumeration with wordlist support
3. **Virtual Host Scanner** - Virtual host discovery on web servers with subdomain enumeration
4. **Host Scanner** - Network host discovery using ping and TCP connection methods

The application features a professional curses-based terminal user interface with:
- Full arrow key navigation and interactive menus
- Real-time input dialogs for all scan parameters
- Configurable settings for each tool (threads, timeouts, wordlists)
- Real-time scan progress and results display
- Comprehensive result filtering and export capabilities
- Timestamped logging and configuration saving
- Color-coded results and error handling

It's designed for network administrators, security professionals, and developers who need to perform comprehensive network reconnaissance tasks.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Terminal User Interface Architecture
- **UI Framework**: Built using Python's `curses` library for cross-platform terminal interface
- **UI Manager**: Centralized `NetworkToolsUI` class handles all interface operations, menu navigation, and user input
- **Color Scheme**: Predefined color pairs for different message types (success, error, warning, info, highlight)
- **Non-blocking Input**: 100ms timeout for responsive interface while background scans execute
- **Thread-Safe Display**: Uses threading locks to safely update UI during concurrent scan operations

### Network Tools Architecture
- **Modular Design**: Each tool implemented as separate class (`PortScanner`, `DirectoryBuster`, `VirtualHostScanner`, `HostScanner`)
- **Multi-threading**: ThreadPoolExecutor for concurrent network operations with configurable thread limits
- **Socket-based Scanning**: Raw socket connections for port scanning with customizable timeouts
- **HTTP-based Enumeration**: Requests library for web-based scanning (directory busting, virtual hosts)

### Configuration Management
- **Centralized Config**: Single `Config` class containing all application settings and defaults
- **Scan Parameters**: Configurable timeouts, thread counts, port ranges, and file extensions
- **Resource Limits**: Built-in limits for maximum threads, hosts, and results to prevent resource exhaustion
- **Wordlist Support**: External wordlist files for directory and virtual host enumeration

### Data Flow Architecture
- **Input Validation**: User inputs validated before passing to network tools
- **Result Aggregation**: Scan results collected and stored in UI manager for display
- **Background Processing**: Network scans execute in separate threads to maintain UI responsiveness
- **Real-time Updates**: Results displayed in real-time as scans progress

## External Dependencies

### Python Standard Library
- **curses** - Terminal user interface framework
- **socket** - Low-level network socket operations
- **threading** - Multi-threading support for concurrent scans
- **subprocess** - System command execution for ping operations
- **ipaddress** - IP address parsing and validation
- **concurrent.futures** - High-level threading interface
- **urllib.parse** - URL parsing and manipulation

### Third-party Libraries
- **requests** - HTTP client library for web-based scanning operations

### System Dependencies
- **ping command** - System ping utility for host discovery (cross-platform)

### File Dependencies
- **Wordlist Files**: Text files containing common directory names and virtual host names
  - `wordlists/common_dirs.txt` - Common web directory names
  - `wordlists/common_vhosts.txt` - Common virtual host names
- **Results Directory**: File system location for storing scan results
- **Configuration File**: Optional external configuration file support

### Network Requirements
- **TCP Socket Access** - Required for port scanning operations
- **HTTP/HTTPS Access** - Required for directory busting and virtual host scanning
- **ICMP Access** - Required for ping-based host discovery (may require elevated privileges on some systems)