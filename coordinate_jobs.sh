#!/bin/bash

jobfile_path="/tmp/current_job"

get_current_instance() {
  instance=$(ec2metadata --instance-id | cut -d " " -f 2)
  echo "Got instance $instance"
}

get_current_job() {
  touch $jobfile_path
  job_data=$(<$jobfile_path)
  IFS=',' read -ra job_info <<< "$job_data"; unset IFS;
  job=${job_info[0]}
  echo "Starting with $job"
  /home/ubuntu/code/fleet/fetch_job.sh
  job_data=$(<$jobfile_path)
  IFS=',' read -ra job_info <<< "$job_data"; unset IFS;
  job=${job_info[0]}
  echo "Got job $job"
}

shutdown_instance() {
  # Sleep 2 minutes to allow debugging
  echo "Sleeping"
  sleep 2m
  aws ec2 stop-instances --instance-ids=$instance
}

update_repos() {
  repos=( "/home/ubuntu/code/campfin" "/home/ubuntu/code/campfin_admin" "/home/ubuntu/code/fleet" )
  for i in "${repos[@]}"
  do
    cd $i
    echo "Updating $i"
    git pull origin master
  done
}

update_repos

get_current_job
get_current_instance

while [ -n "$job" ]
do

  case "$job" in
    "degree days" ) echo "Launching degree days"; /home/ubuntu/code/degree_days/runner.sh ;;
    "WA ETL"      ) echo "Launching WA ETL"; /home/ubuntu/code/campfin/scripts/rebuild_prod.sh ;;
    "WA dedupe"   ) echo "Launching WA dedupe"; /home/ubuntu/code/campfin/scripts/run_dedupe.sh ;;
  esac

  echo "Deleting job"
  /home/ubuntu/code/fleet/delete_job.sh

  get_current_job

done

shutdown_instance
