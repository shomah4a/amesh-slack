import base64
import datetime
import json
import os
import urllib.parse
import hashlib
import hmac
import time
from typing import Dict, Any
from io import BytesIO

from PIL import Image

import boto3


import amesh


SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
QUEUE_URL = os.environ['QUEUE_URL']


def verify_slack_request(event, slack_signing_secret=SLACK_SIGNING_SECRET):
    slack_signature = event['headers'].get('x-slack-signature', '')
    slack_request_timestamp = event['headers'].get('x-slack-request-timestamp', '')

    if slack_signing_secret is None:
        slack_signing_secret = os.environ.get('SLACK_SIGNING_SECRET')

    b64decoded_body = base64.decodebytes(event['body'].encode()).decode()

    if not slack_signature or not slack_request_timestamp:
        print("Missing required headers")
        return False

    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        print("Request is too old")
        return False

    sig_basestring = f"v0:{slack_request_timestamp}:{b64decoded_body}"

    print('basestring:', sig_basestring)
    calculated_signature = 'v0=' + hmac.new(
        slack_signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    print(f"Calculated signature: {calculated_signature}")

    if hmac.compare_digest(calculated_signature, slack_signature):
        print("Signature verified successfully")
        return True
    else:
        print("Signature verification failed")
        return False


def put_queue(params: Dict):

    # 非同期処理のためのメッセージをSQSに送信
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps(params)
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    body = base64.decodebytes(event.get('body', '').encode()).decode()
    params = dict(urllib.parse.parse_qsl(body))

    print(json.dumps(event))
    print(params)

    if not verify_slack_request(event):
        print('verify failed')
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Invalid request signature'})
        }

    print('verified')

    response_url = params['response_url']
    user_id = params['user_id']

    put_queue(params)

    payload = {
        "response_type": "ephemeral",
        "text": "",
        "blocks": []
    }

    response = {
        'statusCode': 204,
        'headers': {'Content-Type': 'text/plain'},
        'body': ''
    }

    print(json.dumps(response))

    return response
