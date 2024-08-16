import traceback
import base64
import datetime
import json
import os
import urllib.parse
import hashlib
import hmac
import time
import logging
from typing import Dict, Any
import io

from PIL import Image

import requests
import slack_sdk

import tempfile


import amesh

logger = logging.getLogger()
logger.setLevel(logging.INFO)


AMESH_URL = 'https://tokyo-ame.jwa.or.jp/'
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

def upload_image(filepath, channel_id):

    client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)

    result = client.files_upload_v2(
        channel=channel_id,
        file=filepath,
        title="amesh",
        filename="amesh.png",
        initial_comment=AMESH_URL
    )


def lambda_handler(event, context):

    now = datetime.datetime.now()
    amesh_image = amesh.generate_amesh_image(now)

    for record in event['Records']:

        try:
            body = json.loads(record['body'])
            print(body)
            response_url = body['response_url']
            user_id = body['user_id']

            with tempfile.NamedTemporaryFile(suffix='.png') as fp:
                amesh_image.save(fp.name, format='PNG')
                upload_image(fp.name, body['channel_id'])

        except Exception as e:
            traceback.print_exception(e)
