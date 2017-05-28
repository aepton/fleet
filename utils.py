import boto3
import calendar
import json
import os
import time
import uuid

from StringIO import StringIO

JOBFILE_PATH = '/tmp/current_job'
S3_BUCKET = 'status.epton.org'

def write_to_s3(
    s3_path, local_path=None, contents=None, bucket=S3_BUCKET, content_type='text/html'):
  session = boto3.Session(profile_name='abe')
  s3 = session.resource('s3')
  if local_path:
    source = open(local_path, 'rb')
  else:
    source = StringIO(contents)

  key = s3.Object(bucket, s3_path)
  key.put(Body=source, ContentType=content_type)
  key.Acl().put(ACL='public-read')

def load_from_s3_base(s3_path, bucket, encoding):
  session = boto3.Session(profile_name='abe')
  s3 = session.resource('s3')
  obj = s3.Object(bucket, s3_path)
  return obj.get()

def load_from_s3(s3_path, bucket=S3_BUCKET, encoding='utf-8'):
  return load_from_s3_base(s3_path, bucket, encoding)['Body'].read()

def store_job_status_in_dynamodb(settings):
  table = get_dynamodb_table('status-job')
  table = set_dynamodb_throughput(table, 'WriteCapacityUnits', 1)

  if settings['status'] == 'pending':
    settings['created'] = calendar.timegm(time.gmtime())

  table.put_item(Item=settings)

  table = set_dynamodb_throughput(table, 'WriteCapacityUnits', 1)

def fetch_job_from_dynamodb(job_id):
  table = get_dynamodb_table('status-job')
  table = set_dynamodb_throughput(table, 'ReadCapacityUnits', 1)

  return table.get_item(Key={'jobId': job_id})['Item']

def get_dynamodb_table(table_name):
  session = boto3.Session(profile_name='abe')
  dynamodb = session.resource('dynamodb')
  return dynamodb.Table(table_name)

def set_dynamodb_throughput(table, operation, capacity):
  read_operation = 'ReadCapacityUnits'
  write_operation = 'WriteCapacityUnits'

  if table.provisioned_throughput[operation] != capacity:
    throughput = {operation: capacity}

    # Leave the property we didn't intend to modify unmodified
    if operation == read_operation:
      throughput[write_operation] = table.provisioned_throughput[write_operation]
    else:
      throughput[read_operation] = table.provisioned_throughput[read_operation]

    try:
      table = table.update(ProvisionedThroughput=throughput)
    except Exception, e:
      print 'Error updating throughput: %s' % e

  return table

def job_matches_settings(job, settings):
  for key in settings:
    if key not in job or job[key] != settings[key]:
      return False
  return True

def get_most_recent_jobs(num_jobs=10, settings=None):
  table = get_dynamodb_table('status-job')
  #table = set_dynamodb_throughput(table, 'ReadCapacityUnits', num_jobs)

  results = table.scan()['Items']
  if settings:
    results = [job for job in results if job_matches_settings(job, settings)]
  results = sorted(results)[:num_jobs]

  #set_dynamodb_throughput(table, 'ReadCapacityUnits', 1)

  return results

def publish_job_dashboard():
  jobs = []
  for job in get_most_recent_jobs(20):
    job['created'] = float(job['created'])
    if 'completed' in job:
      job['completed'] = float(job['completed'])
    jobs.append(job)

  write_to_s3('jobs.json', contents=json.dumps({'jobs': jobs}), content_type='application/json')

def fetch_and_save_dynamodb_job():
  try:
    job = get_most_recent_jobs(1, {'status': 'pending'})[0]
    job['status'] = 'in process'
    store_job_status_in_dynamodb(job)
  except:
    pass

  try:
    with open(JOBFILE_PATH, 'w+') as fh:
      fh.write(','.join([job['jobName'], job['jobId']]))
  except:
      os.remove(JOBFILE_PATH)

  publish_job_dashboard()

def finish_dynamodb_job():
  with open(JOBFILE_PATH) as fh:
    (job_name, job_id) = fh.read().split(',')

    job = fetch_job_from_dynamodb(job_id)
    job['completed'] = calendar.timegm(time.gmtime())
    job['status'] = 'completed'
    store_job_status_in_dynamodb(job)

    os.remove(JOBFILE_PATH)

  publish_job_dashboard()

if __name__ == '__main__':
  jobs = get_most_recent_jobs(1)
  print jobs[0]