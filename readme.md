# Variant Classification DB

## Introduction

A  database to hold information about variant classifications done within the laboratory.

The main purpose of this database is to store the results of classifying variants using the ACMG guidelines [1] and CNVs using the ACMG CNV guidelines [2].


## Install and Setup

### Software Setup

Works on Centos 6/7

The software is a Django application using Python 3. It is reccomended that the software be deployed in a conda virtual environment.

First install Conda/Miniconda from [3]. Then type the following commands in your terminal to install and setup the application.

Optionally collect the gene annotations from the variant_filtering_app/data_sets/gene_data.csv

`git clone https://github.com/AWGL/variant_filtering_app.git`

Download main repository

`git clone https://github.com/josephhalstead/variant_classification_DB.git`

`cd variant_classification_DB`

`conda env create -f env/acmg_db.yaml `

`source activate acmg_db`

`python manage.py migrate`

`python manage.py makemigrations acmg_db`

`python manage.py migrate`

`python manage.py createsuperuser`

`python manage.py loaddata acmg_questions.json`

`python manage.py loaddata CNV_Gain_ACMG_questions.json`

`python manage.py loaddata CNV_Loss_ACMG_questions.json`

Optionally add gene data:

`python manage.py load_genes --gene_file variant_filtering_app/data_sets/gene_data.csv `


Static files which are viewed on the webpage also need to be moved to the static directory:

`mv files/* static/files/`

### Other Resources

* Reference Genome - either Human Reference GRCh37 or Human Reference GRCh38
* VEP Cache for GRCh37 - http://ftp.ensembl.org/pub/release-100/variation/indexed_vep_cache/homo_sapiens_refseq_vep_100_GRCh37.tar.gz
* VEP Cache for GRCh38 - http://ftp.ensembl.org/pub/release-104/variation/indexed_vep_cache/homo_sapiens_refseq_vep_104_GRCh38.tar.gz 

### Settings

There are also some options in mysite/settings.py that may need to be changed:

SECRET_KEY = 'xxxxxx'

ALLOWED_HOSTS = ['127.0.0.1']

MUTALYZER_URL = 'https://mutalyzer.nl/services/?wsdl'

MUTALYZER_BUILD = 'hg19' 

REFERENCE\_GENOME = '/media/sf\_Documents/genomics\_resources/refs/human\_g1k\_v37.fasta'

VEP\_CACHE = '/media/sf\_Documents/genomics\_resources/vep/'

VEP\_TEMP\_DIR = 'temp/'

Set these to your preferred settings or use the default. The secret key should be changed if running in production.

## Test

There are some tests for the acmg classifier as well as checking all the views work.

`python manage.py test --keepdb`

**Note - encoding error when running tests**: If run without the keepdb flag the encoding will default to LATIN9, which won't be able to load the example data fixtures, and then the database will be deleted. 
If the test database is kept with the keepdb flag, you can log into the psql terminal and change the encoding to UTF8 with the command `update pg_database set encoding = pg_char_to_encoding('UTF8') where datname = 'test_variant_classification_db'`, and then re-run the tests again.

## Run

To run using the development server:

`python manage.py runserver`

## Saving JSON file of ACMG criteria

If the ACMG criteria are changed, a JSON file should be saved into the fixtures folder so that a new database can be initialised with the same criteria.

To do this, run the command `python manage.py dumpdata acmg_db.classificationquestion > <date>_acmg_questions.json`


## References

[1] Standards and guidelines for the interpretation of sequence
variants: a joint consensus recommendation of the American
College of Medical Genetics and Genomics and the
Association for Molecular Pathology https://www.acmg.net/docs/standards\_guidelines\_for\_the\_interpretation\_of\_sequence\_variants.pdf

[2] Technical standards for the interpretation and reporting of constitutional copy number variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics (ACMG) and the Clinical Genome Resource (ClinGen) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7313390/

[3] https://conda.io/miniconda.html
