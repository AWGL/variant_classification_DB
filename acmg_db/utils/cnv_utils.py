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
		
		elif line[0].startswith('Sample ID'):
			
			meta_dict['sample_id'] = line[1]
		
		elif any("GRCh37" in field for field in line):
		
			meta_dict['genome'] = "GRCh37"
			
		elif any("GRCh37" in field for field in line):
		
			meta_dict['genome'] = "GRCh38"
			
		else:
			
			continue
	
	# reverse data because variant database output is in reverse order
	data_values = list(reversed(data_values))
	data_headers = headers[-1]
	
	#Add extra column header as data_values has extra blank column at end
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
