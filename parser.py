import pandas as pd
from pathlib import Path
from io import StringIO
DOWNLOAD_DIR = Path(__file__).parent / "downloads"
def clean_column_names(df):

    df.columns = (
        df.columns
        .map(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]+", "_", regex=True)
        .str.strip("_")
    )

    return df


def clean_money(value):

    if pd.isna(value):
        return None

    text = str(value)

    text = (
        text
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


# ---------------------------------------------------------
# Projects
# ---------------------------------------------------------
def read_greensheet_file(filename):

    filename = Path(filename)

    with open(filename, "rb") as f:
        header = f.read(4096)

    # Real XLSX
    if header.startswith(b"PK"):
        return pd.read_excel(
            filename,
            engine="openpyxl",
        )

    # Real old-style XLS
    if header.startswith(
        b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    ):
        return pd.read_excel(
            filename,
            engine="xlrd",
        )

    # Green Sheet HTML disguised as Excel
    text = header.decode(
        "utf-8",
        errors="ignore",
    ).lower()

    if (
        "<html" in text
        or "<table" in text
        or "<!doctype" in text
    ):

        tables = pd.read_html(
            filename
        )

        if not tables:
            raise ValueError(
                "Green Sheet returned HTML "
                "but no table was found."
            )

        df = tables[0]

        #
        # Green Sheet export structure:
        #
        # Row 0 = issue/search title
        # Row 1/2 = metadata
        # Row 3 = REAL COLUMN HEADERS
        # Row 4+ = data
        #
        if len(df) < 4:
            raise ValueError(
                "Green Sheet export does not "
                "contain the expected header rows."
            )

        df.columns = df.iloc[3]

        df = (
            df.iloc[4:]
            .reset_index(drop=True)
        )

        return df

    # Normal CSV fallback
    try:
        return pd.read_csv(
            filename,
            encoding="utf-8-sig",
        )

    except UnicodeDecodeError:
        return pd.read_csv(
            filename,
            encoding="latin1",
        )

def normalize_projects(filename):
    """
    Read and normalize the Green Sheet Projects export.
    """

    df = read_greensheet_file(filename)   

    df = clean_column_names(df)    

    # --------------------------------------------------
    # Make sure we're dealing with real project records
    # --------------------------------------------------

    if "ref" not in df.columns:
        raise ValueError(
            "Projects export does not contain "
            "the expected 'ref' column. "
            f"Columns: {df.columns.tolist()}"
        )

    # Remove completely empty rows
    df = df.dropna(how="all").copy()

    # Ref # identifies a real Green Sheet project.
    # Convert to numeric so garbage/footer rows become NaN.
    df["ref"] = pd.to_numeric(
        df["ref"],
        errors="coerce",
    )

    df = df[
        df["ref"].notna()
    ].copy()

    # Store project reference as integer
    df["ref"] = df["ref"].astype("Int64")

    # --------------------------------------------------
    # Dates
    # --------------------------------------------------

    for column in [
        "first_report",
        "interm_report",
        "last_report",
    ]:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------
    # Numeric fields
    # --------------------------------------------------

    for column in [
        "project_latitude",
        "project_longitude",
        "units",
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------
    # Clean text
    # --------------------------------------------------

    text_columns = [
        "city",
        "project_address",
        "project_type",
        "project_description",
        "project",
        "project_status",
        "status",
        "applicant",
        "architect",
        "developer",
        "general_contr",
        "owner",
        "website",
        "notes",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    print(
        f"Normalized Projects: {len(df)}"
    )

    return df

# ---------------------------------------------------------
# Permits
# ---------------------------------------------------------

def normalize_permits(filename):
    """
    Read and normalize the Green Sheet Building Permits export.
    """

    df = read_greensheet_file(filename)    

    df = clean_column_names(df) 

    # --------------------------------------------------
    # Verify expected columns
    # --------------------------------------------------

    required = [
        "issue_date",
        "region",
        "project_address",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Permit export is missing expected "
            f"columns: {missing}. "
            f"Columns: {df.columns.tolist()}"
        )

    # Remove completely empty rows
    df = df.dropna(how="all").copy()

    # --------------------------------------------------
    # Dates
    # --------------------------------------------------

    df["issue_date"] = pd.to_datetime(
        df["issue_date"],
        errors="coerce",
    )

    # A real permit should have an issue date
    df = df[
        df["issue_date"].notna()
    ].copy()

    # --------------------------------------------------
    # Numeric fields
    # --------------------------------------------------

    for column in [
        "project_latitude",
        "project_longitude",
        "amount",
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # --------------------------------------------------
    # Clean text fields
    # --------------------------------------------------

    text_columns = [
        "region",
        "owner",
        "owner_address",
        "owner_city",
        "owner_postal_code",
        "owner_phone_number",
        "owner_email",
        "project_address",
        "project_type",
        "project_details",
        "contractor",
        "contractor_address",
        "contractor_city",
        "contractor_postal_code",
        "contractor_phone_number",
        "contractor_email",
        "notes",
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    print(
        f"Normalized Permits: {len(df)}"
    )

    return df
