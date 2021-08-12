import json
import random
import os
import csv

from django.core.exceptions import  ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from acmg_db.forms import ReportingSearchForm, ReportingCNVSearchForm
from acmg_db.models import *

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def reporting(request):
	"""
	Page to view completed worksheets for reporting

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	context = {
		'classifications': None, 
		'form': ReportingSearchForm(options=PANEL_OPTIONS),
		'worksheet_status': None,
		'first_checker': None,
		'second_checker': None,
		'warn': None,
	}

	# if form is submitted
	if request.method == 'POST':
		form = ReportingSearchForm(request.POST, options=PANEL_OPTIONS)
		if form.is_valid():
			cleaned_data = form.cleaned_data

			# pull out classifications
			try:
				sample_obj = Sample.objects.get(
					name = cleaned_data['worksheet'] + '-' + cleaned_data['sample'] + '-' + cleaned_data['panel_name'].lower()
				)

				classifications = Classification.objects.filter(
					sample=sample_obj,
				)

				# work out if the worksheet has been completed
				worksheet_status = 'Completed'
				status_values = classifications.values('status')
				for s in status_values:
					if s['status'] in ['0', '1']:
						worksheet_status = 'Pending'

				# pull out any first checkers
				first_checker_values = classifications.values('user_first_checker').distinct()
				first_checker_list = []
				for value in first_checker_values:
					if value['user_first_checker']:
						user = User.objects.get(id=value['user_first_checker'])
						first_checker_list.append(user.username)
					else:
						first_checker_list.append('Unassigned')
				first_checker = ', '.join(first_checker_list)

				# pull out any second checkers
				second_checker_values = classifications.values('user_second_checker').distinct()
				second_checker_list = []
				for value in second_checker_values:
					if value['user_second_checker']:
						user = User.objects.get(id=value['user_second_checker'])
						second_checker_list.append(user.username)
					else:
						second_checker_list.append('Unassigned')
				second_checker = ', '.join(second_checker_list)

				context = {
					'classifications': classifications,
					'form': form,
					'worksheet_status': worksheet_status,
					'first_checker': first_checker,
					'second_checker': second_checker,
					'warn': None,
				}
			
			except ObjectDoesNotExist:
				context = {
					'classifications': None, 
					'form': form,
					'worksheet_status': None,
					'first_checker': None,
					'second_checker': None,
					'warn': ['Analysis does not exist.'],
				}

	return render(request, 'acmg_db/reporting.html', context)
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_reporting(request):
	"""
	Page to view completed worksheets for reporting

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	context = {
		'cnvs': None, 
		'form': ReportingCNVSearchForm(options=PANEL_OPTIONS),
		'worksheet_status': None,
		'first_checker': None,
		'second_checker': None,
		'warn': None,
	}

	# if form is submitted
	if request.method == 'POST':
		form = ReportingCNVSearchForm(request.POST, options=PANEL_OPTIONS)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			print(cleaned_data['sample'])
			
			# pull out CNV classifications
			try:	
				sample_obj = CNVSample.objects.get(
					sample_name = cleaned_data['sample']
				)

				cnvs = CNV.objects.filter(
					sample=sample_obj,
				)

				# work out if the worksheet has been completed
				worksheet_status = 'Completed'
				status_values = cnvs.values('status')
				for s in status_values:
					if s['status'] in ['0', '1']:
						worksheet_status = 'Pending'

				# pull out any first checkers
				first_checker_values = cnvs.values('user_first_checker').distinct()
				first_checker_list = []
				for value in first_checker_values:
					if value['user_first_checker']:
						user = User.objects.get(id=value['user_first_checker'])
						first_checker_list.append(user.username)
					else:
						first_checker_list.append('Unassigned')
				first_checker = ', '.join(first_checker_list)

				# pull out any second checkers
				second_checker_values = cnvs.values('user_second_checker').distinct()
				second_checker_list = []
				for value in second_checker_values:
					if value['user_second_checker']:
						user = User.objects.get(id=value['user_second_checker'])
						second_checker_list.append(user.username)
					else:
						second_checker_list.append('Unassigned')
				second_checker = ', '.join(second_checker_list)

				context = {
					'cnvs': cnvs,
					'form': form,
					'worksheet_status': worksheet_status,
					'first_checker': first_checker,
					'second_checker': second_checker,
					'warn': None,
				}
			
			except ObjectDoesNotExist:
				context = {
					'cnvs': None, 
					'form': form,
					'worksheet_status': None,
					'first_checker': None,
					'second_checker': None,
					'warn': ['Analysis does not exist.'],
				}

	return render(request, 'acmg_db/cnv_reporting.html', context)
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_cnv_decipher_download(request):
	"""
	Gets the ajax results from the cnv_reporting.html page and produces a decipher upload file. 

	"""
	if request.method == "POST":
		
		# Get the submitted answers and convert to python object
		cnv_selected = json.loads(request.body)
		
		print(cnv_selected)
		
		cnvs = cnv_selected['cnvs']
		
		print(cnvs)
		
		cnv_list=[]
		
		#Add headers to the list - based on decipher bulk upload template format
		cnv_list.append(["Patient internal reference number or ID", "Variant class", "Shared", "Assembly", "Chromosome", "Genomic start", "Genomic end", "Mean ratio", "Genotype", "Inheritance", "Heteroplasmy/Mosaicism by tissue", "Pathogenicity", "Pathogenicity evidence", "Evidence framework", "Pathogenicity note", "Contribution", "Genotype groups"])
		
		#Get elements needed for decipher file, changing them where decipher is specific about wording
		for i in cnvs:
			
			cnv = CNV.objects.get(pk=i)
			
			ID = cnv.sample.sample_name
			
			if cnv.copy == 'Amplification (>Trip)':
				cnv_class = "Amplification"
			else:
				cnv_class = cnv.copy
			
			shared = 'CAW'
			
			if cnv.sample.genome == "GRCh37":
				assembly = "GRCh37/hg19"
			elif cnv.sample.genome == "GRCh38":
				assembly = cnv.sample.genome
				
			chromosome = cnv.cnv.chromosome
			start = cnv.cnv.start
			end = cnv.cnv.stop
			ratio = ""
			genotype = cnv.genotype
			
			if cnv.inheritance == "De novo,Mosaic":
				inheritance = "De novo, mosaic"
			elif cnv.inheritance == "Maternal":
				inheritance = "Maternally inherited"
			elif cnv.inheritance == "Maternal,Mosaic":
				inheritance = "Maternally inherited, mosaic in mother"
			elif cnv.inheritance == "Paternal":
				inheritance = "Paternally inherited"
			elif cnv.inheritance == "Paternal,Mosaic":
				inheritance = "Paternally inherited, mosaic in father"
			else:
				inheritance = cnv.inheritance
			
			tissue = ""
			pathogenicity = cnv.display_classification()
			evidence = ""
			
			if cnv.method == 'Gain':
				framework = "ACMG/ClinGen CNV Gain Guidelines (2020)"
			elif cnv.method == 'Loss':
				framework = "ACMG/ClinGen CNV Loss Guidelines (2020)"
			
			note = ""
			contribution = ""
			group = ""
				
			cnv_list.append([ID, cnv_class, shared, assembly, chromosome, start, end, ratio, genotype, inheritance, tissue, pathogenicity, evidence, framework, note, contribution, group])
		
		#response = HttpResponse(cnv_list, content_type="text/plain")
			
		file_name = f'cnv_decipher_{request.user}_{random.randint(1,100000)}.csv'
		file_path = f'{settings.VEP_TEMP_DIR}/{file_name}'
			
		with open(file_path, mode='w') as cnv_list_file:
			cnv_list_writer = csv.writer(cnv_list_file , delimiter=',')

			for row in cnv_list:
				cnv_list_writer.writerow(row)
		
		response = HttpResponse(open(file_path, 'rb').read())
		response['Content-Type'] = 'text/csv'
		response['Content-Disposition'] = f'attachment; filename={file_name}'

		os.remove(file_path)

		return response
	
	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]
	form = ReportingCNVSearchForm(request.POST, options=PANEL_OPTIONS)
	return render(request, 'acmg_db/cnv_reporting.html', {'form': form})
