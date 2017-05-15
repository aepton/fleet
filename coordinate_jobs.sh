#!/bin/bash

/home/ubuntu/code/fleet/fetch_sqs.sh

job=$(</etc/current_job)
instance=$(ec2metadata --instance-id | cut -d " " -f 2)

if [ "$job" == "degree days" ]; then
  /home/ubuntu/code/degree_days/runner.sh
elif [ "$job" == "WA ETL" ]; then
  /home/ubuntu/code/campfin/scripts/rebuild_prod.sh
elif [ "$job" == "WA dedupe" ]; then
  /home/ubuntu/code/campfin/scripts/run_dedupe.sh
elif [ "$job" == "" ]; then
  # Sleep 2 minutes to allow debugging
  sleep 2m
  aws ec2 stop-instances --instance-ids=$instance
fi

