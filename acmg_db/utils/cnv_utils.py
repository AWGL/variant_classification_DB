"""
Various functions for dealing with CNVs inputted by the user.

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
from django.db import transaction
from django.db.models import Q, F

from acmg_db.models import *

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
			
		elif any("GRCh38" in field for field in line):
		
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
def load_bluefuse(input_file):
	"""
	Loads the CNV worksheet (from bluefuse) and returns a dataframe containing the information as
	well as meta data.
	"""

	# make empty dictionary and lists to collect data
	meta_dict = {}
	headers = []
	data_values = []
	max_values = []

	# make a csv reader object from the worksheet tsv file
	reader = csv.reader(input_file, delimiter='\t')
	
	# loop through lines, seperate out headers from data, pull out Worksheet (Array Barcode), Sample and Genome from headers
	for line in reader:
			
		#skip empty lines
		if len(line) == 0:
		
			continue
		
		# If line starts with Region , take the headers, and then the data lines until an empty line is reached
		if line[0] == 'Region':

			headers += [field for field in line if field != '']
			next_line = next(reader)
			while len(next_line) != 0:
				data_values += [next_line]
				next_line = next(reader)
			
		#Molecular Number
		elif line[0].startswith('Sample ID'):
			
			sample_id = line[0].split(": ")[1]
			meta_dict['sample_id'] = sample_id
		
		#Cyto ID
		elif line[0].startswith('Subject ID'):
		
			subject_id = line[0].split(": ")[1]
			meta_dict['cyto_id'] = subject_id
		
		#Reference Genome	
		elif any("GRCh37" in field for field in line):
		
			meta_dict['genome'] = "GRCh37"
			
		elif any("GRCh38" in field for field in line):
		
			meta_dict['genome'] = "GRCh38"
			
		#Max values
		elif line[0] == 'max':
			
			start = line[7]
			stop = line[8]
			max_values += [[start, stop]]
			
		else:
			
			continue
	
	print(headers)
	print(data_values)
	print(meta_dict)
	print(max_values)
	
	# pull out metadata
	report_info = []

	for i in headers:

		report_info.append(i)

	# make a dataframe from data section
	df_values = pd.DataFrame(data=data_values, columns=headers)
	
	df_max = pd.DataFrame(data=max_values, columns=("max_start","max_stop"))

	df = pd.concat([df_values,df_max], axis=1)
	
	print(df)

	#add to meta dictionary
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
	
#-------------------------------------------
def calculate_acmg_class(score):
	
	if score == "NA":
		return "5"
	else:
		score = float(score) #bug fix, without this the elif statements below don't work correctly
		if score >= 0.99:
			return "4"
		elif 0.90 <= score <= 0.98: 
			return "3"
		elif -(0.89) <= score <= 0.89:
			return "2"
		elif -(0.98) <= score <= -(0.90):
			return "1"
		elif score <= -(0.99):
			return "0"
		else:
			print("ERROR! Class could not be calculated")
			return "Error"
	
		
		
#---------------------------------------------------
def cnv_previous_classifications(cnv):
	"""
	Function to get all existing classifications which overlap with a new CNV with 50% reciprocal overlap
	"""
	# set 50% of length of new CNV
	length_50 = (cnv.cnv.length/100)*50
		
	# Initial filter based on start/stop coordinate overlap + same reference genome
	# Q(start__lte=cnv.start, stop__gte=cnv.stop, status__in=['2','3']) = New CNV contained entirely within existing CNV, also covers instances where CNV is identical
	# Q(start__gte=cnv.start, stop__lte=cnv.stop, status__in=['2','3']) = Existing CNV contained entirely within new CNV
	# Q(start__lte=cnv.start, stop__lte=cnv.stop, stop__gte=cnv.start, status__in=['2','3']) = New CNV starts after existing start, stops after existing stop, but start is before existing stop 
	# Q(start__gte=cnv.start, stop__gte=cnv.stop, start__lte=cnv.stop, status__in=['2','3']) = New CNV starts before existing start, stops before existing stop, but stop is after existing start
		
	filter_classifications = CNV.objects.filter(Q(cnv__chromosome=cnv.cnv.chromosome, cnv__start__gte=cnv.cnv.start, cnv__stop__lte=cnv.cnv.stop, status__in=['2','3'], cnv__genome=cnv.cnv.genome) | 
							Q(cnv__chromosome=cnv.cnv.chromosome, cnv__start__lte=cnv.cnv.start, cnv__stop__gte=cnv.cnv.stop, status__in=['2','3'], cnv__genome=cnv.cnv.genome) |
							Q(cnv__chromosome=cnv.cnv.chromosome, cnv__start__lte=cnv.cnv.start, cnv__stop__lte=cnv.cnv.stop, cnv__stop__gte=cnv.cnv.start, status__in=['2','3'], cnv__genome=cnv.cnv.genome) |
							Q(cnv__chromosome=cnv.cnv.chromosome, cnv__start__gte=cnv.cnv.start, cnv__stop__gte=cnv.cnv.stop, cnv__start__lte=cnv.cnv.stop, status__in=['2','3'], cnv__genome=cnv.cnv.genome)).exclude(pk=cnv.pk).order_by('-second_check_date')
		
	#make empty lists for classifications
	previous_classifications = []
	previous_full_classifications = []
		
	#Now add filter for 50% reciprocal overlap
	#Loop over initial filter
	for classification in filter_classifications:
			
		#if new CNV is entirely contained within existing CNV, add to list (with a second add if genuine)
		if (classification.cnv.start<=cnv.cnv.start) & (classification.cnv.stop>=cnv.cnv.stop):
			previous_classifications.append(classification)
			if classification.genuine is '1':
				previous_full_classifications.append(classification)
				
		#if new CNV entirely contains an existing CNV, add to list (with a second add if genuine)
		elif (classification.cnv.start>=cnv.cnv.start) & (classification.cnv.stop<=cnv.cnv.stop):
			previous_classifications.append(classification)
			if classification.genuine is '1':
				previous_full_classifications.append(classification)
				
		#For all other overlap cases, check there is 50% reciprocal overlap
		# Where start of new CNV > start of existing CNV	
		# calculate overlap and 50% of length of existing CNV
		elif (classification.cnv.start<=cnv.cnv.start):
			overlap = classification.cnv.stop-cnv.cnv.start
			exist_length_50 = (classification.cnv.length/100)*50
			# if overlap is > 50% length of both new CNV and existing CNV, add to list (with a second add if genuine)
			if (overlap > length_50) & (overlap > exist_length_50):
				previous_classifications.append(classification)
				if classification.genuine is '1':
					previous_full_classifications.append(classification)
				
		# Where start of new CNV < start of existing CNV	
		# calculate overlap and 50% of length of existing CNV
		elif (classification.cnv.start>=cnv.cnv.start):
			overlap = cnv.cnv.stop-classification.cnv.start
			exist_length_50 = (classification.cnv.length/100)*50
			# if overlap is > 50% length of both new CNV and existing CNV, add to list (with a second add if genuine)
			if (overlap > length_50) & (overlap > exist_length_50):
				previous_classifications.append(classification)
				if classification.genuine is '1':
					previous_full_classifications.append(classification)
	
	return (previous_classifications,previous_full_classifications)
