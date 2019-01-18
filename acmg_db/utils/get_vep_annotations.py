import json
from .variant_utils import *
import random
import csv
import subprocess
import io
import os


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
	random_int = random.randint(1,10000)

	vcf_file_name = f'{temp_dir}/{sample}_{random_int}.vcf'

	for variant in variant_list:

		variant_info = process_variant_input(variant)

		vcf_list.append(variant_info)
		

	with open(vcf_file_name, 'w') as csvfile:

		vcf_writer = csv.writer(csvfile, delimiter='\t')

		for row in vcf_list:
			vcf_writer.writerow(row[1:3] + ['.'] + row[3:5])

	# Run vep

	command = f'source activate acmg_db && vep --input_file {vcf_file_name} --format vcf -o stdout --cache --offline --assembly GRCh37 --fasta {reference_genome} --refseq --dir {vep_cache} --flag_pick --species homo_sapiens --check_ref --cache_version 94 --json --numbers  --symbol --hgvs --no_stats --exclude_predicted'
	result = subprocess.check_output(command, shell=True)

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









