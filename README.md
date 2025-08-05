# Network Security Tools

A comprehensive, interactive terminal-based networking utility suite for security professionals, network administrators, and developers.

## Features

### 🔍 Network Scanning Tools
- **Port Scanner** - Multi-threaded TCP port scanning with customizable ranges
- **Directory Buster** - Web directory and file enumeration using wordlists
- **Virtual Host Scanner** - Subdomain discovery and virtual host identification
- **Host Scanner** - Network discovery using ping and TCP connection methods

### 🎯 Interactive Terminal Interface
- Full arrow key navigation through all menus
- Real-time input dialogs for scan parameters
- Live configuration settings display
- Color-coded results (success, errors, warnings, info)
- Professional curses-based UI with proper formatting

### ⚙️ Advanced Configuration
- Configurable threads, timeouts, and scan parameters for each tool
- Persistent settings that can be saved and loaded
- Comprehensive wordlists for directory and virtual host scanning
- Default values with complete customization options

### 📊 Results Management
- **Inline Results Display** - Results appear directly within each tool's window
- Real-time timestamped result logging with color-coded status
- Tool-specific result filtering (clear results per tool)
- Comprehensive filtering system to search through all results
- Export results to timestamped files in organized directories
- Live scan progress indicators within each tool interface

## Installation

### Prerequisites
- Python 3.7 or higher
- Linux/Unix terminal (for optimal curses support)
- Network connectivity for web-based scanning

### Required Dependencies
The application automatically installs required dependencies:
```bash
pip install requests ipaddress
```

### Setup
1. Clone or download the project
2. Ensure all files are in the same directory
3. Run the application:
```bash
python main.py
```

## Usage

### Starting the Application
```bash
python main.py
```

### Navigation Controls
- **Arrow Keys (↑↓)** - Navigate through menu options
- **Enter** - Select current menu item
- **ESC** - Cancel current operation or stop scan
- **b** - Go back to previous menu
- **q** - Quit application

### Tool Usage

#### Port Scanner
1. Navigate to "Port Scanner" and press Enter
2. Configure settings if needed (threads, timeout, port range)
3. Select "Start Scan"
4. Enter target host/IP when prompted
5. Optionally customize port range (default: 1-1000)
6. View real-time results

#### Directory Buster
1. Navigate to "Directory Buster" and press Enter
2. Configure settings (wordlist, extensions, threads)
3. Select "Start Scan"
4. Enter target URL when prompted
5. Optionally specify custom wordlist and extensions
6. Monitor discovery results

#### Virtual Host Scanner
1. Navigate to "Virtual Host Scanner" and press Enter
2. Configure settings (wordlist, threads, timeout)
3. Select "Start Scan"
4. Enter target IP address
5. Enter domain name
6. Optionally specify custom wordlist
7. View discovered virtual hosts

#### Host Scanner
1. Navigate to "Host Scanner" and press Enter
2. Configure settings (scan method, threads, timeout)
3. Select "Start Scan"
4. Enter network range in CIDR notation (e.g., 192.168.1.0/24)
5. View discovered hosts

### Configuration Options

Each tool provides configurable settings:

**Port Scanner:**
- Port range (e.g., "1-1000", "80,443,8080")
- Thread count (1-100)
- Connection timeout (seconds)

**Directory Buster:**
- Wordlist file path
- File extensions to test
- Thread count
- Request timeout

**Virtual Host Scanner:**
- Wordlist file path
- Thread count
- Request timeout

**Host Scanner:**
- Scan method (ping+tcp)
- Thread count
- Ping timeout

### Results Management

**Viewing Results:**
1. Results appear directly within each tool's interface as scans complete
2. Each tool shows its specific results in real-time below the menu options
3. Results are color-coded by type and status (green for success, red for errors, yellow for warnings)
4. Navigate to "View Results" from main menu for consolidated view of all results

**Available Options in Each Tool:**
- **Start Scan** - Begin scanning with current settings
- **Configure Settings** - Modify tool-specific parameters
- **Clear Results** - Remove results for this specific tool only
- **Back to Main Menu** - Return to main interface

**Global Results Management:**
- **View Results** - See all results from all tools in one consolidated view
- **Export Results** - Save all results to timestamped file in results/ directory
- **Filter Results** - Search through all results by keyword

**Export Formats:**
- Results are exported to `results/scan_results_YYYYMMDD_HHMMSS.txt`
- Configuration saved to `network_tools_config.txt`

## File Structure

```
network-tools/
├── main.py                 # Application entry point
├── ui_manager.py          # Terminal interface manager
├── network_tools.py       # Core scanning implementations
├── config.py              # Configuration management
├── test_network_tools.py  # Test suite
├── wordlists/
│   ├── common_dirs.txt    # Directory enumeration wordlist
│   └── common_vhosts.txt  # Virtual host wordlist
└── results/               # Exported scan results (auto-created)
```

## Testing

Run the test suite to verify all functionality:
```bash
python test_network_tools.py
```

The test suite validates:
- Port scanning capabilities
- Directory enumeration
- Virtual host discovery
- Host discovery methods
- Configuration system

## Wordlists

The application includes comprehensive wordlists:

**Directory Wordlist** (`wordlists/common_dirs.txt`):
- 133+ common web directories and files
- Includes admin panels, backup locations, configuration files
- Standard web application paths

**Virtual Host Wordlist** (`wordlists/common_vhosts.txt`):
- 98+ common subdomain patterns
- Development, staging, and production environments
- Service-specific subdomains (mail, ftp, api, etc.)

## Security Considerations

**Ethical Usage:**
- Only scan networks and systems you own or have explicit permission to test
- Respect rate limits and avoid overwhelming target systems
- Be aware of legal implications in your jurisdiction

**Performance:**
- Default thread counts are conservative for stability
- Increase threads cautiously to avoid network congestion
- Monitor system resources during intensive scans

**Network Impact:**
- Tools generate network traffic that may be logged
- Directory and virtual host scanning can generate many HTTP requests
- Consider using VPN or proxy for sensitive testing

## Troubleshooting

**Common Issues:**

1. **Curses Display Problems:**
   - Ensure terminal supports curses
   - Try resizing terminal window
   - Use modern terminal emulator

2. **Permission Errors:**
   - Some features may require elevated privileges
   - Ping functionality might need sudo on some systems

3. **Network Connectivity:**
   - Verify internet connection for web-based tools
   - Check firewall settings if scans fail
   - Ensure target hosts are reachable

4. **Performance Issues:**
   - Reduce thread count in configuration
   - Increase timeout values for slow networks
   - Use smaller wordlists for faster scans

## Contributing

This is a complete, production-ready networking utility. For modifications:

1. Review the modular architecture in `network_tools.py`
2. UI modifications should be made in `ui_manager.py`
3. Configuration changes go in `config.py`
4. Add tests to `test_network_tools.py` for new features

## License

This software is provided for educational and authorized security testing purposes only. Users are responsible for complying with all applicable laws and regulations.

## Version

**Network Security Tools v1.0**
- Complete interactive terminal interface
- Four comprehensive scanning tools
- Advanced configuration and results management
- Production-ready with comprehensive error handling

---

**Quick Start:** Run `python main.py` and use arrow keys to navigate!