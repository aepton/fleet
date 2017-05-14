import boto3
import json
import os

def resubmit_message(sqs_client, queue_url, payload, receipt_handle):
    sqs_client.delete_message(
        QueueUrl=queue_url, ReceiptHandle=receipt_handle)
    sqs_client.send_message(
        QueueUrl=queue_url,
        MessageGroupId=payload['group_id'],
        MessageBody=json.dumps(payload))

def fetch_and_save_sqs_message():
    sqs_client = boto3.client(
        'sqs',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

    found = False
    job = None
    for queue in ['campfin', 'personal']:
        seen_messages = set()
        queue_url = '%s/%s.fifo' % (os.environ.get('AWS_SQS_QUEUE_PREFIX'), queue)

        while not Found:
            response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

            if not response or not response['Messages']:
                break
            if response['Messages'][0]['MessageId'] in seen_messages:
                break

            seen_messages.add(response['Messages'][0]['MessageId'])

            payload = json.loads(response['Messages'][0]['Body'])
            if payload['instance'] == os.environ.get('INSTANCE_ID'):
                if payload['status'] != 'unclaimed':
                    resubmit_message(
                        sqs_client, queue_url, payload, response['Messages'][0]['ReceiptHandle'])

                job = payload['job_name']
                payload['status'] = 'in process'

                found = True
                sqs_client.send_message(
                    QueueUrl=job['queue'],
                    MessageGroupId=job['group_id'],
                    MessageBody=json.dumps(job))
                break
            else:
                resubmit_message(
                    sqs_client, queue_url, payload, response['Messages'][0]['ReceiptHandle'])

    if found and job:
        pass
        # write job to /etc/current_job

if __name__ == '__main__':
    fetch_and_save_sqs_message()
