import json

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

from acmg_db.forms import CNVSampleInfoForm, CNVDetailsForm, CNVMethodForm, FinaliseClassificationSecondCheckForm
from acmg_db.models import *

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_acmg_cnv_classification_second(request):
	"""
	Gets the ajax results from the new_classifcations.html page \
	and stores them in the database - also returns the calculated result.

	This view is for the second check.
	"""

	if request.is_ajax():

		# Get the submitted answers and convert to python object
		classification_answers = request.POST.get('cnvs')
		classification_answers = json.loads(classification_answers)

		# Get the classification pk and load the classification
		cnv_pk = request.POST.get('cnv_pk').strip()
		cnv = get_object_or_404(CNV, pk=cnv_pk)

		# Ensure correct user and status
		if cnv.status != '1' or request.user != cnv.user_second_checker:

			raise PermissionDenied('You do not have permission to start this classification.')
		
		if cnv.method == "Gain":
			correct_number_of_questions = CNVGainClassificationQuestion.objects.all().count()
			if len(classification_answers) != correct_number_of_questions:
				raise Exception('Wrong number of questions')

			# Update the classification answers
			for classification_answer in classification_answers:
				
				pk = classification_answer.strip()

				classification_answer_obj = get_object_or_404(CNVGainClassificationAnswer, pk=pk)

				classification_answer_obj.score_second = classification_answers[classification_answer][0].strip()

				classification_answer_obj.comment_second = classification_answers[classification_answer][1].strip()

				classification_answer_obj.save()
			
			
		elif cnv.method == "Loss":
			correct_number_of_questions = CNVLossClassificationQuestion.objects.all().count()
			if len(classification_answers) != correct_number_of_questions:
				raise Exception('Wrong number of questions')
			
			# Update the classification answers
			for classification_answer in classification_answers:
				
				pk = classification_answer.strip()

				classification_answer_obj = get_object_or_404(CNVLossClassificationAnswer, pk=pk)

				classification_answer_obj.score_second = classification_answers[classification_answer][0].strip()

				classification_answer_obj.comment_second = classification_answers[classification_answer][1].strip()

				classification_answer_obj.save()

		# update the score in the database
		cnv.second_final_score = cnv.calculate_acmg_score_second()
		if cnv.second_final_score >= 0.99:
			cnv.second_final_class = "4"
		elif 0.90 <= cnv.second_final_score <= 0.98:
			cnv.second_final_class = "3"
		elif -(0.89) <= cnv.second_final_score <= 0.89:
			cnv.second_final_class = "2"
		elif -(0.98) <= cnv.second_final_score <= -(0.90):
			cnv.second_final_class = "1"
		elif cnv.second_final_score <= -(0.99):
			cnv.second_final_class = "0"
		cnv.save()
		
		context = {
			'result_first': cnv.display_first_classification(),
			'result_second': cnv.display_final_classification(),
		}

		html = render_to_string('acmg_db/acmg_results_second.html', context)

	return HttpResponse(html)


