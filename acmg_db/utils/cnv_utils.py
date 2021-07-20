"""
Various functions for dealing with variants inputted by the user.

"""

import hashlib
import re
import pandas as pd
import csv
import subprocess
import io
import os
import random
import json

from django.conf import settings

def load_cnv(input_file):
	"""
	Loads the CNV worksheet and returns a dataframe containing the information as
	well as meta data.
	"""

	# make empty dictionary and lists to collect data
	meta_dict = {}
	headers = []
	data_values = []

	# make a csv reader object from the worksheet tsv file
	reader = csv.reader(input_file, delimiter='\t')
	
	# loop through lines, seperate out headers from data, pull out Worksheet (Array Barcode), Sample and Genome from headers
	for line in reader:
		
		#skip empty lines
		if len(line) == 0:
		
			continue
		
		if line[0].startswith('ISCN'):

			headers += [[field for field in line if field != '']]

		elif line[0].startswith('arr['):

			data_values += [line]
		
		elif line[0].startswith('Array Barcode'):
			
			meta_dict['worksheet_id'] = line[1] 
		
		elif line[0].startswith('Molecular Number'):
			
			meta_dict['sample_id'] = line[1]
			
		elif line[0].startswith('Sample ID'):
			meta_dict['cyto_id'] = line[1]
		
		elif any("GRCh37" in field for field in line):
		
			meta_dict['genome'] = "GRCh37"
			
		elif any("GRCh37" in field for field in line):
		
			meta_dict['genome'] = "GRCh38"
			
		else:
			
			continue
	
	# Set up headers
	#Add extra column header as data_values has extra blank column at end
	data_headers = headers[-1]
	data_headers.append('blank')

	# pull out metadata
	report_info = []

	for i in headers[:-1]:

		report_info.append(i[0].strip('#'))

	
	# make a dataframe from data section
	df = pd.DataFrame(data=data_values, columns=data_headers)

	# add to meta dictionary
	meta_dict['report_info'] = report_info


	return df, meta_dict

#------------------------------------------------
def process_cnv_input(cnv_input):
	"""
	Split the inputted cnv e.g. 8:8494182-8753293 into it's components.

	"""

	chromosome = cnv_input.split(':')[0]

	start = (cnv_input.split(':')[1]).split('-')[0]

	end = (cnv_input.split(':')[1]).split('-')[1]

	return ([chromosome, start, end])

	
#------------------------------------------------
def get_vep_info_local_cnv(cnv_list, vep_info, sample):
	"""
	Annotate the CNVs in cnv_list with a local installation of vep.

	Input:

	CNV_list = A list of variants e.g ['8:8494182-8753293', '8:61591393-61592346' ]
	vep_info = A dictionary containing information about vep. For example executable location
	sample = The sample ID

	"""

	# Make a vcf for input into vep

	vcf_list = []
	temp_dir = vep_info['temp_dir']
	reference_genome = vep_info['reference_genome']
	vep_cache = vep_info['vep_cache']
	assembly = vep_info['assembly']
	vep_version = vep_info['version']
	random_int = random.randint(1,10000)

	vcf_file_name = f'{temp_dir}/{sample}_{random_int}.vcf'

	# For each variant process it and append to list
	for cnv in cnv_list:

		variant_info = process_cnv_input(cnv)

		vcf_list.append(variant_info)
		
	# Write a temporary vcf for later vep annotation
	with open(vcf_file_name, 'w') as csvfile:

		for row in vcf_list:
			
			csvfile.write("%s\t%s\t.\t.\t<CNV>\t.\t.\tSNVTYPE=CNV;END=%s\t.\n" % (row[0],row[1],row[2]))

	# Run vep

	command = f'source  ~/miniconda3/bin/activate acmg_db && vep --input_file {vcf_file_name} --format vcf -o stdout --cache --offline --no_check_variants_order --assembly {assembly} --fasta {reference_genome} --refseq --dir {vep_cache} --flag_pick --species homo_sapiens --check_ref --cache_version {vep_version} --json --numbers  --symbol --hgvs --no_stats --exclude_predicted --max_sv_size 1000000000000'
	result = subprocess.check_output(command, shell=True, executable='/bin/bash')

	# Collect output and put into json
	result = result.decode("utf-8") 
	file = io.StringIO(result)

	vep_anno_list = []

	for variant, original in zip(file,cnv_list):

		vep_anno_list.append([json.loads(variant), original])

	if len(vep_anno_list) != len(cnv_list):

		raise Exception('VEP annotation failed - annotated variant list is not the same length as original list. Did you select the correct reference genome?')

	os.remove(vcf_file_name)

	return vep_anno_list

