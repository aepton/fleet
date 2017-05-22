def lambda_handler(event, context):
  metadata = {
    'ec2': {
      'instances': {
        'small': 'i-014eae664012ac9ba'
      }
    }
  }

  job_info = [{
      'jobId': str(uuid.uuid4()),
      'jobType': 'campfin',
      'jobName': 'WA ETL',
      'instance': metadata['ec2']['instances']['small'],
      'status': 'pending'
  }, {
      'jobId': str(uuid.uuid4()),
      'jobType': 'personal',
      'jobName': 'degree days',
      'instance': metadata['ec2']['instances']['small'],
      'status': 'pending'
  }]

  for job in job_info:
      store_job_status_in_dynamodb(job)

  return 'Launch successful'

  ec2_client = boto3.client(
      'ec2',
      aws_access_key_id=os.environ.get('aws_key_id'),
      aws_secret_access_key=os.environ.get('aws_key'))
  try:
      #response = ec2_client.start_instances(
      #    InstanceIds=[job['instance'] for job in job_info])
      return 'Launch successful'
  except Exception, e:
      return 'Launch failed: %s' % e