import json
import uuid

def resubmit_message(sqs_client, queue_url, payload, receipt_handle):
    sqs_client.delete_message(
        QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageGroupId=payload['group_id'],
        MessageBody=json.dumps(payload),
        MessageDeduplicationId=str(uuid.uuid4()))