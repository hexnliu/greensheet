CREATE TABLE dbo.GreenSheetProjects
(
    Id BIGINT IDENTITY(1,1) NOT NULL
        PRIMARY KEY,

    GreenSheetId NVARCHAR(100) NOT NULL,

    ProjectName NVARCHAR(500) NULL,
    Address NVARCHAR(500) NULL,
    City NVARCHAR(200) NULL,

    ProjectType NVARCHAR(200) NULL,
    ProjectStatus NVARCHAR(200) NULL,

    EstimatedValue DECIMAL(18,2) NULL,

    OwnerName NVARCHAR(500) NULL,
    ArchitectName NVARCHAR(500) NULL,
    ContractorName NVARCHAR(500) NULL,

    Description NVARCHAR(MAX) NULL,

    ReleaseDate DATE NULL,

    FirstImportedUtc DATETIME2 NOT NULL,
    LastUpdatedUtc DATETIME2 NOT NULL,

    CONSTRAINT UQ_GreenSheetProjects
        UNIQUE (GreenSheetId)
);


CREATE TABLE dbo.GreenSheetPermits
(
    Id BIGINT IDENTITY(1,1) NOT NULL
        PRIMARY KEY,

    PermitNumber NVARCHAR(100) NOT NULL,

    ProjectName NVARCHAR(500) NULL,
    Address NVARCHAR(500) NULL,
    City NVARCHAR(200) NULL,

    PermitType NVARCHAR(200) NULL,
    PermitValue DECIMAL(18,2) NULL,

    Description NVARCHAR(MAX) NULL,

    OwnerName NVARCHAR(500) NULL,
    ContractorName NVARCHAR(500) NULL,

    IssueDate DATE NULL,

    FirstImportedUtc DATETIME2 NOT NULL,
    LastUpdatedUtc DATETIME2 NOT NULL,

    CONSTRAINT UQ_GreenSheetPermits
        UNIQUE (PermitNumber)
);


CREATE TABLE dbo.GreenSheetImportLog
(
    Id BIGINT IDENTITY(1,1) NOT NULL
        PRIMARY KEY,

    StartedUtc DATETIME2 NOT NULL,
    FinishedUtc DATETIME2 NULL,

    ProjectCount INT NULL,
    PermitCount INT NULL,

    Status NVARCHAR(50) NOT NULL,

    ErrorMessage NVARCHAR(MAX) NULL
);