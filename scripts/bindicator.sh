#!/bin/bash

#python3 -m venv .venv
#source .venv/bin/activate
#pip install selenium webdriver-manager

#first cd into the directory where this script lives
cd "$(dirname "$0")"

source .venv/bin/activate && python ./bindicator.py > /dev/null

cat ./bin_schedule.json
