-- analytics.sql
-- Analytical queries against the loaded educational_analytics database.
-- Section A covers the 5 example questions from the Phase 2 Day 2
-- guideline exactly; Section B has additional queries that are also
-- answerable from this schema.

-- =============================================================
-- SECTION A -- the guideline's suggested questions
-- =============================================================

-- A1. How many students are represented?
SELECT COUNT(*) AS total_students FROM students;

-- A2. How many courses are represented?
SELECT COUNT(*) AS total_courses FROM courses;

-- A3. What is the average assessment result? (overall, across everything)
SELECT ROUND(AVG(score), 1) AS overall_average_score FROM results;

-- A4. How do results differ between courses?
SELECT c.code_module, c.code_presentation, ROUND(AVG(r.score), 1) AS avg_score,
       COUNT(DISTINCT r.id_student) AS students_assessed
FROM results r
JOIN assessments a ON a.id_assessment = r.id_assessment
JOIN courses c ON c.code_module = a.code_module AND c.code_presentation = a.code_presentation
GROUP BY c.code_module, c.code_presentation
ORDER BY avg_score DESC;

-- A5. How do results change over time?
-- code_presentation encodes year + start month: B = February start,
-- J = October start (e.g. 2013J = October 2013 presentation), so we
-- can sort chronologically by year then B-before-J.
SELECT c.code_presentation,
       ROUND(AVG(r.score), 1) AS avg_score,
       COUNT(DISTINCT r.id_student) AS students_assessed
FROM results r
JOIN assessments a ON a.id_assessment = r.id_assessment
JOIN courses c ON c.code_module = a.code_module AND c.code_presentation = a.code_presentation
GROUP BY c.code_presentation
ORDER BY
    CAST(SUBSTRING(c.code_presentation, 1, 4) AS INTEGER),
    CASE SUBSTRING(c.code_presentation, 5, 1) WHEN 'B' THEN 1 WHEN 'J' THEN 2 END;

-- =============================================================
-- SECTION B -- additional queries answerable from this schema
-- =============================================================

-- B1. Completion / outcome breakdown by course
SELECT c.code_module, c.code_presentation, e.final_result, COUNT(*) AS num_students
FROM enrollments e
JOIN courses c ON c.code_module = e.code_module AND c.code_presentation = e.code_presentation
GROUP BY c.code_module, c.code_presentation, e.final_result
ORDER BY c.code_module, c.code_presentation, e.final_result;

-- B2. Average assessment score per student
SELECT s.id_student, ROUND(AVG(r.score), 1) AS avg_score, COUNT(r.result_id) AS assessments_taken
FROM students s
JOIN results r ON r.id_student = s.id_student
GROUP BY s.id_student
ORDER BY avg_score DESC;

-- B3. Students who withdrew, with their registration/unregistration days
SELECT s.id_student, e.code_module, e.code_presentation, e.date_registration, e.date_unregistration
FROM enrollments e
JOIN students s ON s.id_student = e.id_student
WHERE e.final_result = 'Withdrawn';

-- B4. Enrollment counts per course presentation
SELECT code_module, code_presentation, COUNT(*) AS enrolled_students
FROM enrollments
GROUP BY code_module, code_presentation
ORDER BY code_module, code_presentation;
