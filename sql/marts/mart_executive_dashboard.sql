CREATE OR REPLACE VIEW
northstar.executive_dashboard
AS

SELECT

    COUNT(*) AS total_students,

    AVG(attendance)
        AS avg_attendance,

    AVG(assessment_score)
        AS avg_assessment_score,

    AVG(engagement_score)
        AS avg_engagement,

    SUM(
        CASE

            WHEN attendance < 70

            THEN 1

            ELSE 0

        END

    ) AS at_risk_students

FROM northstar.learners;