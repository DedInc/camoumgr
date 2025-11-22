import os
import threading
import subprocess
import sys
from typing import Optional, Dict
from ..models.profile import Profile

class BrowserLauncher:
    @staticmethod
    def parse_proxy(proxy_str: str) -> Optional[Dict]:
        if not proxy_str:
            return None
        try:
            if "://" not in proxy_str:
                proxy_str = "http://" + proxy_str
            from urllib.parse import urlparse
            p = urlparse(proxy_str)
            cfg = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
            if p.username:
                cfg["username"] = p.username
            if p.password:
                cfg["password"] = p.password
            return cfg
        except Exception:
            return None

    active_sessions: Dict[str, subprocess.Popen] = {}

    @staticmethod
    def start_thread(profile: Profile, log_callback, on_start=None, on_ready=None, on_stop=None):
        if profile.name in BrowserLauncher.active_sessions:
            return

        log_callback(f"Starting {profile.name} ({profile.os_type})...")
        if on_start:
            on_start()

        def monitor_process(proc, name):
            for line in iter(proc.stdout.readline, b''):
                msg = line.decode().strip()
                if msg == "BROWSER_STARTED":
                    if on_ready:
                        on_ready()
                    log_callback("Browser started!")
                elif msg:
                    log_callback(f"[{name}] {msg}")
            
            # Process ended
            if name in BrowserLauncher.active_sessions:
                del BrowserLauncher.active_sessions[name]
            
            log_callback(f"Session ended: {name}")
            if on_stop:
                on_stop()

        try:
            cmd = [sys.executable, "src/services/run_browser.py", profile.name, str(profile.proxy), profile.os_type]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
            
            BrowserLauncher.active_sessions[profile.name] = proc
            
            # Start monitor thread
            threading.Thread(target=monitor_process, args=(proc, profile.name), daemon=True).start()
            
        except Exception as e:
            log_callback(f"Error starting process: {e}")
            if on_stop:
                on_stop()

    @staticmethod
    def stop_profile(profile_name: str):
        if profile_name in BrowserLauncher.active_sessions:
            proc = BrowserLauncher.active_sessions[profile_name]
            proc.terminate()
            return True
        return False
