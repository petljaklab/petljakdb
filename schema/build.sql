/* build.sql */
/* drop the db, then build the PetljakDB at NYU Langone */
/* Author: Luka Culibrk */


-- Remove later
DROP DATABASE IF EXISTS petljakdb_devel;
CREATE DATABASE petljakdb_devel;

USE petljakdb_devel;

CREATE TABLE studies(
    id INT unsigned NOT NULL AUTO_INCREMENT,
    rname VARCHAR(150),
    study_pmid VARCHAR(150), 
    ncbi_bioproject_id VARCHAR(50),
    PRIMARY KEY (id),
    UNIQUE KEY unique_rname (rname)
);

CREATE TABLE cells(
    id INT unsigned NOT NULL AUTO_INCREMENT,
    rname VARCHAR(150),
    PRIMARY KEY (id),
    UNIQUE KEY unique_rname (rname)
);

CREATE TABLE samples(
    id INT unsigned NOT NULL AUTO_INCREMENT,
    rname VARCHAR(150),
    study_id INT unsigned,
    biosample_id VARCHAR(50),
    treatment VARCHAR(1000),
    sample_parent_id INT unsigned,
    cell_id INT unsigned,
    PRIMARY KEY (id),
    FOREIGN KEY (study_id)
        REFERENCES studies(id),
    FOREIGN KEY (cell_id)
        REFERENCES cells(id),
    FOREIGN KEY (sample_parent_id)
        REFERENCES samples(id),
    UNIQUE KEY unique_rname (rname)
);

CREATE TABLE runs(
    id INT unsigned NOT NULL AUTO_INCREMENT,
    rname VARCHAR(150),
    sample_id INT unsigned NOT NULL,
    study_id INT unsigned NOT NULL,
    source VARCHAR(150) NOT NULL,
    ega_id VARCHAR(20),
    sra_id VARCHAR(20),
    local_path VARCHAR(150),
    PRIMARY KEY (id),
    UNIQUE KEY unique_rname (rname),
    FOREIGN KEY (sample_id)
        REFERENCES samples(id),
    FOREIGN KEY (study_id)
        REFERENCES studies(id)
);

