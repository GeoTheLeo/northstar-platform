CREATE OR REPLACE TABLE northstar.learners AS

SELECT *

FROM read_csv_auto(
    'data/raw/student_data.csv'
);