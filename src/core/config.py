import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

PROFILES_FILE = os.getenv("CAMOUMGR_PROFILES_FILE", "profiles.json")
DATA_DIR = os.getenv("CAMOUMGR_DATA_DIR", "camoufox_data")
LOG_DIR = os.getenv("CAMOUMGR_LOG_DIR", "logs")
LOG_LEVEL = os.getenv("CAMOUMGR_LOG_LEVEL", "INFO")
PROXY_CHECK_TIMEOUT = int(os.getenv("CAMOUMGR_PROXY_TIMEOUT", "10"))

API_HOST = os.getenv("CAMOUMGR_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("CAMOUMGR_API_PORT", "8000"))