#--------------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def cnv_second_check(request, pk):
	"""
	Page for entering doing a second check classifications.

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	cnv = get_object_or_404(CNV, pk=pk)

	# Assign second check to first person to click the link
	if cnv.user_second_checker == None:

		cnv.user_second_checker = request.user
		cnv.save()

	#reject if wrong status or user
	if cnv.status != '1' or request.user != cnv.user_second_checker:

		raise PermissionDenied(f'You do not have permission to perform the second check. It is assigned to {request.user}')

	else:
		# Get data to render form

#		previous_classifications = Classification.objects.filter(variant=variant,genome=classification.sample.genome, status__in=['2', '3']).exclude(pk=classification.pk).order_by('-second_check_date')
#		previous_full_classifications = previous_classifications.filter(genuine='1').order_by('-second_check_date')

		if cnv.method == "Gain":
			answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
			if len(answers) == 0:
				cnv.initiate_classification()
				answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
		elif cnv.method == "Loss":
			answers = CNVLossClassificationAnswer.objects.filter(cnv=cnv)
			if len(answers) == 0:
				cnv.initiate_classification()
				answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)

		comments = CNVUserComment.objects.filter(classification=cnv, visible=True)

		result_first = cnv.display_first_classification()
		result_second = cnv.display_final_classification()

		if result_second == 'VUS - contradictory evidence provided':

			result_second = 'Contradictory evidence provided'

		

		# make empty instances of forms
		sample_form = CNVSampleInfoForm(request.POST)
		details_form = CNVDetailsForm(request.POST)
		method_form = CNVMethodForm(request.POST)
#		finalise_form = FinaliseClassificationSecondCheckForm(classification_pk=classification.pk)

		# dict of data to pass to view
		context = {
			'cnv': cnv,
#			'previous_classifications': previous_classifications,
#			'previous_full_classifications': previous_full_classifications,
			'answers': answers,
			'comments': comments,
			'result_first': result_first,
			'result_second': result_second,
			'sample_form': sample_form,
			'details_form': details_form,
			'method_form' : method_form,
#			'finalise_form': finalise_form,
			'warn': []
		}
			
		#-----------------------------------------------
		# if a form is submitted
		if request.method == 'POST':

			# SampleInfoForm
			if 'affected_with' in request.POST:

				sample_form = CNVSampleInfoForm(request.POST)

				# load in data
				if sample_form.is_valid():

					cleaned_data = sample_form.cleaned_data
					sample = cnv.sample
					sample.affected_with =  cleaned_data['affected_with']
					sample.cyto = cleaned_data['cyto_ID']
					sample.platform = cleaned_data['platform']
					sample.save()
					
				
				# reload dict variables for rendering
				context['cnv'] = get_object_or_404(CNV, pk=pk)
				context['sample_form'] = CNVSampleInfoForm(request.POST)
			
			#Details Form
			if 'inheritance' in request.POST:
				
				details_form = CNVDetailsForm(request.POST)
				
				if details_form.is_valid():
					
					#Inheritance
					#makes list based on the inheritance check box
					inheritance = details_form.cleaned_data['inheritance']					
					#convert list to string to save in model
					inheritance_str = ""
					for entry in inheritance:
						inheritance_str += entry+','
					#Remove comma from end of string
					inheritance_str = inheritance_str[:-1]
					
					#Copy Number
					copy = details_form.cleaned_data['copy_number']
					
					#Genotype
					genotype = details_form.cleaned_data['genotype']
					
					#Add to cnv model
					cnv.inheritance = inheritance_str
					cnv.copy = copy
					cnv.genotype = genotype
					cnv.save()
			
			# Changing ACMG Method Form
			if 'method' in request.POST:

				method_form = CNVMethodForm(request.POST)

				if method_form.is_valid():
					
					method = method_form.cleaned_data['method']
					
					# if method on form doesn't equal method saved in object, update method and re-calculate answers
					if method != cnv.method:
						cnv.method = method
						cnv.save()
					
					if cnv.method == "Gain":
						answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
						if len(answers) == 0:
							cnv.initiate_classification()
							answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
					elif cnv.method == "Loss":
						answers = CNVLossClassificationAnswer.objects.filter(cnv=cnv)
						if len(answers) == 0:
							cnv.initiate_classification()
							answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
					
					context['answers'] = answers
					context['method_form'] = CNVMethodForm(request.POST)	
		"""
			
			# FinaliseClassificationForm
			if 'final_classification' in request.POST:

				# Don't let anyone except the assigned second checker submit the form
				if classification.status != '1' or request.user != classification.user_second_checker:

					raise PermissionDenied('You do not have permission to finalise the classification.')

				finalise_form = FinaliseClassificationSecondCheckForm(request.POST, classification_pk=classification.pk)

				if finalise_form.is_valid():

					cleaned_data = finalise_form.cleaned_data

					# validation that everything has been completed - make sure all fields are completed, genuine/artefact is set

					if classification.genuine == '0':

						context['warn'] += ['Select whether the variant is genuine or artefact']

					if classification.selected_transcript_variant.transcript.gene.inheritance_pattern == None or classification.selected_transcript_variant.transcript.gene.inheritance_pattern == '':

						context['warn'] += ['Inheritence pattern has not been set']

					if classification.selected_transcript_variant.transcript.gene.conditions == None or classification.selected_transcript_variant.transcript.gene.conditions == '':

						context['warn'] += ['Gene associated conditions have not been set']

					if classification.genuine  == '2' and (cleaned_data['final_classification'] != previous_full_classifications[0].second_final_class):

						context['warn'] += ['You selected to use the last full classification, but the selected classification does not match']

					if classification.genuine  == '3' and cleaned_data['final_classification'] != '7':

						context['warn'] += ['This classification was selected as Not Analysed - therefore the only option is NA']

					if classification.genuine  == '4' and cleaned_data['final_classification'] != '6' :

						context['warn'] += ['This classification was selected as Artefect - therefore the only valid option is Artefect']

					# if validation has been passed, finalise first check
					if len(context['warn']) == 0:

						# if new classification, pull score from the acmg section and save to final class
						if classification.genuine == '1':

							classification.second_final_class = classification.calculate_acmg_score_second()

						# if anything other than 'dont override' selected, then change the classification
						if cleaned_data['final_classification'] != '8':

							classification.second_final_class = cleaned_data['final_classification']

						# update status and save
						classification.status = '2'
						classification.second_check_date = timezone.now()
						classification.user_second_checker = request.user
						classification.save()

						#return redirect('home')
						return redirect('/pending_classifications?sample={}&worksheet={}&panel={}'.format(
							classification.sample.sample_name_only,
							classification.sample.worklist.name,
							classification.sample.analysis_performed.panel
						))

			return render(request, 'acmg_db/second_check.html', context)
			"""
			
		return render(request, 'acmg_db/cnv_second_check.html', context)
