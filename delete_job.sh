#!/bin/bash

APP_PATH=/home/ubuntu/code/fleet
cd $APP_PATH

source /home/ubuntu/envs/fleet/bin/activate

python delete_current_job.py