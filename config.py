import os
from pathlib import Path

from dotenv import load_dotenv


# ---------------------------------------------------------
# Directories
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = BASE_DIR / "downloads"
LOG_DIR = BASE_DIR / "logs"

DOWNLOAD_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------
# Environment variables
# ---------------------------------------------------------

load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Green Sheet
# ---------------------------------------------------------

GREENSHEET_USERNAME = os.getenv("GREENSHEET_USERNAME")
GREENSHEET_PASSWORD = os.getenv("GREENSHEET_PASSWORD")

GREENSHEET_BASE_URL = "https://greensheet.ca"


GREENSHEET_LOGIN_URL = "https://greensheet.ca/login.php"
GREENSHEET_PROJECTS_URL = "https://greensheet.ca/members/project_results.php?button_clicked=btn_search&override=yes&city_select%5B%5D=&type_select%5B%5D=71&type_select%5B%5D=26&type_select%5B%5D=24&type_select%5B%5D=92&type_select%5B%5D=93&stage_select%5B%5D=6&stage_select%5B%5D=4&stage_select%5B%5D=7&stage_select%5B%5D=10&stage_select%5B%5D=9&consultant_select=&address_select=&ref_select=&storeys_select%5B%5D=1&storeys_select%5B%5D=2&storeys_select%5B%5D=3&units_select%5B%5D=1&units_select%5B%5D=2&units_select%5B%5D=3&units_select%5B%5D=4&issue_select=now&issue_select2=now"
GREENSHEET_PERMITS_URL = "https://greensheet.ca/members/zone_results.php?zone=zoneall&SEARCH_x=Advanced+Search&override=yes&city_select%5B%5D=&ptype_select%5B%5D=71&ptype_select%5B%5D=26&ptype_select%5B%5D=24&owner_select=&address_select=&amount1=0&amount2=0&issue_select=now&issue_select2=now&feedname="


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

DB_SERVER = os.getenv("DB_SERVER")
DB_DATABASE = os.getenv("DB_DATABASE")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ---------------------------------------------------------
# Playwright
# ---------------------------------------------------------

# Keep False while developing.
# This lets you watch the browser.
HEADLESS = False

BROWSER_TIMEOUT = 60_000


# ---------------------------------------------------------
# Configuration validation
# ---------------------------------------------------------

def validate_config():

    missing = []

    if not GREENSHEET_USERNAME:
        missing.append("GREENSHEET_USERNAME")

    if not GREENSHEET_PASSWORD:
        missing.append("GREENSHEET_PASSWORD")

    if not DB_SERVER:
        missing.append("DB_SERVER")

    if not DB_DATABASE:
        missing.append("DB_DATABASE")

    if missing:
        raise RuntimeError(
            "Missing configuration values: "
            + ", ".join(missing)
        )