import logging
import os
import urllib.request, urllib.parse
import json
import base64
import hashlib
import hmac
import boto3

# AWSのSQSサービスを指定
sqs = boto3.client('sqs')
# 対象のSQSのURLを記載
queue_url = os.getenv('QUEUE_URL')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# グローバル変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']

# メイン
def lambda_handler(request, context):
    #署名検証を実施
    if not validateReq(request) :
        logger.info("LINE 以外からのアクセス")
        return {'statusCode': 405, 'body': '{}'}
    
    #リクエストの内容をSQSに飛ばす 
    bot_job_enqueue(sqs,os.getenv('QUEUE_URL'), request)

    return {'statusCode': 200, 'body': '{}'}
    
# 署名の検証
def validateReq(request):
    # 検証結果
    validateResult = False

    try:
        # Request情報取得
        body = request['body']
        header = request['headers']

        # リクエストBodyのハッシュ化(SHA256)
        hash = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'),
        body.encode('utf-8'), hashlib.sha256).digest()

        # エンコーディング(base64)
        signature = base64.b64encode(hash).decode('utf-8')
        # .decode('utf-8')は文字列で照合するためいったんデコードしている。

        # 署名検証
        if signature == header['X-Line-Signature'] :
            validateResult = True
            logger.info('検証成功')
        # 検証用(おそらくバグ)
        # if signature == header['x-line-signature'] :
        #     validateResult = True
            

    except:
        logger.info('検証失敗')
        validateResult = False
    finally:
        return validateResult


# SQSにメッセージを送信
def bot_job_enqueue(sqs_client,target_queue_url, message_body):
    json_str = json.dumps(message_body)
    logger.info(json_str)
    
    sqs_client.send_message(
            QueueUrl=target_queue_url,
            MessageBody=json_str
        )


