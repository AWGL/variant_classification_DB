#!/bin/bash

source ~/miniconda3/bin/activate acmg_db

set -eo pipefail

cd ~/variant_classification_DB/
python manage.py productivity_report --output TEST
