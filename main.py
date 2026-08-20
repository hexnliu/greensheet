import csv
import json
import sys

from datetime import datetime
from pathlib import Path

from config import validate_config

from logger import create_logger

from greensheet_client import (
    GreenSheetClient,
)

from database import Database

from parser import (
    normalize_projects,
    normalize_permits,
)


DOWNLOAD_DIR = (
    Path(__file__).resolve().parent
    / "downloads"
)


def print_records(title, records):
    """
    Print normalized records in a readable format.
    """

    print()
    print("=" * 80)
    print(title)
    print("=" * 80)

    if not records:
        print("No records found.")
        return

    for index, record in enumerate(
        records,
        start=1
    ):

        print()
        print(f"Record #{index}")
        print("-" * 80)

        print(
            json.dumps(
                record,
                indent=4,
                default=str,
                ensure_ascii=False
            )
        )

    print()
    print(f"Total: {len(records)}")
    print("=" * 80)


def save_records_to_csv(records, filename):
    """
    Save a Pandas DataFrame to a real CSV file.
    """

    filename.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if records is None or records.empty:
        return

    records.to_csv(
        filename,
        index=False,
        encoding="utf-8-sig"
    )

def main():

    print(
        "Green Sheet importer starting..."
    )    

    logger = create_logger()

    client = None
    database = None

    try:

        # ---------------------------------------------
        # Validate configuration
        # ---------------------------------------------

        validate_config()

        logger.info(
            "======================================"
        )

        logger.info(
            "Starting Green Sheet weekly import"
        )

        # ---------------------------------------------
        # Start browser
        # ---------------------------------------------

        client = GreenSheetClient(
            logger
        )

        client.start()

        # ---------------------------------------------
        # Login
        # ---------------------------------------------

        logger.info(
            "Logging into Green Sheet..."
        )

        client.login()

        # ---------------------------------------------
        # Download projects
        # ---------------------------------------------

        logger.info(
            "Fetching Projects..."
        )

        project_file = (
            client.download_projects()
        )

        # ---------------------------------------------
        # Download permits
        # ---------------------------------------------

        logger.info(
            "Fetching Building Permits..."
        )

        permit_file = (
            client.download_permits()
        )

        # ---------------------------------------------
        # Normalize Projects
        # ---------------------------------------------

        logger.info(
            "Normalizing Projects..."
        )

        projects = normalize_projects(
            project_file
        )

        logger.info(
            "Projects found: %s",
            len(projects)
        )

        # ---------------------------------------------
        # Normalize Permits
        # ---------------------------------------------

        logger.info(
            "Normalizing Permits..."
        )

        permits = normalize_permits(
            permit_file
        )

        logger.info(
            "Permits found: %s",
            len(permits)
        )

        # ---------------------------------------------
        # Create real CSV files
        # ---------------------------------------------

        timestamp = (
            datetime.now()
            .strftime("%Y%m%d-%H%M%S")
        )

        project_csv = (
            DOWNLOAD_DIR
            / f"projects-{timestamp}.csv"
        )

        permit_csv = (
            DOWNLOAD_DIR
            / f"permits-{timestamp}.csv"
        )

        logger.info(
            "Creating Projects CSV..."
        )

        save_records_to_csv(
            projects,
            project_csv
        )

        logger.info(
            "Projects CSV saved to %s",
            project_csv
        )

        logger.info(
            "Creating Permits CSV..."
        )

        save_records_to_csv(
            permits,
            permit_csv
        )

        logger.info(
            "Permits CSV saved to %s",
            permit_csv
        )

        # ---------------------------------------------
        # Database
        # ---------------------------------------------

        database = Database(
            logger
        )

        database.connect()

        # ---------------------------------------------
        # UPSERT Projects
        # ---------------------------------------------

        logger.info(
            "Saving Projects..."
        )

        for project in projects:

            database.upsert_project(
                project
            )

        # ---------------------------------------------
        # UPSERT Permits
        # ---------------------------------------------

        logger.info(
            "Saving Permits..."
        )

        for permit in permits:

            database.upsert_permit(
                permit
            )

        database.commit()

        # ---------------------------------------------
        # Done
        # ---------------------------------------------

        logger.info(
            "======================================"
        )

        logger.info(
            "Green Sheet import completed."
        )

        logger.info(
            "Projects processed: %s",
            len(projects)
        )

        logger.info(
            "Permits processed: %s",
            len(permits)
        )

        logger.info(
            "Projects CSV: %s",
            project_csv
        )

        logger.info(
            "Permits CSV: %s",
            permit_csv
        )

        logger.info(
            "======================================"
        )

    except Exception as ex:

        logger.exception(
            "Green Sheet import FAILED: %s",
            ex
        )

        return 1

    finally:

        if database:
            database.close()

        if client:
            client.close()

    return 0


if __name__ == "__main__":

    sys.exit(
        main()
    )