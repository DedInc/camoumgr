import asyncio
import json
import os
import shutil
import traceback
import logging
from typing import Optional, Dict
from dataclasses import dataclass, asdict

from camoufox.async_api import AsyncCamoufox
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

# Уменьшаем шум логов, оставляем только важное
logging.basicConfig(level=logging.WARNING)

# --- CONFIG ---
PROFILES_FILE = "profiles.json"
DATA_DIR = "camoufox_data"

console = Console()

@dataclass
class Profile:
    name: str
    proxy: Optional[str] = None
    os_type: str = "windows"
    
    def to_dict(self):
        return asdict(self)

class ProfileManager:
    def __init__(self):
        self.profiles: Dict[str, Profile] = {}
        self.load_profiles()
        os.makedirs(DATA_DIR, exist_ok=True)

    def load_profiles(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, p_data in data.items():
                        clean_data = {
                            "name": p_data.get("name"),
                            "proxy": p_data.get("proxy"),
                            "os_type": p_data.get("os_type", p_data.get("config", {}).get("os", "windows"))
                        }
                        self.profiles[name] = Profile(**clean_data)
            except Exception:
                pass

    def save_profiles(self):
        with open(PROFILES_FILE, 'w', encoding='utf-8') as f:
            json.dump({name: p.to_dict() for name, p in self.profiles.items()}, f, indent=4)

    def add_profile(self, name: str, proxy: str, os_type: str):
        if name in self.profiles: return False
        self.profiles[name] = Profile(name=name, proxy=proxy if proxy else None, os_type=os_type)
        self.save_profiles()
        os.makedirs(os.path.join(DATA_DIR, name), exist_ok=True)
        return True

    def delete_profile(self, name: str):
        if name in self.profiles:
            del self.profiles[name]
            self.save_profiles()
            shutil.rmtree(os.path.join(DATA_DIR, name), ignore_errors=True)
            return True
        return False

    def list_profiles(self):
        return list(self.profiles.values())

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
    async def start(profile: Profile):
        profile_dir = os.path.join(os.getcwd(), DATA_DIR, profile.name)
        state_file = os.path.join(profile_dir, "state.json")
        
        # === ИСПРАВЛЕННЫЙ КОНФИГ ===
        # Мы убрали "fonts": True и "webgl": True.
        # Параметр 'os' сам подтянет нужные шрифты и видеокарту.
        launch_config = {
            "headless": False,
            "os": profile.os_type,  # Это главное. Оно включает спуфинг под ОС.
            "humanize": True,       # Эмуляция мыши
            "geoip": True,          # Таймзона под IP
            "block_images": False,
        }

        proxy_conf = BrowserLauncher.parse_proxy(profile.proxy)
        if proxy_conf:
            launch_config["proxy"] = proxy_conf

        console.print(Panel(
            f"[bold green]Profile:[/bold green] {profile.name}\n"
            f"[bold yellow]OS:[/bold yellow] {profile.os_type}\n"
            f"[bold blue]Proxy:[/bold blue] {profile.proxy or 'Direct'}",
            title="🚀 Native Camoufox", border_style="green"
        ))

        try:
            console.print("[dim]Starting engine...[/dim]")
            
            async with AsyncCamoufox(**launch_config) as browser:
                console.print("[green]Browser started![/green]")
                
                context_options = {"locale": "en-US"}
                if os.path.exists(state_file):
                    context_options["storage_state"] = state_file
                    console.print(f"[dim]✓ Session loaded[/dim]")

                context = await browser.new_context(**context_options)
                page = await context.new_page()
                
                # Проверка
                try:
                    await page.goto("https://www.browserscan.net/bot-detection", timeout=30000, wait_until="domcontentloaded")
                except:
                    pass

                # KEEP ALIVE
                close_event = asyncio.Event()
                
                def on_close():
                    console.print("[yellow]Browser closed.[/yellow]")
                    close_event.set()

                browser.on("disconnected", on_close)
                page.on("close", on_close)

                console.print("[bold white]Running... Press Ctrl+C to stop.[/bold white]")
                
                await close_event.wait()
                
                console.print("[yellow]Saving cookies...[/yellow]")
                try:
                    await context.storage_state(path=state_file)
                    console.print("[green]Saved![/green]")
                except Exception:
                    pass

        except asyncio.CancelledError:
            console.print("\n[yellow]Stopped.[/yellow]")
        except Exception as e:
            console.print("\n[bold red]CRITICAL ERROR:[/bold red]")
            console.print(traceback.format_exc())
            Prompt.ask("\n[bold red]PRESS ENTER TO MENU...[/bold red]")

# --- MENU ---

def print_header():
    console.clear()
    console.print(Panel.fit("[bold white]CAMOUFOX MANAGER[/bold white] [dim]v3.2 Fixed[/dim]", style="blue"))

async def main_menu():
    pm = ProfileManager()
    
    while True:
        print_header()
        
        table = Table(box=None, show_header=True, header_style="bold cyan")
        table.add_column("#", width=3)
        table.add_column("Name", style="bold")
        table.add_column("OS", style="magenta")
        table.add_column("Proxy", style="green")

        profiles = pm.list_profiles()
        for i, p in enumerate(profiles):
            icon = "🪟" if p.os_type == 'windows' else ("🍎" if p.os_type == 'macos' else "🐧")
            table.add_row(str(i+1), p.name, icon, "✅" if p.proxy else "❌")

        console.print(table)
        console.print("\n[1] Launch  [2] Create  [3] Delete  [4] Exit")
        
        cmd = Prompt.ask("Select", choices=["1", "2", "3", "4"], default="1")

        if cmd == "1":
            if not profiles: continue
            idx = int(Prompt.ask("ID", default="1")) - 1
            if 0 <= idx < len(profiles):
                await BrowserLauncher.start(profiles[idx])

        elif cmd == "2":
            name = Prompt.ask("Name")
            proxy = Prompt.ask("Proxy (user:pass@ip:port) [Empty=None]")
            os_type = Prompt.ask("OS", choices=["windows", "macos", "linux"], default="windows")
            pm.add_profile(name, proxy.strip(), os_type)

        elif cmd == "3":
            idx = int(Prompt.ask("ID", default="1")) - 1
            if 0 <= idx < len(profiles):
                pm.delete_profile(profiles[idx].name)

        elif cmd == "4":
            break

if __name__ == "__main__":
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        pass