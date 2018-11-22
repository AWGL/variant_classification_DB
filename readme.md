# Variant Classification DB

## Introduction

A small database to hold information about variant classifications done within the laboratory.

The main purpose of this database is to store the results of classifying variants using the ACMG guidlines [1].

The program is quite simple as it is not meant to act as a full Variant Database.

## Install and Setup

The software is a Django application using Python 3. It is reccomended that the software be deployed in a conda virtual environment.

First install Conda/Miniconda from [2]. Then type the following commands in your terminal to install and setup the application.

`git clone https://github.com/josephhalstead/variant_classification_DB.git`

`cd variant_classification_DB`

`conda env create -f env/acmg_db.yaml `

`source activate acmg_db`

`python manage.py migrate`

`python manage.py makemigrations acmg_db`

`python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py loaddata acmg_questions.json`

### Settings

There are also some options in mysite/settings.py that may need to be changed:

MUTALYZER_URL = 'https://mutalyzer.nl/services/?wsdl'

MUTALYZER_BUILD = 'hg19' 

Set these to your preferred settings or use the default.

## Test

There are some tests for the acmg classifier as well as checking all the views work.

`python manage.py test`

## Run

To run using the development server:

`python manage.py runserver`


## User Guide

### Setup an Account

No registration page - login using admin credentials (or contact an admin) (createsuperuser) at {your-url}/admin and follow the instructions to make a new account.

### Analyse a Variant

Enter variant details on home page form. The variant will be checked using Mutalzer to ensure you have entered a valid genomic coordinate.

The variant should be entered in the following format: {chromosome}:{pos}{ref}>{alt} e.g. 17:41197732G>A

If the variant is valid you will be redirected to the new_classifications page. This has three tabs

1. Sample Information Tab - Enter Details about the sample/classification here. Do not click the Submit button until you have finished on the other tabs.

2. ACMG Tab - Select ACMG classification codes that are relevant to the variant in question.

3. Evidence and Comments Tab - Enter comments and evidence here.

### View Previous Classifications.

Select Previous Classifications from the navigation bar at the top of the page.

There is a table showing all previous classifications - This can be filtered as needed.

### Perform Second Check

Navigate to the Previous Classifications page.

If a classification needs a second check there will be a 'perform second check' action displayed in the action column.

Click this to do a second check.

### Change Classification Status

Login the admin panel at {your-url}/admin with a superuser account.

Find the classification on the Classification page and change the status e.g. archive it by setting status to 'Old'

## To do and Limitations

* Automatically get variant annotations using VEP

* Add variant and sample pages

* Improve filtering


## References

[1] Standards and guidelines for the interpretation of sequence
variants: a joint consensus recommendation of the American
College of Medical Genetics and Genomics and the
Association for Molecular Pathology https://www.acmg.net/docs/standards_guidelines_for_the_interpretation_of_sequence_variants.pdf

[2] https://conda.io/miniconda.html