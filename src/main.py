import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.container import Container
from src.ui.app import App


def main():
    container = Container()
    app = App(container)
    app.run()


if __name__ == "__main__":
    main()
