import json

from ..forms import SampleInfoFormSecondCheck, VariantInfoFormSecondCheck, FinaliseClassificationSecondCheckForm
from ..models import *

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse

# GLOBAL VARIABLES
# list of all panels to populate dropdown lists
PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_acmg_classification_second(request):
	"""
	Gets the ajax results from the new_classifcations.html page \
	and stores them in the database - also returns the calculated result.

	This view is for the second check.
	"""

	if request.is_ajax():

		# Get the submitted answers and convert to python object
		classification_answers = request.POST.get('classifications')
		classification_answers = json.loads(classification_answers)

		# Get the classification pk and load the classification
		classification_pk = request.POST.get('classification_pk').strip()
		classification = get_object_or_404(Classification, pk =classification_pk)

		# Ensure correct user and status
		if classification.status != '1' or request.user != classification.user_second_checker:

			raise PermissionDenied('You do not have permission to start this classification.')

		# Check we have every question
		correct_number_of_questions = ClassificationQuestion.objects.all().count()

		if len(classification_answers) != correct_number_of_questions:

			raise Exception('Wrong number of questions')


		# Update the classification answers
		for classification_answer in classification_answers:

			pk = classification_answer.strip()

			classification_answer_obj = get_object_or_404(ClassificationAnswer, pk=pk)

			classification_answer_obj.strength_second= classification_answers[classification_answer][1].strip()

			classification_answer_obj.selected_second = classification_answers[classification_answer][2].strip()

			classification_answer_obj.comment = classification_answers[classification_answer][3].strip()

			classification_answer_obj.save()

		acmg_result_first = classification.display_first_classification()

		# update the score in the database
		classification.second_final_class = classification.calculate_acmg_score_second()
		classification.save()

		acmg_result_second = classification.display_final_classification()

		html = render_to_string('acmg_db/acmg_results_second.html', {'result_first': acmg_result_first, 'result_second': acmg_result_second})

	return HttpResponse(html)


#--------------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def second_check(request, pk):
	"""
	Page for entering doing a second check classifications.

	"""

	classification = get_object_or_404(Classification, pk=pk)

	# Assign second check to first person to click the link
	if classification.user_second_checker == None:

		classification.user_second_checker = request.user
		classification.save()

	#reject if wrong status or user
	if classification.status != '1' or request.user != classification.user_second_checker:

		raise PermissionDenied(f'You do not have permission to perform the second check. It is assigned to {request.user}')

	else:
		# Get data to render form
		variant = classification.variant

		previous_classifications = Classification.objects.filter(variant=variant, status__in=['2', '3']).exclude(pk=classification.pk).order_by('-second_check_date')
		previous_full_classifications = previous_classifications.filter(genuine='1').order_by('-second_check_date')

		answers = ClassificationAnswer.objects.filter(classification=classification).order_by('classification_question__order')
		comments = UserComment.objects.filter(classification=classification, visible=True)

		result_first = classification.display_first_classification()
		result_second = classification.display_final_classification()

		if result_second == 'VUS - contradictory evidence provided':

			result_second = 'Contradictory evidence provided'

		transcript = classification.selected_transcript_variant.transcript

		refseq_options = TranscriptVariant.objects.filter(variant=variant)
		fixed_refseq_options = []

		# Get relevant options for the variant transcripts
		for transcript_var in refseq_options:

			fixed_refseq_options.append((transcript_var.pk, transcript_var.transcript.name + ' - ' + transcript_var.transcript.gene.name + ' - ' + transcript_var.consequence))

		# make empty instances of forms
		sample_form = SampleInfoFormSecondCheck(classification_pk=classification.pk, options=PANEL_OPTIONS)
		variant_form = VariantInfoFormSecondCheck(classification_pk=classification.pk, options=fixed_refseq_options)
		finalise_form = FinaliseClassificationSecondCheckForm(classification_pk=classification.pk)

		# dict of data to pass to view
		context = {
			'classification': classification,
			'variant': variant,
			'previous_classifications': previous_classifications,
			'previous_full_classifications': previous_full_classifications,
			'answers': answers,
			'comments': comments,
			'result_first': result_first,
			'result_second': result_second,
			'sample_form': sample_form,
			'variant_form': variant_form,
			'finalise_form': finalise_form,
			'warn': []
		}
		
		#-----------------------------------------------
		# if a form is submitted
		if request.method == 'POST':

			# SampleInfoForm
			if 'affected_with' in request.POST:

				sample_form = SampleInfoFormSecondCheck(request.POST, classification_pk=classification.pk, options=PANEL_OPTIONS)

				# load in data
				if sample_form.is_valid():

					cleaned_data = sample_form.cleaned_data

					panel = get_object_or_404(Panel, panel = cleaned_data['analysis_performed'].lower())

					sample = classification.sample
					sample.analysis_performed = panel
					sample.affected_with =  cleaned_data['affected_with']
					sample.other_changes = cleaned_data['other_changes']
					sample.save()
					
				
				# reload dict variables for rendering
				context['classification'] = classification
				context['sample_form'] = SampleInfoFormSecondCheck(classification_pk=classification.pk, options=PANEL_OPTIONS)

			# VariantInfoForm
			if 'inheritance_pattern' in request.POST:

				variant_form = VariantInfoFormSecondCheck(request.POST, classification_pk = classification.pk, options=fixed_refseq_options)

				if variant_form.is_valid():

					cleaned_data = variant_form.cleaned_data

					# transcript section
					select_transcript = cleaned_data['select_transcript']
					selected_transcript_variant = get_object_or_404(TranscriptVariant, pk=select_transcript)
					classification.selected_transcript_variant = selected_transcript_variant
					classification.is_trio_de_novo = cleaned_data['is_trio_de_novo']
					classification.save()

					# genes section
					gene = classification.selected_transcript_variant.transcript.gene
					gene.inheritance_pattern = cleaned_data['inheritance_pattern']
					gene.conditions = cleaned_data['conditions']
					gene.save()

				# reload dict variables for rendering
				context['classification'] = classification
				context['variant_form'] = VariantInfoFormSecondCheck(classification_pk=classification.pk, options=fixed_refseq_options)

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
		return render(request, 'acmg_db/second_check.html', context)
