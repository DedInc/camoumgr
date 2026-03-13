import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.app import create_app
from src.api.server import APIServer
from src.core.config import API_HOST, API_PORT
from src.core.container import Container
from src.core.logging import get_logger
from src.ui.app import App

logger = get_logger("main")


def main() -> None:
    container = Container()

    fastapi_app = create_app(container)
    api_server = APIServer(fastapi_app)
    api_server.start()
    logger.info("API available at http://%s:%s/api/v1", API_HOST, API_PORT)

    try:
        gui = App(container)
        gui.run()
    finally:
        api_server.stop()


if __name__ == "__main__":
    main()
