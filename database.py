import pyodbc

from config import (
    DB_SERVER,
    DB_DATABASE,
    DB_USERNAME,
    DB_PASSWORD,
)


class Database:

    def __init__(self, logger):

        self.logger = logger
        self.connection = None

    # -----------------------------------------------------
    # Connect
    # -----------------------------------------------------

    def connect(self):

        if DB_USERNAME and DB_PASSWORD:

            connection_string = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                f"UID={DB_USERNAME};"
                f"PWD={DB_PASSWORD};"
                "TrustServerCertificate=yes;"
            )

        else:

            connection_string = (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={DB_SERVER};"
                f"DATABASE={DB_DATABASE};"
                "Trusted_Connection=yes;"
                "TrustServerCertificate=yes;"
            )

        self.connection = pyodbc.connect(
            connection_string
        )

        self.logger.info(
            "Connected to SQL Server."
        )

    # -----------------------------------------------------
    # Project UPSERT
    # -----------------------------------------------------

    def upsert_project(self, project):

        sql = """
        MERGE GreenSheetProjects AS target

        USING
        (
            SELECT ? AS GreenSheetId
        ) AS source

        ON target.GreenSheetId =
           source.GreenSheetId

        WHEN MATCHED THEN

            UPDATE SET

                ProjectName = ?,
                Address = ?,
                City = ?,
                ProjectType = ?,
                ProjectStatus = ?,
                EstimatedValue = ?,
                OwnerName = ?,
                ArchitectName = ?,
                ContractorName = ?,
                Description = ?,
                ReleaseDate = ?,
                LastUpdatedUtc =
                    SYSUTCDATETIME()

        WHEN NOT MATCHED THEN

            INSERT
            (
                GreenSheetId,
                ProjectName,
                Address,
                City,
                ProjectType,
                ProjectStatus,
                EstimatedValue,
                OwnerName,
                ArchitectName,
                ContractorName,
                Description,
                ReleaseDate,
                FirstImportedUtc,
                LastUpdatedUtc
            )

            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            );
        """

        cursor = self.connection.cursor()

        cursor.execute(
            sql,

            # Match
            project["greensheet_id"],

            # Update
            project["project_name"],
            project["address"],
            project["city"],
            project["project_type"],
            project["project_status"],
            project["estimated_value"],
            project["owner_name"],
            project["architect_name"],
            project["contractor_name"],
            project["description"],
            project["release_date"],

            # Insert
            project["greensheet_id"],
            project["project_name"],
            project["address"],
            project["city"],
            project["project_type"],
            project["project_status"],
            project["estimated_value"],
            project["owner_name"],
            project["architect_name"],
            project["contractor_name"],
            project["description"],
            project["release_date"],
        )

    # -----------------------------------------------------
    # Permit UPSERT
    # -----------------------------------------------------

    def upsert_permit(self, permit):

        sql = """
        MERGE GreenSheetPermits AS target

        USING
        (
            SELECT ? AS PermitNumber
        ) AS source

        ON target.PermitNumber =
           source.PermitNumber

        WHEN MATCHED THEN

            UPDATE SET

                ProjectName = ?,
                Address = ?,
                City = ?,
                PermitType = ?,
                PermitValue = ?,
                Description = ?,
                OwnerName = ?,
                ContractorName = ?,
                IssueDate = ?,
                LastUpdatedUtc =
                    SYSUTCDATETIME()

        WHEN NOT MATCHED THEN

            INSERT
            (
                PermitNumber,
                ProjectName,
                Address,
                City,
                PermitType,
                PermitValue,
                Description,
                OwnerName,
                ContractorName,
                IssueDate,
                FirstImportedUtc,
                LastUpdatedUtc
            )

            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                SYSUTCDATETIME(),
                SYSUTCDATETIME()
            );
        """

        cursor = self.connection.cursor()

        cursor.execute(
            sql,

            # Match
            permit["permit_number"],

            # Update
            permit["project_name"],
            permit["address"],
            permit["city"],
            permit["permit_type"],
            permit["permit_value"],
            permit["description"],
            permit["owner_name"],
            permit["contractor_name"],
            permit["issue_date"],

            # Insert
            permit["permit_number"],
            permit["project_name"],
            permit["address"],
            permit["city"],
            permit["permit_type"],
            permit["permit_value"],
            permit["description"],
            permit["owner_name"],
            permit["contractor_name"],
            permit["issue_date"],
        )

    # -----------------------------------------------------
    # Commit
    # -----------------------------------------------------

    def commit(self):

        self.connection.commit()

    # -----------------------------------------------------
    # Close
    # -----------------------------------------------------

    def close(self):

        if self.connection:

            self.connection.close()

            self.logger.info(
                "SQL connection closed."
            )