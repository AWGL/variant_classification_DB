from ..forms import ReportingSearchForm
from ..models import *

from django.core.exceptions import  ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render

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
