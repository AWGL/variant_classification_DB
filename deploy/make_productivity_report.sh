#!/bin/bash

source ~/miniconda3/bin/activate acmg_db

set -eo pipefail

cd ~/variant_classification_DB/
python manage.py productivity_report --output temp/temp_raw_data.csv

#Get all checkers
cut -f 2 -d "," temp/temp_raw_data.csv | sort -u > temp/temp_checkers

#Write out headers
echo "Checker,First Checks,First Check Samples,Second Checks,Second Check Samples" > "../CNV_reports/checker_report_$(date -I).csv"

#Get number of first checks, first check samples, second checks, second check samples per checker
while read checker; do

	first_checks=$(awk -F ',' -v checker=$checker '($2==checker && $3=="First_Check"){print}' temp/temp_raw_data.csv | wc -l)
	first_check_samples=$(awk -F ',' -v checker=$checker '($2==checker && $3=="First_Check"){print $1}' temp/temp_raw_data.csv | sort -u | wc -l)  
	second_checks=$(awk -F ',' -v checker=$checker '($2==checker && $3=="Second_Check"){print}' temp/temp_raw_data.csv | wc -l)
	second_check_samples=$(awk -F ',' -v checker=$checker '($2==checker && $3=="Second_Check"){print $1}' temp/temp_raw_data.csv | sort -u | wc -l)
	
	echo $checker,$first_checks,$first_check_samples,$second_checks,$second_check_samples >> "../CNV_reports/checker_report_$(date -I).csv"

done < temp/temp_checkers

#Remove temporary files
rm temp/temp_raw_data.csv temp/temp_checkers

