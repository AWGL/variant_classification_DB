import json
import base64
import re

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

from acmg_db.forms import CNVSampleInfoForm, VariantInfoForm, GenuineArtefactForm, FinaliseClassificationForm, TranscriptForm
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
		#previous_classifications = Classification.objects.filter(variant=variant,genome=classification.sample.genome, status__in=['2', '3']).exclude(pk=classification.pk).order_by('-second_check_date')
		#previous_full_classifications = previous_classifications.filter(genuine='1').order_by('-second_check_date')
		if cnv.gain_loss == "Gain":
			answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
			if len(answers) == 0:
				cnv.initiate_classification()
				answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
		elif cnv.gain_loss == "Loss":
			answers = CNVLossClassificationAnswer.objects.filter(cnv=cnv)
			if len(answers) == 0:
				cnv.initiate_classification()
				answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
		comments = CNVUserComment.objects.filter(classification=cnv, visible=True)
		result = cnv.first_final_class  # current class to display
		score = cnv.first_final_score

		# make empty instances of forms
		#sample_form = CNVSampleInfoForm(cnv_pk=cnv.pk, options=PANEL_OPTIONS)
		#transcript_form = TranscriptForm(classification_pk=classification.pk, options=fixed_refseq_options)
		#variant_form = VariantInfoForm(classification_pk=classification.pk, options=fixed_refseq_options)
		#genuine_form = GenuineArtefactForm(classification_pk=classification.pk)
		#finalise_form = FinaliseClassificationForm(classification_pk=classification.pk)

		# dict of data to pass to view
		context = {
			#'classification': classification,
			'cnv': cnv,
			#'previous_classifications': previous_classifications,
			#'previous_full_classifications': previous_full_classifications,
			'answers': answers,
			'comments': comments,
			'result': result,
			'score': score,
			#'sample_form': sample_form,
			#'transcript_form': transcript_form,
			#'variant_form': variant_form,
			#'genuine_form': genuine_form,
			#'finalise_form': finalise_form,
			'warn': []
		}
		#-------
		
		"""
		# if a form is submitted
		if request.method == 'POST':

			# SampleInfoForm
			if 'affected_with' in request.POST:

				sample_form = CNVSampleInfoForm(request.POST, cnv_pk=cnv.pk, options=PANEL_OPTIONS)

				# load in data
				if sample_form.is_valid():

					cleaned_data = sample_form.cleaned_data
					sample = cnv.sample
					sample.affected_with =  cleaned_data['affected_with']
					sample.other_changes = cleaned_data['other_changes']
					sample.save()
					
				# reload dict variables for rendering
				context['cnv'] = get_object_or_404(CNV, pk=pk)
				context['sample_form'] = CNVSampleInfoForm(cnv_pk=cnv.pk, options=PANEL_OPTIONS)
				

			# TranscriptForm
			if 'select_transcript' in request.POST:
				transcript_form = TranscriptForm(request.POST, classification_pk=classification.pk, options=fixed_refseq_options)
				if transcript_form.is_valid():
					cleaned_data = transcript_form.cleaned_data
					select_transcript = cleaned_data['select_transcript']
					selected_transcript_variant = get_object_or_404(TranscriptVariant, pk=select_transcript)
					classification.selected_transcript_variant = selected_transcript_variant
					classification.save()
				# reload dict variables for rendering
				context['classification'] = classification
				context['transcript_form'] = TranscriptForm(classification_pk=classification.pk, options=fixed_refseq_options)
				context['variant_form'] = VariantInfoForm(classification_pk=classification.pk, options=fixed_refseq_options)

			# VariantInfoForm
			if 'inheritance_pattern' in request.POST:

				variant_form = VariantInfoForm(request.POST, classification_pk = classification.pk, options=fixed_refseq_options)

				if variant_form.is_valid():

					cleaned_data = variant_form.cleaned_data

					classification.is_trio_de_novo = cleaned_data['is_trio_de_novo']

					genotype = cleaned_data['genotype']

					if genotype == 'Het':
						genotype = 1

					elif genotype == 'Hom':
						genotype = 2

					elif genotype == 'Hemi':
						genotype = 3

					elif genotype == 'Mosaic':
						genotype = 4

					else:
						genotype = None

					classification.genotype = genotype

					classification.save()

					# genes section
					gene = classification.selected_transcript_variant.transcript.gene
					gene.inheritance_pattern = cleaned_data['inheritance_pattern']
					gene.conditions = cleaned_data['conditions']
					gene.save()

				# reload dict variables for rendering
				context['classification'] = classification
				context['variant_form'] = VariantInfoForm(classification_pk=classification.pk, options=fixed_refseq_options)

			# GenuineArtefactForm
			if 'genuine' in request.POST:

				genuine_form = GenuineArtefactForm(request.POST, classification_pk=classification.pk)

				if genuine_form.is_valid():
					cleaned_data = genuine_form.cleaned_data

					# genuine - new classification
					if cleaned_data['genuine'] == '1':

						classification.genuine = '1'

						# if not already initiated, make new classification answers
						if len(answers) == 0:
							classification.initiate_classification()

						# save final_class as output of calculate_acmg_score_first
						classification.first_final_class = classification.calculate_acmg_score_first()

					# genuine - use previous classification
					elif cleaned_data['genuine'] == '2':

						# if there isnt a previous classification, throw a warning and stop
						if len(previous_classifications) == 0:

							context['warn'] += ['There are no previous classifications to use.']

						# if there is, update final class to whatever it was previously
						else:

							classification.genuine = '2'
							classification.first_final_class = previous_full_classifications[0].second_final_class

					# genuine - not analysed - update final_class to 'not analysed'
					elif cleaned_data['genuine'] == '3':

						classification.genuine = '3'
						classification.first_final_class = '7'

					# artefact - set final_class to artefact
					elif cleaned_data['genuine'] == '4':

						classification.genuine = '4'
						classification.first_final_class = '6'
						
					classification.save()

				# reload dict variables for rendering
				result = classification.display_first_classification()
				context['result'] = result
				context['answers'] = ClassificationAnswer.objects.filter(classification=classification).order_by('classification_question__order')
				context['classification'] = get_object_or_404(Classification, pk=pk)
				context['genuine_form'] = GenuineArtefactForm(classification_pk=classification.pk)


			# FinaliseClassificationForm
			if 'final_classification' in request.POST:

				# Don't let anyone except the assigned first checker submit the form
				if classification.status != '0' or request.user != classification.user_first_checker:

					raise PermissionDenied('You do not have permission to finalise the classification.')

				finalise_form = FinaliseClassificationForm(request.POST, classification_pk=classification.pk)

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

					if classification.genuine  == '3' and (cleaned_data['final_classification'] != '7' ):

						context['warn'] += ['This classification was selected as Not Analysed - therefore the only valid option is NA']

					if classification.genuine  == '4' and (cleaned_data['final_classification'] != '6' ):

						context['warn'] += ['This classification was selected as Artefect - therefore the only valid option is Artefect']

					# if validation has been passed, finalise first check
					if len(context['warn']) == 0:
						
						# if new classification, pull score from the acmg section and save to final class
						if classification.genuine == '1':

							classification.first_final_class = classification.calculate_acmg_score_first()

						# if anything other than 'dont override' selected, then change the classification
						if cleaned_data['final_classification'] != '8':

							classification.first_final_class = cleaned_data['final_classification']

						# update status and save
						classification.status = '1'
						classification.first_check_date = timezone.now()
						classification.user_first_checker = request.user
						classification.save()

						#return redirect('home')
						return redirect('/pending_classifications?sample={}&worksheet={}&panel={}'.format(
							classification.sample.sample_name_only,
							classification.sample.worklist.name,
							classification.sample.analysis_performed.panel
						))
			
			return render(request, 'acmg_db/first_check.html', context)
	"""	
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
		
		if cnv.gain_loss == "Gain":
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
			
			
		elif cnv.gain_loss == "Loss":
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
			cnv.first_final_class = "Pathogenic"
		elif 0.90 <= cnv.first_final_score <= 0.98:
			cnv.first_final_class = "Likely Pathogenic"
		elif -(0.89) <= cnv.first_final_score <= 0.89:
			cnv.first_final_class = "VUS"
		elif -(0.98) <= cnv.first_final_score <= -(0.90):
			cnv.first_final_class = "Likely Benign"
		elif cnv.first_final_score <= -(0.99):
			cnv.first_final_class = "Benign"
		cnv.save()
		
		score = cnv.first_final_score
		
		context = {
			'result': cnv.first_final_class,
			'score': score,
		}
		
		html = render_to_string('acmg_db/acmg_results_first.html', context)

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

				new_evidence = Evidence()

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

				new_evidence = Evidence()

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
