from utils import catch_as_reject, get_environ
import json
import requests
from bs4 import BeautifulSoup as Soup
from pprint import pprint
from datetime import datetime
import re
import boto3
import botocore 


@catch_as_reject
def pull_csvs(resolve, reject):
    """ This reaches out to the url defined in env.env and writes the files listed there to s3 """

    source_url = get_environ('CSV_URL')
    s3_bucket_name = get_environ('S3_BUCKET')
    
    # Scrape server HTML response
    with requests.get(f'https://{source_url}') as response:
        response.raise_for_status()
        soup = Soup(response.text, "html.parser")
    elements = [_ for _ in soup.find('pre').children][3:]
    
    # Extract available files
    file_names = [e.text for e in elements[1:-1:3]]
    #file_hrefs = [e['href'] for e in elements[1:-1:3]]
    file_times = [re.match('.+(AM|PM)', e.text).group().strip() for e in elements[0:-1:3]]

    # Get objects in the s3 bucket
    s3_bucket = boto3.resource('s3').Bucket(s3_bucket_name)
    s3_objects = s3_bucket.objects.filter(Prefix=source_url)
    s3_keys = [o.key for o in s3_objects]
    s3_filenames = [k.split('/')[-1] for k in s3_keys]
    
    # Get a list of source server times from s3
    #     Note: done this way because we don't know the timezone on the source server
    try:
        source_times = json.loads(
            s3_bucket.Object(source_url + '.source_times.json').get()['Body'].read().decode('utf-8')
        )
    except botocore.exceptions.ClientError as e:
        source_times = {}

    # Iterate over each file on the server
    failed = []
    updated = []
    for _name, _time in zip(file_names, file_times):
        
        # Check to see if the file needs to be downloaded
        download = True
        for s3o in s3_objects:
            s3_name = s3o.key.split('/')[-1]
            if _name != s3_name:
                continue
            if _time == source_times.get(_name):
                download = False
            break

        # Download the file from the server
        if download:
            try:
                with requests.get(f'https://{source_url}{_name}', stream=True) as response:
                    response.raise_for_status()
                    # TODO: stream with firehose to handle arbitrary file size
                    s3_bucket.Object(source_url + _name).put(Body=response.text)
                updated.append(_name)
                source_times[_name] = _time

                # Put updated source times
                s3_bucket.Object(source_url + '.source_times.json').put(
                    Body=json.dumps(source_times)
                )
            except ValueError:
                raise
            except:
                print('ERROR: failed to pull file: ' + _name)
                raise
                failed.append([_name, _href])

    resolve({
        'updated_files': updated,
        'failed_files' : failed
    })


if __name__ == '__main__':
    pull_csvs(lambda _: pprint(_), lambda _: pprint(_))

