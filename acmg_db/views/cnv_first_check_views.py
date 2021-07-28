import json
import base64
import re

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q, F
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

from acmg_db.forms import CNVSampleInfoForm, CNVGenuineArtefactForm, CNVFinaliseClassificationForm, CNVDetailsForm, CNVMethodForm
from acmg_db.models import *

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_first_check(request, pk):
	"""
	Page for entering new CNV classifications.

	Has the following featues:

	1) Forms for entering CNV and sample information
	2) Form for selecting whether the CNV is genuine
	3) ACMG classifier.
	4) Comments and Evidence.
	5) Final submit form

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	cnv = get_object_or_404(CNV, pk=pk)

	# Assign first check to first person to click the link
	if cnv.user_first_checker == None:

		cnv.user_first_checker = request.user
		cnv.save()
	
	#reject if wrong status or user
	if cnv.status != '0' or request.user != cnv.user_first_checker:

		raise PermissionDenied('You do not have permission to start this classification.')

	else:

		# Get data to render form
		
		# previous classifications
		# set 50% of length of new CNV
		length_50 = (cnv.length/100)*50
		
		# Initial filter based on start/stop coordinate overlap + same reference genome
		# Q(start__lte=cnv.start, stop__gte=cnv.stop, status__in=['2','3']) = New CNV contained entirely within existing CNV, also covers instances where CNV is identical
		# Q(start__gte=cnv.start, stop__lte=cnv.stop, status__in=['2','3']) = Existing CNV contained entirely within new CNV
		# Q(start__lte=cnv.start, stop__lte=cnv.stop, stop__gte=cnv.start, status__in=['2','3']) = New CNV starts after existing start, stops after existing stop, but start is before existing stop 
		# Q(start__gte=cnv.start, stop__gte=cnv.stop, start__lte=cnv.stop, status__in=['2','3']) = New CNV starts before existing start, stops before existing stop, but stop is after existing start
		
		filter_classifications = CNV.objects.filter(Q(start__gte=cnv.start, stop__lte=cnv.stop, status__in=['2','3'], sample__genome=cnv.sample.genome) | 
								Q(start__lte=cnv.start, stop__gte=cnv.stop, status__in=['2','3'], sample__genome=cnv.sample.genome) |
								Q(start__lte=cnv.start, stop__lte=cnv.stop, stop__gte=cnv.start, status__in=['2','3'], sample__genome=cnv.sample.genome) |
								Q(start__gte=cnv.start, stop__gte=cnv.stop, start__lte=cnv.stop, status__in=['2','3'], sample__genome=cnv.sample.genome)).exclude(pk=cnv.pk).order_by('-second_check_date')
		
		#make empty lists for classifications
		previous_classifications = []
		previous_full_classifications = []
		
		#Loop over initial filter
		for classification in filter_classifications:
			
			#if new CNV is entirely contained within existing CNV, add to list (with a second add if genuine)
			if (classification.start<=cnv.start) & (classification.stop>=cnv.stop):
				previous_classifications.append(classification)
				if classification.genuine is '1':
					previous_full_classifications.append(classification)
				
			#if new CNV entirely contains an existing CNV, add to list (with a second add if genuine)
			elif (classification.start>=cnv.start) & (classification.stop<=cnv.stop):
				previous_classifications.append(classification)
				if classification.genuine is '1':
					previous_full_classifications.append(classification)
				
			#For all other overlap cases, check there is 50% reciprocal overlap
			# Where start of new CNV > start of existing CNV	
			# calculate overlap and 50% of length of existing CNV
			elif (classification.start<=cnv.start):
				overlap = classification.stop-cnv.start
				exist_length_50 = (classification.length/100)*50
				# if overlap is > 50% length of both new CNV and existing CNV, add to list (with a second add if genuine)
				if (overlap > length_50) & (overlap > exist_length_50):
					previous_classifications.append(classification)
					if classification.genuine is '1':
						previous_full_classifications.append(classification)
					
			# Where start of new CNV < start of existing CNV	
			# calculate overlap and 50% of length of existing CNV
			elif (classification.start>=cnv.start):
				overlap = cnv.stop-classification.start
				exist_length_50 = (classification.length/100)*50
				# if overlap is > 50% length of both new CNV and existing CNV, add to list (with a second add if genuine)
				if (overlap > length_50) & (overlap > exist_length_50):
					previous_classifications.append(classification)
					if classification.genuine is '1':
						previous_full_classifications.append(classification)
		
		# Sort by second checker date so that the most recent is the first object in the list
		previous_classifications.sort(key=lambda x: x.second_check_date, reverse = True)
		previous_full_classifications.sort(key=lambda x: x.second_check_date, reverse = True)
		
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
		result = cnv.display_first_classification()  # current class to display
		score = cnv.first_final_score

		# make empty instances of forms
		details_form = CNVDetailsForm(request.POST)
		sample_form = CNVSampleInfoForm(request.POST)
		genuine_form = CNVGenuineArtefactForm(cnv_pk=pk)
		method_form = CNVMethodForm(request.POST)
		finalise_form = CNVFinaliseClassificationForm(cnv_pk=cnv.pk)

		# dict of data to pass to view
		context = {
			#'classification': classification,
			'cnv': cnv,
			'previous_classifications': previous_classifications,
			'previous_full_classifications': previous_full_classifications,
			'answers': answers,
			'comments': comments,
			'result': result,
			'score': score,
			'details_form': details_form,
			'sample_form': sample_form,
			'genuine_form': genuine_form,
			'method_form': method_form,
			'finalise_form': finalise_form,
			'warn': []
		}
		#-------
		
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
			
			# GenuineArtefactForm
			if 'genuine' in request.POST:

				genuine_form = CNVGenuineArtefactForm(request.POST, cnv_pk=cnv.pk)

				if genuine_form.is_valid():
					cleaned_data = genuine_form.cleaned_data

					# genuine - new classification
					if cleaned_data['genuine'] == '1':

						cnv.genuine = '1'

						# if not already initiated, make new classification answers
						if len(answers) == 0:
							cnv.initiate_classification()

					# genuine - use previous classification
					elif cleaned_data['genuine'] == '2':

						# if there isnt a previous classification, throw a warning and stop
						if len(previous_classifications) == 0:

							context['warn'] += ['There are no previous classifications to use.']

						# if there is, update final class to whatever it was previously
						else:

							cnv.genuine = '2'
							cnv.first_final_class = previous_full_classifications[0].second_final_class

					# genuine - not analysed - update final_class to 'not analysed'
					elif cleaned_data['genuine'] == '3':

						cnv.genuine = '3'
						cnv.first_final_class = '5'

					# artefact - set final_class to artefact
					elif cleaned_data['genuine'] == '4':

						cnv.genuine = '4'
						cnv.first_final_class = '6'
						
					cnv.save()

				# reload dict variables for rendering
				result = cnv.display_first_classification()
				context['result'] = result
				context['cnv'] = get_object_or_404(CNV, pk=pk)
				context['genuine_form'] = CNVGenuineArtefactForm(cnv_pk=cnv.pk)
		
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
					
					return render(request, 'acmg_db/cnv_first_check.html', context)		

			# FinaliseClassificationForm
			if 'final_classification' in request.POST:

				# Don't let anyone except the assigned first checker submit the form
				if cnv.status != '0' or request.user != cnv.user_first_checker:

					raise PermissionDenied('You do not have permission to finalise the classification.')

				finalise_form = CNVFinaliseClassificationForm(request.POST, cnv_pk=cnv.pk)

				if finalise_form.is_valid():

					cleaned_data = finalise_form.cleaned_data

					# validation that everything has been completed - make sure all fields are completed, genuine/artefact is set
					if cnv.genuine == '0':

						context['warn'] += ['Select whether the CNV is genuine or artefact']

					if cnv.inheritance == None or cnv.inheritance == '':

						context['warn'] += ['Inheritence pattern has not been set']

					if cnv.genuine  == '2' and (cleaned_data['final_classification'] != previous_full_classifications[0].second_final_class):

						context['warn'] += ['You selected to use the last full classification, but the selected classification does not match']

					if cnv.genuine  == '3' and (cleaned_data['final_classification'] != '7' ):

						context['warn'] += ['This classification was selected as Not Analysed - therefore the only valid option is Not Analysed']

					if cnv.genuine  == '4' and (cleaned_data['final_classification'] != '6' ):

						context['warn'] += ['This classification was selected as Artefect - therefore the only valid option is Artefect']

					# if validation has been passed, finalise first check
					if len(context['warn']) == 0:

						# if anything other than 'dont override' selected, then change the classification
						if cleaned_data['final_classification'] != '8':

							cnv.first_final_class = cleaned_data['final_classification']

						# update status and save
						cnv.status = '1'
						cnv.first_check_date = timezone.now()
						cnv.user_first_checker = request.user
						cnv.save()

						#return redirect('home')
						return redirect('/cnv_pending')
			
			return render(request, 'acmg_db/cnv_first_check.html', context)
	
	return render(request, 'acmg_db/cnv_first_check.html', context)


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_acmg_cnv_classification_first(request):
	"""
	Gets the ajax results from the first_check.html page \
	and stores them in the database - also returns the calculated result.

	This view is for the first check.

	"""

	if request.is_ajax():

		# Get the submitted answers and convert to python object
		classification_answers = request.POST.get('cnvs')
		classification_answers = json.loads(classification_answers)

		# Get the classification pk and load the classification
		cnv_pk = request.POST.get('cnv_pk').strip()
		cnv = get_object_or_404(CNV, pk=cnv_pk)

		# Ensure correct user and status
		if cnv.status != '0' or request.user != cnv.user_first_checker:

			raise PermissionDenied('You do not have permission to start this classification.')
		
		if cnv.method == "Gain":
			correct_number_of_questions = CNVGainClassificationQuestion.objects.all().count()
			if len(classification_answers) != correct_number_of_questions:
				raise Exception('Wrong number of questions')

			# Update the classification answers
			for classification_answer in classification_answers:
				
				pk = classification_answer.strip()

				classification_answer_obj = get_object_or_404(CNVGainClassificationAnswer, pk=pk)

				classification_answer_obj.score = classification_answers[classification_answer][0].strip()

				classification_answer_obj.comment = classification_answers[classification_answer][1].strip()

				classification_answer_obj.save()
			
			
		elif cnv.method == "Loss":
			correct_number_of_questions = CNVLossClassificationQuestion.objects.all().count()
			if len(classification_answers) != correct_number_of_questions:
				raise Exception('Wrong number of questions')
			
			# Update the classification answers
			for classification_answer in classification_answers:
				
				pk = classification_answer.strip()

				classification_answer_obj = get_object_or_404(CNVLossClassificationAnswer, pk=pk)

				classification_answer_obj.score = classification_answers[classification_answer][0].strip()

				classification_answer_obj.comment = classification_answers[classification_answer][1].strip()

				classification_answer_obj.save()

		# update the score in the database
		cnv.first_final_score = cnv.calculate_acmg_score_first()
		if cnv.first_final_score >= 0.99:
			cnv.first_final_class = "4"
		elif 0.90 <= cnv.first_final_score <= 0.98:
			cnv.first_final_class = "3"
		elif -(0.89) <= cnv.first_final_score <= 0.89:
			cnv.first_final_class = "2"
		elif -(0.98) <= cnv.first_final_score <= -(0.90):
			cnv.first_final_class = "1"
		elif cnv.first_final_score <= -(0.99):
			cnv.first_final_class = "0"
		cnv.save()
		
		score = cnv.first_final_score
		
		context = {
			'result': cnv.display_first_classification(),
			'score': score,
		}
		
		html = render_to_string('acmg_db/cnv_acmg_results_first.html', context)

	return HttpResponse(html)


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_cnv_comments(request):
	"""
	Ajax View - when the user clicks the upload comment/file button \
	this updates the comment section of the page. 
	Clipboard paste only works on HTML5 enabled browser.
	"""

	if request.is_ajax():

		cnv_pk = request.POST.get('cnv_pk')
		comment_text = request.POST.get('comment_text')

		cnv_pk = cnv_pk.strip()
		comment_text = comment_text.strip()

		cnv = get_object_or_404(CNV, pk =cnv_pk)

		if len(comment_text) >1: #Check user has entered a comment

			new_comment = CNVUserComment(user=request.user,
								text=comment_text,
								time=timezone.now(),
								classification=cnv)

			new_comment.save()

			#Deal with files selected using the file selector html widget 
			if request.FILES.get('file', False) != False:

				file = request.FILES.get('file')

				new_evidence = CNVEvidence()

				new_evidence.file = file

				new_evidence.comment= new_comment

				new_evidence.save()

			#Deal with images pasted in from the clipboard
			if request.POST.get('image_data') != None: 

				image_data = request.POST.get('image_data')

				#strip of any leading characters
				image_data = image_data.strip() 

				#add appropiate file header
				dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$') 

				ImageData = dataUrlPattern.match(image_data).group(2)

				ImageData = base64.b64decode(ImageData) #to binary

				new_evidence = CNVEvidence()

				new_evidence.comment= new_comment

				#save image
				img_file_string = '{}_{}_clip_image.png'.format(cnv.pk,new_comment.pk)
				new_evidence.file.save(img_file_string, ContentFile(ImageData)) 

				new_evidence.save()

		comments = CNVUserComment.objects.filter(classification=cnv, visible=True)

		html = render_to_string('acmg_db/ajax_comments.html',
								{'comments': comments, 'user': request.user})

		return HttpResponse(html)

	else:

		raise Http404
