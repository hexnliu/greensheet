# Green Sheet Weekly Importer

Python automation for downloading Project and Building Permit data from Green Sheet, normalizing the exported data, saving it as CSV, and importing it into a database.

## Features

- Automatically logs into Green Sheet
- Uses Playwright/Chromium for browser automation
- Downloads Project data
- Downloads Building Permit data
- Handles Green Sheet Excel/HTML exports
- Normalizes data using Pandas
- Creates clean CSV files
- Imports Projects and Permits into a database
- Uses environment variables for credentials and configuration
- Generates logs for troubleshooting

## Project Structure

```text
greensheet/
│
├── main.py
├── config.py
├── greensheet_client.py
├── parser.py
├── database.py
├── logger.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
├── .env.example
│
├── downloads/
│   ├── projects-YYYYMMDD-HHMMSS.csv
│   └── permits-YYYYMMDD-HHMMSS.csv
│
└── logs/
```

## Requirements

- Python 3.13+
- Google Chromium / Playwright Chromium
- Access to Green Sheet
- Database access if database importing is enabled

## Installation

Clone or download the project and open a terminal in the project directory.

Create a virtual environment:

```bash
py -3.13 -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Install the Playwright Chromium browser:

```bash
playwright install chromium
```

## Python Dependencies

The project uses packages including:

```text
python-dotenv
playwright
pandas
pyodbc
openpyxl
xlrd
lxml
```

These should be included in `requirements.txt`.

Example:

```text
python-dotenv
playwright
pandas
pyodbc
openpyxl
xlrd
lxml
```

## Configuration

Configuration is stored in a local `.env` file.

**Never commit `.env` to Git.**

Create `.env` in the project root:

```text
greensheet/
    .env
    main.py
    config.py
    ...
```

Example:

```env
GREENSHEET_USERNAME=your_username
GREENSHEET_PASSWORD=your_password

GREENSHEET_PROJECTS_URL=https://greensheet.ca/members/main-menu.php

GREENSHEET_PERMITS_URL=https://greensheet.ca/members/zone_results.php?zone=zoneall&...

DB_SERVER=your_database_server
DB_DATABASE=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

Use the actual variable names expected by `config.py`.

## Environment Template

The repository should contain `.env.example`, but not the real `.env`.

Example `.env.example`:

```env
GREENSHEET_USERNAME=
GREENSHEET_PASSWORD=

GREENSHEET_PROJECTS_URL=
GREENSHEET_PERMITS_URL=

DB_SERVER=
DB_DATABASE=
DB_USERNAME=
DB_PASSWORD=
```

Developers can copy it:

```bash
copy .env.example .env
```

and then enter their own credentials.

## Running the Importer

Run:

```bash
python main.py
```

or:

```bash
py -3.13 main.py
```

The importer will:

1. Validate configuration.
2. Start Chromium.
3. Log into Green Sheet.
4. Download Projects.
5. Download Building Permits.
6. Normalize the downloaded data.
7. Create CSV files.
8. Connect to the configured database.
9. Upsert Projects.
10. Upsert Permits.
11. Commit the database transaction.

## CSV Output

Generated CSV files are stored under:

```text
downloads/
```

For example:

```text
projects-20260820-143500.csv
permits-20260820-143500.csv
```

The timestamp prevents one import from accidentally overwriting another.

## Green Sheet Export Format

Green Sheet's Excel export may not be a native Excel workbook.

The importer detects the returned format and supports:

- XLSX
- XLS
- HTML tables presented as Excel downloads
- CSV/text exports

The parser converts the downloaded data into a Pandas DataFrame before normalization.

## Logging

The importer logs each major operation, including:

```text
Starting Green Sheet weekly import
Starting Chromium...
Logging into Green Sheet...
Fetching Projects...
Projects found: ...
Fetching Building Permits...
Permits found: ...
Creating Projects CSV...
Creating Permits CSV...
Saving Projects...
Saving Permits...
Green Sheet import completed.
```

Errors include a Python traceback to help diagnose failures.

## Security

Do not place passwords directly in Python source files.

Credentials and environment-specific configuration belong in:

```text
.env
```

The `.env` file is excluded from Git through `.gitignore`.

Never commit:

- Green Sheet passwords
- Database passwords
- Connection strings containing passwords
- Browser/session credentials
- Production `.env` files

If a credential is accidentally committed to Git, removing the file afterward is not sufficient. Rotate the exposed credential and remove it from Git history if necessary.

## Troubleshooting

### Playwright browser missing

If you see:

```text
BrowserType.launch: Executable doesn't exist
```

run:

```bash
playwright install chromium
```

### Missing Python package

For example:

```text
ModuleNotFoundError: No module named 'pandas'
```

install the dependencies:

```bash
pip install -r requirements.txt
```

### ODBC IM002 Error

If you see:

```text
[IM002] [Microsoft][ODBC Driver Manager]
Data source name not found and no default driver specified
```

check that:

- The required ODBC driver is installed.
- The configured driver name is correct.
- The configured DSN exists, if using a DSN.
- The database server and database configuration are correct.

Available ODBC drivers can be checked with:

```bash
py -3.13 -c "import pyodbc; print(pyodbc.drivers())"
```

## Important

This automation depends on the Green Sheet website structure. If Green Sheet changes its login, results, or export pages, the Playwright selectors in `greensheet_client.py` may need to be updated.