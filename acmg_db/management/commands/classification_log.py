from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from acmg_db.models import *
import csv
from datetime import datetime 

'''
Author: Seemu Ali 
Date: 02.11.2021 
Description: Get a log of classifications requested by clinical scientist for their competency portfolio, run command within variant_classification_DB directory 
	     and ensure the acmg_db conda environment is activated.
Command: python manager.py classification_log <--firstchecker or --secondchecker flag> <email> <path to output directory>
Example: python manager.py classification_log --firstchecker laz.lazarou@wales.nhs.uk ./queries 
'''

class Command(BaseCommand):

	help = "Generate a clinical scientist's log of variant classifications"

	def add_arguments(self, parser):
	  	group = parser.add_mutually_exclusive_group(required=True)
	  	group.add_argument('--firstchecker', action='store_true', help="pull out all classifications with clinical scientist as first checker")
	  	group.add_argument('--secondchecker', action='store_true', help="pull out all classifications with clinical scientist as second checker")
	  	parser.add_argument('email', help="clinical scientist's NHS email as reigistered in the database")
	  	parser.add_argument('output', help="file path to store classification log")

	def get_classifications(self, check_string, checks, output):
		date = datetime.now().strftime("%Y_%m_%d")
		variant_info=[]
		sample_id=[]
		second_chk = []
		second_chk_date = []
		first_chk = []
		first_chk_date =[]
		first_class = []
		second_class = []
		
		#loop through classification object to pull out relevant data for report 
		for contents in checks:  
			second_chk.append(contents.user_second_checker)
			second_chk_date.append(contents.second_check_date)
			first_chk.append(contents.user_first_checker)
			first_chk_date.append(contents.first_check_date)
			variant_info.append(contents.variant)
			sample_id.append(contents.sample)
			first_class.append(contents.first_final_class)
			second_class.append(contents.second_final_class)
		
		
		#collates all classification data from lists defined above and defines the header for log report 
		data_log=zip(sample_id, variant_info, first_class, first_chk, first_chk_date, second_class, second_chk, second_chk_date) 
		header=['sample', 'variant',  'first classification (0-5=benign-pathogenic, 6=artefact, 7=not analysed)', 'first checker', 'first check date', 'second classification (0-5=benign-pathogenic, 6=artefact, 7=not analysed)', 'second checker', 'second check date']
		
		#generate log report  
		with open(f"{output}/{date}_{check_string}.csv", "w") as f:
			writer = csv.writer(f)
			writer.writerow(header)
			for data in data_log:
				writer.writerow(data)  #write each classification instance into file 
			

	def handle(self, *args, **options):
		
		#define variables from command line arguments 
		email = options['email']
		firstcheck = options['firstchecker']
		secondcheck = options['secondchecker']
		output = options['output']
		
		scientist = User.objects.get(username=email)

		if firstcheck == True:
			# if firstcheck flag used filter database with clinical scientist as first checker  
			checks = Classification.objects.filter(user_first_checker=scientist)   
			check_string = 'firstchk'

		if secondcheck == True:
			#if secondcheck flag used filter database with clinical scientist as second checker  
			checks = Classification.objects.filter(user_second_checker=scientist) 
			check_string = 'secondchk' 


		self.get_classifications(check_string,checks,output)

		
