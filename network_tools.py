"""
Network Tools Implementation
Contains all the networking utilities: port scanner, directory buster, vhost scanner, and host scanner
"""

import socket
import threading
import time
import subprocess
import requests
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import os
import re

class PortScanner:
    """TCP Port Scanner with service detection and host discovery"""
    
    def __init__(self):
        self.timeout = 3
        self.open_ports = []
        self.lock = threading.Lock()
        self.service_detection = True
        self.host_discovery = True
        
        # Common service signatures
        self.service_signatures = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            6379: "Redis",
            8080: "HTTP-Alt",
            27017: "MongoDB"
        }

    def detect_service(self, target, port):
        """Attempt to detect service running on port"""
        if not self.service_detection:
            return None
            
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((target, port))
            
            # Send basic probe
            try:
                sock.send(b"\r\n")
                banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                sock.close()
                
                # Analyze banner for service identification
                if banner:
                    if "SSH" in banner.upper():
                        return f"SSH ({banner[:50]})"
                    elif "HTTP" in banner.upper() or "SERVER:" in banner.upper():
                        return "HTTP Server"
                    elif "FTP" in banner.upper():
                        return f"FTP ({banner[:30]})"
                    elif "SMTP" in banner.upper():
                        return f"SMTP ({banner[:30]})"
                    else:
                        return f"Service: {banner[:30]}"
            except:
                pass
            
            # Fall back to common port identification
            return self.service_signatures.get(port, "Unknown Service")
            
        except:
            return self.service_signatures.get(port, "Unknown Service")

    def check_host_alive(self, target):
        """Check if host is alive using ping"""
        if not self.host_discovery:
            return True
            
        try:
            # Try ping first
            result = subprocess.run(['ping', '-c', '1', '-W', '1', target], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Try TCP connect to common ports as fallback
        common_ports = [80, 443, 22, 23, 21]
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                if sock.connect_ex((target, port)) == 0:
                    sock.close()
                    return True
                sock.close()
            except:
                continue
        return False

    def scan_port(self, target, port):
        """Scan a single port with service detection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                with self.lock:
                    self.open_ports.append(port)
                
                # Detect service if enabled
                service = self.detect_service(target, port) if self.service_detection else ""
                service_info = f" [{service}]" if service else ""
                
                return f"{target}:{port} - OPEN{service_info}"
            else:
                return None
        except socket.gaierror:
            return f"{target}:{port} - DNS resolution failed"
        except Exception as e:
            return f"{target}:{port} - ERROR: {str(e)}"

    def scan(self, target, port_range, threads=50):
        """Scan multiple ports with threading and host discovery"""
        self.open_ports = []
        results = []
        
        # Check if host is alive first
        if self.host_discovery:
            results.append(f"Checking if {target} is alive...")
            if not self.check_host_alive(target):
                results.append(f"WARNING: {target} appears to be down or filtering packets")
                results.append("Continuing scan anyway...")
            else:
                results.append(f"Host {target} is alive")
        
        # Parse port range
        if '-' in port_range:
            start_port, end_port = map(int, port_range.split('-'))
            ports = range(start_port, end_port + 1)
        elif ',' in port_range:
            ports = [int(p.strip()) for p in port_range.split(',')]
        else:
            ports = [int(port_range)]
        
        results.append(f"Starting port scan on {target} ({len(list(ports))} ports)")
        
        # Use ThreadPoolExecutor for better thread management
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_port = {
                executor.submit(self.scan_port, target, port): port 
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                result = future.result()
                if result:
                    results.append(result)
        
        # Add summary with service detection info
        service_info = " with service detection" if self.service_detection else ""
        results.append(f"Port scan complete{service_info}. Found {len(self.open_ports)} open ports")
        
        return results

class DirectoryBuster:
    """Web Directory and File Discovery Tool"""
    
    def __init__(self):
        self.timeout = 5
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Security Scanner) NetworkTools/1.0'
        })

    def test_directory(self, base_url, directory, extensions=None):
        """Test if a directory or file exists with detailed status info"""
        results = []
        
        # Test directory
        url = urljoin(base_url, directory)
        try:
            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            status_info = self.get_status_info(response.status_code)
            
            # Show results for interesting status codes
            if response.status_code in [200, 301, 302, 403, 401, 500]:
                size_info = f" [{len(response.content)} bytes]" if response.status_code == 200 else ""
                results.append(f"Found: {url} (Status: {response.status_code} - {status_info}){size_info}")
        except requests.exceptions.RequestException as e:
            results.append(f"ERROR testing {url}: {str(e)}")
        
        # Test with extensions if provided
        if extensions:
            for ext in extensions:
                test_url = f"{url}.{ext}"
                try:
                    response = self.session.get(test_url, timeout=self.timeout, allow_redirects=False)
                    status_info = self.get_status_info(response.status_code)
                    
                    if response.status_code in [200, 301, 302, 403, 401, 500]:
                        size_info = f" [{len(response.content)} bytes]" if response.status_code == 200 else ""
                        results.append(f"Found: {test_url} (Status: {response.status_code} - {status_info}){size_info}")
                except requests.exceptions.RequestException:
                    pass
        
        return results
    
    def get_status_info(self, status_code):
        """Get human-readable status information"""
        status_map = {
            200: "OK - Accessible",
            301: "Moved Permanently",
            302: "Found/Redirect",
            400: "Bad Request",
            401: "Unauthorized - Login Required",
            403: "Forbidden - Access Denied",
            404: "Not Found",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        return status_map.get(status_code, f"Status {status_code}")

    def scan(self, target_url, wordlist_path, extensions=None):
        """Perform directory busting scan"""
        results = []
        
        # Ensure URL has proper scheme
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url
        
        # Default extensions
        if extensions is None:
            extensions = ['php', 'html', 'txt', 'js', 'asp', 'aspx', 'jsp']
        
        # Load wordlist
        wordlist = self.load_wordlist(wordlist_path)
        if not wordlist:
            return ["ERROR: Could not load wordlist"]
        
        results.append(f"Starting directory scan on {target_url}")
        results.append(f"Loaded {len(wordlist)} words from wordlist")
        
        # Test each directory/file
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_word = {
                executor.submit(self.test_directory, target_url, word, extensions): word 
                for word in wordlist
            }
            
            for future in as_completed(future_to_word):
                try:
                    word_results = future.result()
                    results.extend(word_results)
                except Exception as e:
                    continue
        
        results.append("Directory scan complete")
        return results

    def load_wordlist(self, wordlist_path):
        """Load wordlist from file"""
        try:
            if os.path.exists(wordlist_path):
                with open(wordlist_path, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            else:
                # Return a basic wordlist if file doesn't exist
                return [
                    'admin', 'administrator', 'login', 'uploads', 'upload',
                    'images', 'js', 'css', 'includes', 'inc', 'config',
                    'backup', 'backups', 'db', 'database', 'sql', 'test',
                    'temp', 'tmp', 'logs', 'log', 'api', 'assets', 'files'
                ]
        except Exception:
            return []

class VirtualHostScanner:
    """Virtual Host Discovery Scanner"""
    
    def __init__(self):
        self.timeout = 5
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Security Scanner) NetworkTools/1.0'
        })

    def test_vhost(self, target_ip, vhost, domain):
        """Test a virtual host with detailed status information"""
        results = []
        
        try:
            # Test HTTP
            vhost_name = f"{vhost}.{domain}"
            url = f"http://{target_ip}/"
            headers = {'Host': vhost_name}
            
            response = self.session.get(url, headers=headers, timeout=self.timeout, allow_redirects=False)
            
            # Also test without subdomain for comparison
            default_headers = {'Host': domain}
            try:
                default_response = self.session.get(url, headers=default_headers, timeout=self.timeout, allow_redirects=False)
            except:
                default_response = None
            
            # Analyze response
            status_info = self.get_vhost_status_info(response.status_code)
            
            # Check if virtual host exists
            is_different = True
            if default_response:
                is_different = (response.status_code != default_response.status_code or 
                              len(response.content) != len(default_response.content))
            
            # Report findings based on status and differences
            if response.status_code in [200, 301, 302, 403, 401]:
                alive_status = "ALIVE" if is_different else "POSSIBLE"
                size_info = f" [{len(response.content)} bytes]" if response.status_code == 200 else ""
                return f"Found virtual host: {vhost_name} (Status: {response.status_code} - {status_info}) [{alive_status}]{size_info}"
            
            elif response.status_code == 404 and is_different:
                return f"Virtual host: {vhost_name} (Status: 404 - Custom Not Found) [ALIVE]"
                
        except requests.exceptions.RequestException as e:
            return f"ERROR testing {vhost}.{domain}: Connection failed"
        
        return None
    
    def get_vhost_status_info(self, status_code):
        """Get status information for virtual hosts"""
        status_map = {
            200: "OK - Active",
            301: "Moved Permanently", 
            302: "Found/Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Configured but Restricted",
            404: "Not Found",
            500: "Internal Server Error - Misconfigured",
            502: "Bad Gateway",
            503: "Service Unavailable"
        }
        return status_map.get(status_code, f"Status {status_code}")

    def scan(self, target_ip, domain, wordlist_path):
        """Perform virtual host scanning"""
        results = []
        
        # Load wordlist
        wordlist = self.load_wordlist(wordlist_path)
        if not wordlist:
            return ["ERROR: Could not load wordlist"]
        
        results.append(f"Starting virtual host scan on {target_ip} for {domain}")
        results.append(f"Loaded {len(wordlist)} subdomains from wordlist")
        
        # Test each virtual host
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_vhost = {
                executor.submit(self.test_vhost, target_ip, vhost, domain): vhost 
                for vhost in wordlist
            }
            
            for future in as_completed(future_to_vhost):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception:
                    continue
        
        results.append("Virtual host scan complete")
        return results

    def load_wordlist(self, wordlist_path):
        """Load virtual host wordlist from file"""
        try:
            if os.path.exists(wordlist_path):
                with open(wordlist_path, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            else:
                # Return a basic vhost wordlist if file doesn't exist
                return [
                    'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging',
                    'api', 'blog', 'shop', 'store', 'forum', 'support',
                    'help', 'docs', 'cdn', 'static', 'media', 'images',
                    'secure', 'vpn', 'remote', 'portal', 'intranet'
                ]
        except Exception:
            return []

class HostScanner:
    """Network Host Discovery Scanner"""
    
    def __init__(self):
        self.timeout = 3
        self.alive_hosts = []
        self.lock = threading.Lock()

    def ping_host(self, ip):
        """Ping a single host"""
        try:
            # Use ping command
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '1', str(ip)], 
                capture_output=True, 
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                with self.lock:
                    self.alive_hosts.append(str(ip))
                return f"Host {ip} is alive (ping)"
            
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        return None

    def tcp_connect_scan(self, ip, port=80):
        """Try TCP connection to detect host"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((str(ip), port))
            sock.close()
            
            if result == 0:
                with self.lock:
                    if str(ip) not in self.alive_hosts:
                        self.alive_hosts.append(str(ip))
                return f"Host {ip} is alive (TCP:{port})"
                
        except Exception:
            pass
        
        return None

    def scan(self, network_range):
        """Perform host discovery scan"""
        results = []
        self.alive_hosts = []
        
        try:
            # Parse network range
            network = ipaddress.ip_network(network_range, strict=False)
            hosts = list(network.hosts())
            
            # Limit scan to reasonable size
            if len(hosts) > 254:
                hosts = hosts[:254]
                results.append(f"Limiting scan to first 254 hosts")
            
            results.append(f"Starting host discovery on {network_range}")
            results.append(f"Scanning {len(hosts)} hosts")
            
            # Ping scan
            with ThreadPoolExecutor(max_workers=50) as executor:
                future_to_ip = {
                    executor.submit(self.ping_host, ip): ip 
                    for ip in hosts
                }
                
                for future in as_completed(future_to_ip):
                    result = future.result()
                    if result:
                        results.append(result)
            
            # TCP connect scan on port 80 for hosts that didn't respond to ping
            remaining_hosts = [ip for ip in hosts if str(ip) not in self.alive_hosts]
            
            if remaining_hosts:
                with ThreadPoolExecutor(max_workers=20) as executor:
                    future_to_ip = {
                        executor.submit(self.tcp_connect_scan, ip, 80): ip 
                        for ip in remaining_hosts[:50]  # Limit TCP scan
                    }
                    
                    for future in as_completed(future_to_ip):
                        result = future.result()
                        if result:
                            results.append(result)
            
            results.append(f"Host discovery complete. Found {len(self.alive_hosts)} alive hosts")
            
        except ValueError as e:
            results.append(f"ERROR: Invalid network range - {str(e)}")
        except Exception as e:
            results.append(f"ERROR: {str(e)}")
        
        return results

    def arp_scan(self, interface="eth0"):
        """Perform ARP scan (requires root privileges)"""
        try:
            result = subprocess.run(
                ['arp-scan', '-l', f'-I{interface}'], 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.split('\n')
            else:
                return ["ARP scan failed - may require root privileges"]
                
        except subprocess.TimeoutExpired:
            return ["ARP scan timed out"]
        except FileNotFoundError:
            return ["arp-scan not found - install arp-scan package"]
        except Exception as e:
            return [f"ARP scan error: {str(e)}"]
