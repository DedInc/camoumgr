import asyncio
import os
import threading
from typing import Optional, Dict
from camoufox.async_api import AsyncCamoufox
from ..models.profile import Profile
from ..config import DATA_DIR

class BrowserLauncher:
    @staticmethod
    def parse_proxy(proxy_str: str) -> Optional[Dict]:
        if not proxy_str: return None
        try:
            if "://" not in proxy_str: proxy_str = "http://" + proxy_str
            from urllib.parse import urlparse
            p = urlparse(proxy_str)
            cfg = {"server": f"{p.scheme}://{p.hostname}:{p.port}"}
            if p.username: cfg["username"] = p.username
            if p.password: cfg["password"] = p.password
            return cfg
        except:
            return None

    @staticmethod
    async def start_async(profile: Profile, log_callback):
        profile_dir = os.path.join(os.getcwd(), DATA_DIR, profile.name)
        state_file = os.path.join(profile_dir, "state.json")
        
        launch_config = {
            "headless": False,
            "os": profile.os_type,
            "humanize": True,
            "geoip": True,
            "block_images": False,
        }

        proxy_conf = BrowserLauncher.parse_proxy(profile.proxy)
        if proxy_conf:
            launch_config["proxy"] = proxy_conf

        log_callback(f"Starting {profile.name} ({profile.os_type})...")
        
        try:
            async with AsyncCamoufox(**launch_config) as browser:
                log_callback("Browser started!")
                
                context_options = {"locale": "en-US"}
                if os.path.exists(state_file):
                    context_options["storage_state"] = state_file
                    log_callback("Session loaded.")

                context = await browser.new_context(**context_options)
                page = await context.new_page()
                
                try:
                    await page.goto("https://www.browserscan.net/bot-detection", timeout=30000, wait_until="domcontentloaded")
                except:
                    pass

                close_event = asyncio.Event()
                
                def on_close():
                    log_callback("Browser closed.")
                    close_event.set()

                browser.on("disconnected", on_close)
                page.on("close", on_close)

                log_callback("Running... Close browser to stop.")
                
                await close_event.wait()
                
                log_callback("Saving cookies...")
                try:
                    await context.storage_state(path=state_file)
                    log_callback("Saved!")
                except Exception:
                    pass

        except asyncio.CancelledError:
            log_callback("Stopped.")
        except Exception as e:
            log_callback(f"Error: {str(e)}")

    @staticmethod
    def start_thread(profile: Profile, log_callback):
        def run():
            asyncio.run(BrowserLauncher.start_async(profile, log_callback))
        
        t = threading.Thread(target=run, daemon=True)
        t.start()
