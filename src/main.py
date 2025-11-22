import sys
import os

# Add the current directory to sys.path so that we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import setup_theme
from src.ui.app import App

if __name__ == "__main__":
    setup_theme()
    app = App()
    app.mainloop()
