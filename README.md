# MariaDB Database Documentation: `petljakdb`
Author: [Luka Culibrk](github.com/lculibrk)
## Overview
This document describes the structure of the `petljakdb` MariaDB database. It includes details about tables, columns, relationships, constraints, and indexes.

---

## Tables Overview
The database contains the following tables:
1. `analyses`
2. `cells`
3. `patients`
4. `runs`
5. `samples`
6. `studies`

---

## Table Details

### 1. `analyses`
- **Description**: Stores information about various analyses.
- **Columns**:
  - `id` (int unsigned, Primary Key): Unique auto-assigned numeric identifier for each analysis.
  - `pipeline_name` (varchar(20)): Name of the pipeline used.
  - `pipeline_version` (varchar(20)): Version of the pipeline.
  - `analysis_type` (varchar(20)): Type of analysis.
  - `input_table` (enum): Source table (`studies`, `samples`, or `runs`).
  - `studies_id` (int unsigned, Foreign Key): Linked to `studies.id`.
  - `samples_id` (int unsigned, Foreign Key): Linked to `samples.id`.
  - `runs_id` (int unsigned, Foreign Key): Linked to `runs.id`.
  - `cells_id` (int): Linked to cell information.
  - `analysis_time` (datetime): Timestamp of the analysis.
  - `analysis_dir` (varchar(250)): Directory for the analysis output.
  - `analysis_complete` (enum): Status of analysis (`True` for complete or `False` for ongoing). Currently not strictly enforced.
  - `reference_genome` (varchar(255)): Reference genome used.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - Foreign Key Indexes: `studies_id`, `samples_id`, `runs_id`
- **Foreign Keys**:
  - `studies_id` → `studies.id`
  - `samples_id` → `samples.id`
  - `runs_id` → `runs.id`

---

### 2. `cells`
- **Description**: Contains information about cells.
- **Columns**:
  - `id` (int unsigned, Primary Key): Unique identifier for each cell.
  - `rname` (varchar(150), Unique): Unique cell name.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - `UNIQUE`: `rname`

---

### 3. `patients`
- **Description**: Stores patient-related data.
- **Columns**:
  - `id` (int, Primary Key): Unique identifier for each patient.
  - `rname` (varchar(255), Unique): Unique patient name.
  - `germline_sample` (int unsigned, Foreign Key): Linked to `samples.id`. Refers to the single authoratative germline sample for the patient. 
  - `study_id` (int unsigned, Foreign Key): Linked to `studies.id`.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - `UNIQUE`: `rname`
  - Foreign Key Indexes: `germline_sample`, `study_id`
- **Foreign Keys**:
  - `germline_sample` → `samples.id` (ON DELETE SET NULL)
  - `study_id` → `studies.id` (ON DELETE SET NULL)

---

### 4. `runs`
- **Description**: Stores details about sequencing runs.
- **Columns**:
  - `id` (int unsigned, Primary Key): Unique identifier for each run.
  - `rname` (varchar(150), Unique): Unique run name.
  - `sample_id` (int unsigned, Foreign Key): Linked to `samples.id`.
  - `study_id` (int unsigned, Foreign Key): Linked to `studies.id`.
  - `source` (varchar(150)): Source of the sequencing data (ERA, SRA, local, etc).
  - `ega_id` (varchar(20)): EGA ID, if applicable.
  - `sra_id` (varchar(20)): SRA ID, if applicable.
  - `local_path` (varchar(150)): Path to local data, if applicable. Deprecated.
  - `sequencing_strategy` (varchar(50)): Sequencing strategy used, such as WGS, WXS, RNA.
  - `fastq_path` (varchar(500)): Path to FASTQ files.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - `UNIQUE`: `rname`
  - Foreign Key Indexes: `sample_id`, `study_id`
- **Foreign Keys**:
  - `sample_id` → `samples.id`
  - `study_id` → `studies.id`

---

### 5. `samples`
- **Description**: Contains sample-related data.
- **Columns**:
  - `id` (int unsigned, Primary Key): Unique identifier for each sample.
  - `rname` (varchar(150), Unique): Unique sample name.
  - `study_id` (int unsigned, Foreign Key): Linked to `studies.id`.
  - `biosample_id` (varchar(50)): Biosample identifier.
  - `treatment` (varchar(1000)): Treatment or relevant genotype details.
  - `sample_parent_id` (int unsigned, Foreign Key): Linked to `samples.id`.
  - `cell_id` (int unsigned, Foreign Key): Linked to `cells.id`.
  - `culture_days` (int unsigned): Number of culture days for cell line models.
  - `patient_id` (int, Foreign Key): Linked to `patients.id` for patient data.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - `UNIQUE`: `rname`
  - Foreign Key Indexes: `study_id`, `cell_id`, `sample_parent_id`, `patient_id`
- **Foreign Keys**:
  - `study_id` → `studies.id`
  - `cell_id` → `cells.id`
  - `sample_parent_id` → `samples.id`
  - `patient_id` → `patients.id` (ON DELETE SET NULL)

---

### 6. `studies`
- **Description**: Stores information about studies.
- **Columns**:
  - `id` (int unsigned, Primary Key): Unique identifier for each study.
  - `rname` (varchar(150), Unique): Unique study name.
  - `study_pmid` (varchar(150)): PubMed ID for the study.
  - `ncbi_bioproject_id` (varchar(50)): NCBI BioProject ID.
- **Indexes**:
  - `PRIMARY KEY`: `id`
  - `UNIQUE`: `rname`

---

## Relationships Overview
- **`analyses`** references `studies`, `samples`, and `runs`.
- **`patients`** references `samples` and `studies`.
- **`runs`** references `samples` and `studies`.
- **`samples`** references `studies`, `cells`, and `patients`.
- **`studies`** serves as a foundational table referenced by other tables.

---


---

## Usage information

### Introduction

![ERD](ERD.png)

Above you will find an [ERD](https://en.wikipedia.org/wiki/Entity%E2%80%93relationship_model) describing the tables in the database. Below is a description of keys that may not be immediately obvious:

| key | description |
|-|-|
| id | numeric identifier for the table, always unique |
| rname | name for the entity, always unique |
| runs.source | describes where the data came from: SRA, EGA, or were we given the raw data? |

### Getting started using the DB

Note that the following must be done on BigPurple/Ultraviolet at NYULH. 

The database can be queried via [mySQL/mariaDB syntax](https://www.javatpoint.com/mariadb-syntax). First you will need a DB account, created by Luka. Once that's set up, the easiest way to authenticate is to create a file `.my.cnf` in your home directory, structured accordingly, replace the text in {} with your own:

```
[client]
user={your_username}
password={your_password}
port=33100
host=db
default-character-set=utf8mb3
```

### Enter the CLI interface:
```
module load mariadb
mysql petljakdb
```

### Some example queries:
Select all the samples from study with ID my_id:

```
SELECT * FROM studies WHERE study_id={my_id};
```

Path to all the raw alignment data for a given study:
```
SELECT id,analysis_dir FROM analyses WHERE study_id={my_id} AND analysis_name="GATK_BAM";
```

Path to all the mutation calls for JSC-1 cells, regardless of study:

```
SELECT * FROM samples INNER JOIN analyses ON analyses.samples_id=samples.id WHERE pipeline_name="MUTECT_CELLLINE" AND cell_id=(SELECT id FROM cells WHERE rname="JSC-1");
```

There are a lot of arcane things you can do with SQL to do increasingly complex queries. See [mySQL/SQL/mariaDB](https://www.javatpoint.com/mariadb-syntax) documentation for more information.

