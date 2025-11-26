import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from camoufox.async_api import AsyncCamoufox
from src.config import DATA_DIR
from src.utils.proxy_parser import parse_proxy


async def run_browser(profile_name, proxy_str, os_type):
    profile_dir = os.path.join(os.getcwd(), DATA_DIR, profile_name)
    
    launch_config = {
        "headless": False,
        "os": os_type,
        "humanize": True,
        "geoip": True,
        "block_images": False,
        "user_data_dir": profile_dir,
        "persistent_context": True,
    }

    proxy_config = parse_proxy(proxy_str)
    if proxy_config:
        launch_config["proxy"] = proxy_config

    print(f"Starting browser for {profile_name}...", flush=True)
    
    try:
        async with AsyncCamoufox(**launch_config) as context:
            print("BROWSER_STARTED", flush=True)
            
            if context.pages:
                page = context.pages[0]
            else:
                page = await context.new_page()
            
            close_event = asyncio.Event()

            def on_close():
                close_event.set()

            context.on("close", on_close)
            page.on("close", on_close)
            
            await close_event.wait() 
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error: {e}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python run_browser.py <name> <proxy> <os>")
        sys.exit(1)
        
    name = sys.argv[1]
    proxy = sys.argv[2]
    os_type = sys.argv[3]
    
    try:
        asyncio.run(run_browser(name, proxy, os_type))
    except KeyboardInterrupt:
        pass
