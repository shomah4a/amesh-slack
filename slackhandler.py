import datetime
import json
import urllib.parse
from typing import Dict, Any

import hashlib
import hmac
import time
from typing import Dict, Any


import amesh


AMESH_URL = 'https://tokyo-ame.jwa.or.jp/'
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']


def verify_slack_request(event: Dict[str, Any], signing_secret: str) -> bool:
    slack_signature = event['headers'].get('x-slack-signature', '')
    slack_request_timestamp = event['headers'].get('x-slack-request-timestamp', '')

    if abs(time.time() - int(slack_request_timestamp)) > 60 * 5:
        return False

    sig_basestring = f"v0:{slack_request_timestamp}:{event['body']}"

    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)


def make_response(img: Image.Image, url: str) -> Dict[str, Any]:
    buffered = BytesIO()
    img.save(buffered, format="JPG", optimized=True)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    response = {
        "response_type": "in_channel",
        "blocks": [
            {
                "type": "image",
                "image_url": f"data:image/png;base64,{img_str}",
                "alt_text": "amesh"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": url
                }
            }
        ]
    }
    return response


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    body = event.get('body', '')
    params = dict(urllib.parse.parse_qsl(body))

    if not verify_slack_request(event):
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Invalid request signature'})
        }

    command = params.get('command', '').lstrip('/')
    text = params.get('text', '')

    now = datetime.datetime.now()

    amesh_image = generate_amesh_image(now)

    response_body = make_response(
        amesh_image,
        AMESH_URL
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body)
    }
