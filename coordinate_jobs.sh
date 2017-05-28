#!/bin/bash

get_current_instance() {
  instance=$(ec2metadata --instance-id | cut -d " " -f 2)
}

get_current_job() {
  /home/ubuntu/code/fleet/fetch_job.sh
  job=$(</etc/current_job)
}

shutdown_instance() {
  # Sleep 2 minutes to allow debugging
  echo "Sleeping"
  sleep 2m
  # aws ec2 stop-instances --instance-ids=$instance
}

update_repos() {
  repos=( "/home/ubuntu/code/campfin" "/home/ubuntu/code/campfin_admin" "/home/ubuntu/code/fleet" )
  for i in "${repos[@]}"
  do
    cd $i
    git pull origin master
  done
}

update_repos

get_current_job
get_current_instance

while [ -n "$job" ]
do

  case "$job" in
    "degree days" ) /home/ubuntu/code/degree_days/runner.sh ;;
    "WA ETL"      ) /home/ubuntu/code/campfin/scripts/rebuild_prod.sh ;;
    "WA dedupe"   ) /home/ubuntu/code/campfin/scripts/run_dedupe.sh ;;
  esac

  /home/ubuntu/code/fleet/delete_job.sh

  get_current_job

done

shutdown_instance
