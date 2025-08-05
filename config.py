"""
Configuration settings for the Network Tools application
"""

import os

class Config:
    """Application configuration class"""
    
    # Default settings
    DEFAULT_THREADS = 50
    DEFAULT_TIMEOUT = 3
    MAX_THREADS = 100
    MIN_THREADS = 1
    
    # Port scanning settings
    PORT_SCAN_TIMEOUT = 3
    DEFAULT_PORT_RANGE = "1-1000"
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080
    ]
    
    # Directory busting settings
    DIR_SCAN_TIMEOUT = 5
    DIR_SCAN_THREADS = 10
    DEFAULT_EXTENSIONS = ['php', 'html', 'txt', 'js', 'asp', 'aspx', 'jsp', 'json', 'xml']
    
    # Virtual host scanning settings
    VHOST_SCAN_TIMEOUT = 5
    VHOST_SCAN_THREADS = 10
    
    # Host discovery settings
    HOST_SCAN_TIMEOUT = 3
    HOST_SCAN_THREADS = 50
    PING_TIMEOUT = 1
    
    # Network settings
    MAX_HOSTS_SCAN = 254
    DEFAULT_HTTP_PORTS = [80, 8080, 8000, 8443, 443]
    
    # File paths
    WORDLIST_DIR = "wordlists"
    RESULTS_DIR = "results"
    CONFIG_FILE = "network_tools.conf"
    
    # Output settings
    MAX_RESULTS_DISPLAY = 1000
    EXPORT_FORMAT = "txt"
    
    # User-Agent strings
    USER_AGENTS = [
        'Mozilla/5.0 (Linux; Security Scanner) NetworkTools/1.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    def __init__(self):
        """Initialize configuration"""
        self.load_config()
        self.create_directories()
    
    def load_config(self):
        """Load configuration from file or environment variables"""
        # Load from environment variables
        self.DEFAULT_THREADS = int(os.getenv('NET_TOOLS_THREADS', self.DEFAULT_THREADS))
        self.DEFAULT_TIMEOUT = int(os.getenv('NET_TOOLS_TIMEOUT', self.DEFAULT_TIMEOUT))
        
        # Validate settings
        self.DEFAULT_THREADS = max(self.MIN_THREADS, min(self.MAX_THREADS, self.DEFAULT_THREADS))
        
    def create_directories(self):
        """Create necessary directories"""
        directories = [self.WORDLIST_DIR, self.RESULTS_DIR]
        
        for directory in directories:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception:
                    pass  # Ignore if we can't create directories
    
    def get_common_ports_list(self):
        """Get list of common ports as string"""
        return ','.join(map(str, self.COMMON_PORTS))
    
    def get_user_agent(self, index=0):
        """Get user agent string"""
        return self.USER_AGENTS[index % len(self.USER_AGENTS)]
