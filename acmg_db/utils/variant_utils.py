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

def get_variant_hash(chromosome, pos, ref,alt):
	"""
	Generates a sha256 hash of the variant. Used as promary key in Variant model.
	Input: chromosome, pos, ref,alt - self explanatory
	Output:
	hash_id = The sha256 hash of the chromosome + " " + pos + " " + ref + " " + alt
	Note The space between the 4 inputs. This stops problem of Chr1 12 A G and Chr11 2 A G being same hash e.g. hash(Chr112AG)
	"""

	hash_string = bytes('{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=pos, ref=ref, alt=alt), 'utf-8')

	hash_id = hashlib.sha256(hash_string).hexdigest()

	return hash_id


def process_variant_input(variant_input):
	"""
	Split the inputted variant e.g. 17:41197732G>A into it's components.

	"""

	chromosome = variant_input.split(':')[0]

	position = re.findall('\d+',variant_input.split(':')[1])[0]

	ref = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[0])

	alt = re.sub('[0-9]', '', variant_input.split(':')[1].split('>')[1])

	var_hash = get_variant_hash(chromosome, position,ref, alt)

	key = '{chr}-{pos}-{ref}-{alt}'.format(chr =chromosome, pos=position, ref=ref, alt=alt)

	return ([var_hash, chromosome, position, ref, alt, key])


def load_worksheet(input_file):
	"""
	Loads the worksheet and returns a dataframe containing the information as
	well as meta data.
	"""

	# make empty lists to collect data
	headers = []
	data_values = []

	# make a csv reader object from the worksheet tsv file
	reader = csv.reader(input_file, delimiter='\t')
	
	# loop through lines, seperate out headers from data
	for line in reader:

		if line[0].startswith('#'):

			headers += [[field for field in line if field != '']]

		else:

			data_values += [line]
	
	# reverse data because variant database output is in reverse order
	data_values = list(reversed(data_values))
	data_headers = headers[-1]

	# pull out metadata
	report_info = []

	for i in headers[:-1]:

		report_info.append(i[0].strip('#'))

	# make a dataframe from data section
	df = pd.DataFrame(data=data_values, columns=data_headers)
	assert len(df['#SampleId'].unique()) == 1
	assert len(df['WorklistId'].unique()) == 1

	# make meta dictionary
	meta_dict = {'report_info': report_info}

	print (df)

	return df, meta_dict


def get_vep_info_local(variant_list, vep_info, sample):
	"""
	Annotate the variants in variant_list with a local installation of vep.

	Input:

	variant_list = A list of variants e.g ['2:170112639G>A' '2:241661268C>G' ]
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
	for variant in variant_list:

		variant_info = process_variant_input(variant)

		vcf_list.append(variant_info)
		
	# Write a temporary vcf for later vep annotation
	with open(vcf_file_name, 'w') as csvfile:

		vcf_writer = csv.writer(csvfile, delimiter='\t')

		for row in vcf_list:
			
			vcf_writer.writerow(row[1:3] + ['.'] + row[3:5])

	# Run vep

	command = f'source  ~/miniconda3/bin/activate acmg_db && vep --input_file {vcf_file_name} --format vcf -o stdout --cache --offline --no_check_variants_order --assembly {assembly} --fasta {reference_genome} --refseq --dir {vep_cache} --flag_pick --species homo_sapiens --check_ref --cache_version {vep_version} --json --numbers  --symbol --hgvs --no_stats --exclude_predicted'
	result = subprocess.check_output(command, shell=True, executable='/bin/bash')

	# Collect output and put into json
	result = result.decode("utf-8") 
	file = io.StringIO(result)

	vep_anno_list = []

	for variant, original in zip(file,variant_list):

		vep_anno_list.append([json.loads(variant), original])

	if len(vep_anno_list) != len(variant_list):

		raise Exception('VEP annotation failed - annotated variant list is not the same length as original list.')

	os.remove(vcf_file_name)

	return vep_anno_list










