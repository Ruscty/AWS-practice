import os
import json
import boto3
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

#大文字で設定しているものは環境変数(Lambdaで設定すること)
channel_secret = os.getenv('LINE_CHANNEL_SECRET')
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

# ログ確認用(cloudwatchで確認する)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LineBotAPI
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
sqs = boto3.client('sqs')
queue_url = os.getenv('QUEUE_URL')

# Lambda Response
ok_response = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
}
error_response = {
    "isBase64Encoded": False,
    "statusCode": 401,
    "headers": {},
    "body": ""
}

# LINEAPIを使うためのおまじない
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )
    
# メイン
def lambda_handler(event, context):
    try:
        for record in event['Records']:
            record_body = json.loads(record['body'])
            signature = record_body["headers"]["X-Line-Signature"]
            event_body = record_body['body']
        handler.handle(event_body, signature)
    except InvalidSignatureError as e:
        logger.error(e)
        return error_response
    except Exception as e:
        logger.error(e)
        return error_response
    return ok_response