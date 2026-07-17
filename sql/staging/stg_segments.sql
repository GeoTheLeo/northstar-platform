CREATE OR REPLACE TABLE northstar.segments AS

SELECT *

FROM read_csv_auto(
    'data/raw/learner_segmentation_data.csv'
);