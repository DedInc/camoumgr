import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import setup_theme
from src.ui.app import App


def main():
    setup_theme()
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
