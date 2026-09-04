-- schema.sql
-- Educational Analytics Data Pipeline
-- Relational schema derived from the OULAD source files
-- (courses.csv, studentInfo.csv, studentRegistration.csv,
--  assessments.csv, studentAssessment.csv)

DROP TABLE IF EXISTS results CASCADE;
DROP TABLE IF EXISTS assessments CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS courses CASCADE;

-- Courses (modules + presentations)
CREATE TABLE courses (
    code_module                  VARCHAR(10) NOT NULL,
    code_presentation            VARCHAR(10) NOT NULL,
    module_presentation_length   INTEGER,
    PRIMARY KEY (code_module, code_presentation)
);

-- Students (deduplicated demographic record, one row per student)
CREATE TABLE students (
    id_student          INTEGER PRIMARY KEY,
    gender              VARCHAR(10),
    region              VARCHAR(50),
    highest_education   VARCHAR(50),
    imd_band            VARCHAR(20),
    age_band            VARCHAR(20),
    disability          VARCHAR(5)
);

-- Enrollments (one row per student per course presentation)
CREATE TABLE enrollments (
    enrollment_id         SERIAL PRIMARY KEY,
    id_student            INTEGER NOT NULL REFERENCES students(id_student),
    code_module           VARCHAR(10) NOT NULL,
    code_presentation     VARCHAR(10) NOT NULL,
    date_registration     INTEGER,
    date_unregistration   INTEGER,
    num_of_prev_attempts  INTEGER,
    studied_credits       INTEGER,
    final_result          VARCHAR(20),
    FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation),
    UNIQUE (id_student, code_module, code_presentation)
);

-- Assessments (defined per course presentation)
CREATE TABLE assessments (
    id_assessment      INTEGER PRIMARY KEY,
    code_module        VARCHAR(10) NOT NULL,
    code_presentation  VARCHAR(10) NOT NULL,
    assessment_type    VARCHAR(10),
    date               INTEGER,
    weight             NUMERIC(5,2),
    FOREIGN KEY (code_module, code_presentation) REFERENCES courses(code_module, code_presentation)
);

-- Results (individual student scores per assessment)
CREATE TABLE results (
    result_id       SERIAL PRIMARY KEY,
    id_assessment   INTEGER NOT NULL REFERENCES assessments(id_assessment),
    id_student      INTEGER NOT NULL REFERENCES students(id_student),
    date_submitted  INTEGER,
    is_banked       BOOLEAN,
    score           NUMERIC(5,2) CHECK (score >= 0 AND score <= 100),
    UNIQUE (id_assessment, id_student)
);

CREATE INDEX idx_enrollments_student ON enrollments(id_student);
CREATE INDEX idx_enrollments_course ON enrollments(code_module, code_presentation);
CREATE INDEX idx_results_student ON results(id_student);
CREATE INDEX idx_results_assessment ON results(id_assessment);
