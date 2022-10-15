from utils import get_environ
import boto3
import json
import pandas as pd
from pandasql import sqldf
from io import StringIO


def lambda_handler(event, context):
    s3_bucket_name = get_environ('S3_BUCKET')

    ### Part 3.0 - Load files from S3
    s3_bucket = boto3.resource('s3').Bucket(s3_bucket_name)

    csv_df = pd.read_csv(
        's3://haaf-rearc-quest/download.bls.gov/pub/time.series/pr/pr.data.1.AllData', 
        delimiter='\t'
    )
    api_df = pd.DataFrame.from_records(
        json.loads(s3_bucket.Object('api_response.json')
            .get()['Body'].read().decode('utf-8'))['data'])

    # clean
    csv_df.columns = [col.strip() for col in csv_df.columns]
    api_df.columns = [col.strip() for col in api_df.columns]
    api_df.Year = api_df.Year.astype(int)
    api_df.Population = api_df.Population.astype(int)
    csv_df['series_id'] = csv_df.series_id.apply(lambda x: x.strip())
    csv_df['period'] = csv_df.period.apply(lambda x: x.strip())

    print(csv_df)
    print(api_df)

    ### Part 3.1 - Mean and STD of api_df
    print('Mean:', round(api_df.Population[(2013 <= api_df.Year) & (api_df.Year <= 2018)].mean(), 1))
    print('STD: ', round(api_df.Population[(2013 <= api_df.Year) & (api_df.Year <= 2018)].std(), 1))

    ### Part 3.2 - Best year for each series_id
    print('Best year for each series_id:')
    # This query isn't working on every platform -- some software thing I can't resolve
#    print(sqldf("""
#        SELECT series_id, year, total_value as value 
#        FROM (
#            SELECT series_id, year, total_value 
#                , ROW_NUMBER() OVER (PARTITION BY _."series_id" ORDER BY _."total_value" DESC) rn
#            FROM (
#                SELECT series_id, year, SUM(value) as total_value
#                FROM csv_df
#                GROUP BY series_id, year
#            ) _
#        ) __
#        WHERE rn = 1
#        ORDER BY series_id ASC
#    """).to_string())

    # So here's an inefficient version without a PARTITION BY clause
    print(sqldf("""
        select series_id, year
        from (
            SELECT l.series_id, r.year --, r.total_value as value
            FROM (
                SELECT series_id, max(total_value) as max_value
                FROM (
                    SELECT series_id, year, SUM(value) as total_value
                    FROM csv_df
                    GROUP BY series_id, year
                )
                GROUP BY series_id
            ) l 
            LEFT JOIN (
                SELECT series_id, year, SUM(value) as total_value
                FROM csv_df
                GROUP BY series_id, year
            ) r
            ON l.series_id = r.series_id AND l.max_value = r.total_value
            order by r.year desc
        ) 
        group by series_id
        order by series_id asc
    """).to_string())

    ### Part 3.3 - Value for given year
    series_id = 'PRS30006032'
    period = 'Q01'

    print('Value for given year and quarter:')
    print(sqldf(f"""
        SELECT series_id, c.year, period, value, population
        FROM api_df a
        LEFT JOIN csv_df c
        ON c.year = a.Year
        WHERE c.series_id = '{series_id}'
          AND c.period = '{period}'
    """).to_string())

    return {
        'StatusCode': 200
    }


if __name__ == '__main__':
    print(lambda_handler(None, None))
