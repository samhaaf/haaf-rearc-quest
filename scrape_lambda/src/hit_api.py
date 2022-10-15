from utils import catch_as_reject, get_environ
import json
import requests
from pprint import pprint
import os
import boto3


@catch_as_reject
def hit_api(resolve, reject):
    """ This reaches out to the url defined in env.env and pulls the JSON blob returned there """

    api_url = get_environ('API_URL')
    s3_bucket_name = get_environ('S3_BUCKET')

    # Hit API
    with requests.get(f'https://{api_url}') as response:
        response.raise_for_status()
        payload = response.json()
    
    # Update s3 bucket
    s3_bucket = boto3.resource('s3').Bucket(s3_bucket_name)
    s3_objects = s3_bucket.Object('api_response.json').put(Body=json.dumps(payload))
    
    resolve({
        'file_updated': True,
    })


if __name__ == '__main__':
    hit_api(lambda _: pprint(_), lambda _: pprint(_))

