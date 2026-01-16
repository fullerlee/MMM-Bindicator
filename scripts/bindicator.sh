#!/bin/bash

#first cd into the directory where this script lives
cd "$(dirname "$0")"

source .venv/bin/activate && python ./bindicator.py 

#cat bin_schedule.json
