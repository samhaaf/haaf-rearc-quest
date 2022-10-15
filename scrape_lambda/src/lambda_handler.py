from pull_csvs import pull_csvs
from hit_api import hit_api
from pprint import pprint
from promise import Promise
import boto3
import json


def lambda_handler(event, context):
    """ Runs 'pull_csvs' and 'hit_api' in parallel and returns their responses """

    promise_responses = Promise.for_dict({
        'pull_csvs': Promise(pull_csvs),
        'hit_api':   Promise(hit_api),
    }).get()

    sqs = boto3.client('sqs')
    sqs_response = sqs.send_message(
        QueueUrl='https://sqs.us-east-1.amazonaws.com/029537599011/haaf_rearc_quest_queue',
        MessageBody=json.dumps(promise_responses)
    )

    return {
        'StatusCode': 200,
        'Body': promise_responses
    }


if __name__ == '__main__':
    pprint(lambda_handler(None, None))
