import os
import threading
import subprocess
import sys
from typing import Dict

from ..models.profile import Profile
from ..logging_config import get_logger

logger = get_logger("browser_launcher")


class BrowserLauncher:
    _lock = threading.Lock()
    active_sessions: Dict[str, subprocess.Popen] = {}

    @classmethod
    def start_thread(cls, profile: Profile, log_callback, on_start=None, on_ready=None, on_stop=None):
        with cls._lock:
            if profile.name in cls.active_sessions:
                return

        log_callback(f"Starting {profile.name} ({profile.os_type})...")
        logger.info(f"Starting browser for profile: {profile.name}")
        
        if on_start:
            on_start()

        def monitor_process(proc, name):
            for line in iter(proc.stdout.readline, b''):
                msg = line.decode().strip()
                if msg == "BROWSER_STARTED":
                    if on_ready:
                        on_ready()
                    log_callback("Browser started!")
                    logger.info(f"Browser started for profile: {name}")
                elif msg:
                    log_callback(f"[{name}] {msg}")
                    logger.debug(f"[{name}] {msg}")
            
            with cls._lock:
                if name in cls.active_sessions:
                    del cls.active_sessions[name]
            
            log_callback(f"Session ended: {name}")
            logger.info(f"Session ended for profile: {name}")
            
            if on_stop:
                on_stop()

        try:
            cmd = [sys.executable, "src/services/run_browser.py", profile.name, str(profile.proxy), profile.os_type]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
            
            with cls._lock:
                cls.active_sessions[profile.name] = proc
            
            threading.Thread(target=monitor_process, args=(proc, profile.name), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error starting browser for {profile.name}: {e}")
            log_callback(f"Error starting process: {e}")
            if on_stop:
                on_stop()

    @classmethod
    def stop_profile(cls, profile_name: str) -> bool:
        with cls._lock:
            if profile_name in cls.active_sessions:
                proc = cls.active_sessions[profile_name]
                proc.terminate()
                logger.info(f"Stopped browser for profile: {profile_name}")
                return True
        return False
    
    @classmethod
    def is_running(cls, profile_name: str) -> bool:
        with cls._lock:
            return profile_name in cls.active_sessions
