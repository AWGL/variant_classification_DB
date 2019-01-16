from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.conf import settings
from .models import *
from .utils.variant_utils import *
from .utils.acmg_worksheet_parser import *
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
import json
import base64
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from io import TextIOWrapper


@login_required
def home(request):
	"""
	The view for the home page.

	Allows users to upload a file of variants to classify.
	"""
	# make a list of all panels and pass to the form to populate the dropdown
	all_panels = Panel.objects.all()
	panel_options = []
	for n, item in enumerate(all_panels):
		panel_options.append((str(n+1), item.panel))

	form = VariantFileUploadForm(options=panel_options)

	# make empty dict for context
	context = {
		'form': form, 
		'error': None,
		'warn': None,
		'success': None,
		'params': None
	}

	if request.POST:

		form = VariantFileUploadForm(request.POST, request.FILES, options=panel_options)
		if form.is_valid():

			# get panel
			analysis_performed_index = form.cleaned_data['panel_applied']
			analysis_performed = ""
			for panel in panel_options:
				print(panel[0])
				if panel[0] == analysis_performed_index:
					analysis_performed = panel[1]

			# get affected with
			affected_with = form.cleaned_data['affected_with']

			# process tsv file
			raw_file = request.FILES['variant_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			
			df, meta_dict = load_worksheet(utf_file)
			variants_dict = process_data(df, meta_dict)

			error = variants_dict["errors"]
			warn = variants_dict["warnings"]

			# if theres any errors, throw error and stop
			if len(error) > 0:
				error += ["ERROR: Didn't upload any files, check your input file and try again"]
				context['error'] = error
				context['warn'] = warn

			
			# else do the upload (warnings are thrown but upload continues)
			else:
				sample_id = variants_dict['sample_id']
				worksheet_id = variants_dict['worksheet_id']

				# add worksheet
				worksheet, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)

				# add sample
				sample, created = Sample.objects.get_or_create(
					name = sample_id,
					worklist = worksheet,
					affected_with = affected_with,
					analysis_performed = analysis_performed,  # TODO move this into classifications - currently in sample - multiple panels might be run on the same sample so there might be multiple analyses
					analysis_complete = False,
					other_changes = ''
					)

				# TODO - make validation if worklist and sample have already been seen? - either add a warning or stop the upload

				# add variants
				for item in variants_dict['variants']:
					print(item)
					var = item['Variant']
					variant_data = process_variant_input(var)

					key = variant_data[5]
					variant_hash = variant_data[0]
					chromosome = variant_data[1]
					position = variant_data[2]
					ref = variant_data[3]
					alt = variant_data[4]
					
					variant, created = Variant.objects.get_or_create(
						key = key,
						variant_hash = variant_hash,
						chromosome = chromosome,
						position = position,
						ref = ref,
						alt = alt
						)

					gene_query = item['Gene']
					gene, created = Gene.objects.get_or_create(
						name = gene_query,
						)

					transcript_query = item['Transcript']
					hgvs_c_query = item['HGVSc']
					hgvs_p_query = item['HGVSp']

					try:
						transcript = Transcript.objects.get(name=transcript_query)
					except Transcript.DoesNotExist:
						refseq_transcripts, ensembl_warn = get_refseq_transcripts(transcript_query, hgvs_c_query)
						warn += ensembl_warn

						if len(refseq_transcripts) == 1:
							refseq_selected = refseq_transcripts[0]
						else:
							refseq_selected = None

						transcript = Transcript.objects.create(
							name = transcript_query,
							gene = gene,
							refseq_options = json.dumps(refseq_transcripts),
							refseq_selected = refseq_selected
						)

					exon_query = item['Location']
					transcript_variant, created = TranscriptVariant.objects.get_or_create(
						variant = variant,
						transcript = transcript,
						hgvs_c = hgvs_c_query,
						hgvs_p = hgvs_p_query,
						exon = exon_query

						)

					new_classification_obj = Classification.objects.create(
						variant= variant,
						sample = sample,
						creation_date = timezone.now(),
						user_creator = request.user,
						status = '0',
						is_trio_de_novo = False,
						final_class = '7',
						selected_transcript_variant = transcript_variant
						)

					new_classification_obj.save()
					#new_classification_obj.initiate_classification()


				success = ['Worksheet {} - Sample {} - Upload completed '.format(worksheet_id, sample_id)]
				params = '?worksheet={}&sample={}'.format(worksheet_id, sample_id)

				context = {
					'form': form, 
					'error': error,
					'warn': warn,
					'success': success,
					'params': params
					}


	return render(request, 'acmg_db/home.html', context)


#--------------------------------------------------------------------------------------------------
@login_required
def manual_input(request):
	"""
	The view for the manual input page.

	Allows users to create a new classification for a variant.
	"""

	form = SearchForm()
	context = {
		'form': form,
		'error': [], 
	}

	# If the user has searched for something
	#if request.GET.get('variant') != '' and request.GET.get('variant') != None:
	if request.POST:
		form = SearchForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			
			# Get the user input from the form.
			search_query = cleaned_data['variant'].strip()
			gene_query = cleaned_data['gene'].strip()
			transcript_query = cleaned_data['transcript'].strip()
			hgvs_c_query = cleaned_data['hgvs_c'].strip()
			hgvs_p_query = cleaned_data['hgvs_p'].strip()
			exon_query = cleaned_data['exon'].strip()

			sample_name_query = cleaned_data['sample_name'].strip()
			affected_with_query = cleaned_data['affected_with'].strip()
			analysis_performed_query = cleaned_data['analysis_performed'].strip()
			other_changes_query = cleaned_data['other_changes'].strip()
			worklist_query = cleaned_data['worklist'].strip()
		
			# Validate the variant using Mutalyzer - i.e. is the variant real?
			# We only check if the chr-pos-ref-alt is real not if gene etc is correct.
			#variant_info = get_variant_info_mutalzer(search_query, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)

			# Add variant to DB if not already present
			# Get varaint information e.g. chr, pos, ref, alt from the input

			variant_data = process_variant_input(search_query)

			variant_hash = variant_data[0]
			chromosome = variant_data[1]
			position = variant_data[2]
			ref = variant_data[3]
			alt = variant_data[4]
			key = variant_data[5]

		
			# Create the objects
			worklist, created = Worklist.objects.get_or_create(
				name = worklist_query
			)

			sample, created = Sample.objects.get_or_create(
				name = sample_name_query,
				worklist = worklist,
				affected_with = affected_with_query,
				analysis_performed = analysis_performed_query,
				analysis_complete = False,
				other_changes = other_changes_query
			)

			variant, created = Variant.objects.get_or_create(
				key = key,
				variant_hash = variant_hash,
				chromosome = chromosome,
				position = position,
				ref = ref,
				alt = alt
			)

			gene, created = Gene.objects.get_or_create(
				name = gene_query
			)

			try:
				transcript = Transcript.objects.get(name=transcript_query)
			except Transcript.DoesNotExist:
				refseq_transcripts, ensembl_warn = get_refseq_transcripts(transcript_query, hgvs_c_query)
				#warn += ensembl_warn

				if len(refseq_transcripts) == 1:
					refseq_selected = refseq_transcripts[0]
				else:
					refseq_selected = None

				transcript = Transcript.objects.create(
					name = transcript_query,
					gene = gene,
					refseq_options = json.dumps(refseq_transcripts),
					refseq_selected = refseq_selected
				)

			transcript_variant, created = TranscriptVariant.objects.get_or_create(
				variant = variant,
				transcript = transcript,
				hgvs_c = hgvs_c_query,
				hgvs_p = hgvs_p_query,
				exon = exon_query
			)

			new_classification_obj = Classification.objects.create(
				variant= variant,
				sample = sample,
				creation_date = timezone.now(),
				user_creator = request.user,
				status = '0',
				is_trio_de_novo = False,
				final_class = '7',
				selected_transcript_variant = transcript_variant
			)

			new_classification_obj.save()
			#new_classification_obj.initiate_classification()
			
			# Go to the new_classification page.
			return redirect(new_classification, new_classification_obj.pk)

	return render(request, 'acmg_db/manual_input.html', context)


#--------------------------------------------------------------------------------------------------
@login_required
def new_classification(request, pk):
	"""
	Page for entering new classifications.

	Has the following featues:

	1) Form for entering classification data e.g. sample_lab_number
	2) ACMG classifier.
	3) Comments and Evidence.

	"""

	classification = get_object_or_404(Classification, pk=pk)

	#reject if wrong status or user
	if classification.status != '0' or request.user != classification.user_creator:
		return HttpResponseForbidden()

	else:
		# Get data to render form
		variant = classification.variant

		previous_classifications = Classification.objects.filter(variant=variant, status__in=['2', '3']).exclude(pk=classification.pk).order_by('-second_check_date')
		previous_full_classifications = previous_classifications.filter(genuine='1').order_by('-second_check_date')

		answers = ClassificationAnswer.objects.filter(classification=classification).order_by('classification_question__order')
		comments = UserComment.objects.filter(classification=classification)

		result = classification.display_final_classification  # current class to display

		transcript = classification.selected_transcript_variant.transcript
		refseq_options = Transcript.objects.get(name=transcript.name).change_refseq_selected()  # list of refseq ids linked to the ensembl id

		# make empty instances of forms
		patient_form = PatientInfoForm(classification_pk=classification.pk)
		variant_form = VariantInfoForm(classification_pk=classification.pk, options=refseq_options)
		genuine_form = GenuineArtefactForm(classification_pk=classification.pk)
		finalise_form = FinaliseClassificationForm(classification_pk=classification.pk)

		# dict of data to pass to view
		context = {
			'classification': classification,
			'variant': variant,
			'previous_classifications': previous_classifications,
			'previous_full_classifications': previous_full_classifications,
			'answers': answers,
			'comments': comments,
			'result': result,
			'patient_form': patient_form,
			'variant_form': variant_form,
			'genuine_form': genuine_form,
			'finalise_form': finalise_form,
			'warn': []
		}
		
		#-----------------------------------------------
		# if a form is submitted
		if request.method == 'POST':

			# PatientInfoForm
			if 'affected_with' in request.POST:
				patient_form = PatientInfoForm(request.POST, classification_pk=classification.pk)

				# load in data
				if patient_form.is_valid():
					cleaned_data = patient_form.cleaned_data
					sample = Sample.objects.filter(name=classification.sample.name)
					sample.update(
						affected_with = cleaned_data['affected_with'],
						other_changes = cleaned_data['other_changes']
					)
				
				# reload dict variables for rendering
				context['classification'] = get_object_or_404(Classification, pk=pk)
				context['patient_form'] = PatientInfoForm(classification_pk=classification.pk)


			# VariantInfoForm
			if 'inheritance_pattern' in request.POST:
				variant_form = VariantInfoForm(request.POST, classification_pk = classification.pk, options=refseq_options)

				if variant_form.is_valid():
					cleaned_data = variant_form.cleaned_data

					# transcript section
					transcript_obj = Transcript.objects.filter(name=transcript.name)
					for item in refseq_options:
						if item[0] == cleaned_data['select_transcript']:
							if item[1] == 'Other':
								refseq_new = cleaned_data['other']
								# validate input
								if refseq_new == '':
									context['warn'] += ['Transcript not set - transcript ID cannot be empty.']
								elif not refseq_new.startswith('NM_'):
									context['warn'] += ['Transcript not set - transcript ID is not a RefSeq ID.']
								# if validation passed, update refseq id
								else:
									transcript_obj.update(refseq_selected = refseq_new)
							# if item is from the list, update refseq id
							else:
								transcript_obj.update(refseq_selected = item[1])

					# genes section
					gene = Gene.objects.filter(name=classification.selected_transcript_variant.transcript.gene.name)
					gene.update(
						inheritance_pattern = cleaned_data['inheritance_pattern'],
						conditions = cleaned_data['conditions']
					)

					# trio de novo section
					classification.is_trio_de_novo = cleaned_data['is_trio_de_novo']
					classification.save()
					
				# reload dict variables for rendering
				context['classification'] = get_object_or_404(Classification, pk=pk)
				context['variant_form'] = VariantInfoForm(classification_pk=classification.pk, options=refseq_options)


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
						classification.final_class = classification.calculate_acmg_score_first()[1]

					# genuine - use previous classification - update final class to whatever it was previously
					elif cleaned_data['genuine'] == '2':
						classification.genuine = '2'
						classification.final_class = previous_full_classifications[0].final_class

					# genuine - not analysed - update final_class to 'not analysed'
					elif cleaned_data['genuine'] == '3':
						classification.genuine = '3'
						classification.final_class = '7'

					# artefact - set final_class to artefact
					elif cleaned_data['genuine'] == '4':
						classification.genuine = '4'
						classification.final_class = '6'
						
					classification.save()

				# reload dict variables for rendering
				result = classification.display_final_classification
				context['result'] = result
				context['answers'] = ClassificationAnswer.objects.filter(classification=classification)
				context['classification'] = get_object_or_404(Classification, pk=pk)
				context['genuine_form'] = GenuineArtefactForm(classification_pk=classification.pk)


			# FinaliseClassificationForm
			if 'final_classification' in request.POST:
				finalise_form = FinaliseClassificationForm(request.POST, classification_pk=classification.pk)

				if finalise_form.is_valid():
					# TODO add validation e.g. make sure all fields are completed, make sure genuine/artefact is set
					cleaned_data = finalise_form.cleaned_data
					
					# if new classification, pull score from the acmg section and save to final class
					if classification.genuine == '1':
						classification.final_class = classification.calculate_acmg_score_first()[1]

					# if anything other than 'dont override' selected, then change the classification
					if cleaned_data['final_classification'] != '8':
						classification.final_class = cleaned_data['final_classification']

					# update status and save
					classification.status = '1'
					classification.first_check_date = timezone.now()
					classification.user_first_checker = request.user
					classification.save()

					return redirect(home)


			return render(request, 'acmg_db/new_classifications.html', context)
		return render(request, 'acmg_db/new_classifications.html', context)


#--------------------------------------------------------------------------------------------------
@login_required
def ajax_acmg_classification_first(request):
	"""
	Gets the ajax results from the new_classifcations.html page \
	and stores them in the database - also returns the calculated result.


	For the first analysis
	"""


	if request.is_ajax():

		# Get the submitted answers and convert to python object
		classification_answers = request.POST.get('classifications')
		classification_answers = json.loads(classification_answers)

		# Get the classification pk and load the classification
		classification_pk = request.POST.get('classification_pk').strip()
		classification = get_object_or_404(Classification, pk =classification_pk)

		# Update the classification answers
		for classification_answer in classification_answers:

			pk = classification_answer.strip()

			classification_answer_obj = get_object_or_404(ClassificationAnswer, pk=pk)

			print (classification_answers[classification_answer])

			classification_answer_obj.strength_first = classification_answers[classification_answer][1].strip()

			classification_answer_obj.selected_first = classification_answers[classification_answer][2].strip()

			classification_answer_obj.comment = classification_answers[classification_answer][3].strip()

			classification_answer_obj.save()

		# Calculate the score
		result = classification.calculate_acmg_score_first()[0]

		# update the score in the database
		classification.final_class = classification.calculate_acmg_score_first()[1]
		classification.save()

		html = render_to_string('acmg_db/acmg_results_first.html', {'result': result})

	return HttpResponse(html)


#--------------------------------------------------------------------------------------------------
@login_required
def ajax_acmg_classification_second(request):
	"""
	Gets the ajax results from the new_classifcations.html page \
	and stores them in the database - also returns the calculated result.

	For the second analysis
	"""

	if request.is_ajax():

		# Get the submitted answers and convert to python object
		classification_answers = request.POST.get('classifications')
		classification_answers = json.loads(classification_answers)

		# Get the classification pk and load the classification
		classification_pk = request.POST.get('classification_pk').strip()
		classification = get_object_or_404(Classification, pk =classification_pk)

		# Update the classification answers
		for classification_answer in classification_answers:

			pk = classification_answer.strip()

			classification_answer_obj = get_object_or_404(ClassificationAnswer, pk=pk)

			print (classification_answers[classification_answer])

			classification_answer_obj.strength_second= classification_answers[classification_answer][1].strip()

			classification_answer_obj.selected_second = classification_answers[classification_answer][2].strip()

			classification_answer_obj.comment = classification_answers[classification_answer][3].strip()

			classification_answer_obj.save()

		acmg_result_first = classification.calculate_acmg_score_first()[0]

		acmg_result_second = classification.calculate_acmg_score_second()

		html = render_to_string('acmg_db/acmg_results_second.html', {'result_first': acmg_result_first, 'result_second': acmg_result_second})

	return HttpResponse(html)


#--------------------------------------------------------------------------------------------------
@login_required
def ajax_comments(request):
	"""
	Ajax View - when the user clicks the upload comment/file button \
	this updates the comment section of the page. 
	Clipboard paste only works on HTML5 enabled browser.
	"""

	if request.is_ajax():

		classification_pk = request.POST.get('classification_pk')
		comment_text = request.POST.get('comment_text')

		classification_pk = classification_pk.strip()
		comment_text = comment_text.strip()

		classification = get_object_or_404(Classification, pk =classification_pk)

		if len(comment_text) >1: #Check user has entered a comment

			new_comment = UserComment(user=request.user,
								text=comment_text,
								time=timezone.now(),
								classification=classification)

			new_comment.save()

			#Deal with files selected using the file selector html widget 
			if request.FILES.get("file", False) != False:

				file = request.FILES.get("file")

				new_evidence = Evidence()

				new_evidence.file = file

				new_evidence.comment= new_comment

				new_evidence.save()

			#Deal with images pasted in from the clipboard
			if request.POST.get("image_data") != None: 

				image_data = request.POST.get("image_data")
				#strip of any leading characters
				image_data = image_data.strip() 

				#add appropiate file header
				dataUrlPattern = re.compile("data:image/(png|jpeg);base64,(.*)$") 

				ImageData = dataUrlPattern.match(image_data).group(2)

				ImageData = base64.b64decode(ImageData) #to binary

				new_evidence = Evidence()

				new_evidence.comment= new_comment

				#save image
				img_file_string = "{}_{}_clip_image.png".format(classification.pk,new_comment.pk)
				new_evidence.file.save(img_file_string, ContentFile(ImageData)) 

				new_evidence.save()

		comments = UserComment.objects.filter(classification=classification)

		html = render_to_string("acmg_db/ajax_comments.html",
								{"comments": comments})

		return HttpResponse(html)

	else:

		raise Http404



#--------------------------------------------------------------------------------------------------
@login_required
def view_previous_classifications(request):
	"""
	Page to view previous classifications

	"""

	classifications = Classification.objects.all().order_by('-creation_date')

	return render(request, 'acmg_db/view_classifications.html', {'classifications': classifications})


@login_required
def view_classification(request, pk):
	"""
	View a read only version of a classification of a variant

	"""

	classification = get_object_or_404(Classification, pk=pk)

	# Allow users to achieve the classification
	if request.method == 'POST':

		form = ArchiveClassificationForm(request.POST, classification_pk = classification.pk)

		if form.is_valid():

			# Update status to archived
			cleaned_data = form.cleaned_data
			classification.status = '3'
			classification.save()
			return redirect(home)

	else:

		# Otherwise just get the information for display
		classification_answers = (ClassificationAnswer.objects.filter(classification=classification)
			.order_by('classification_question__order'))

		comments = UserComment.objects.filter(classification=classification)

		acmg_result = classification.calculate_acmg_score_second()

		form = ArchiveClassificationForm(classification_pk = classification.pk)

		return render(request, 'acmg_db/view_classification.html', {'classification': classification,
									 'classification_answers': classification_answers,
									 'comments': comments,
									 'acmg_result': acmg_result,
									 'form': form})

@login_required
def second_check(request, pk):
	"""
	Page for user to perform second check.

	The user performs a seperate analysis deciding whether to agree or \
	disagree with the first analysis.

	"""

	classification = get_object_or_404(Classification, pk=pk)
	variant = classification.variant

	# Forbidden if status is not correct
	if classification.status != '1':

		return HttpResponseForbidden()

	if request.method == 'POST':

		sample_form = ClassificationInformationSecondCheckForm(request.POST, classification_pk = classification.pk)

		if sample_form.is_valid():

			# Update models
			cleaned_data = sample_form.cleaned_data
			
			classification.is_trio_de_novo = cleaned_data['is_trio_de_novo']
			classification.selected_transcript_variant.transcript.gene.inheritance_pattern = cleaned_data['inheritance_pattern']
			classification.final_class = cleaned_data['final_classification']
			classification.selected_transcript_variant.transcript.gene.conditions = cleaned_data['conditions']
			classification.status = '2'
			classification.second_check_date = timezone.now()
			classification.user_second_checker = request.user

			classification.save()

			return redirect(home)


	else:

		# Get all the previous classifications of this variant
		previous_classifications = Classification.objects.filter(variant=variant).exclude(pk=classification.pk).order_by('-second_check_date')

		# Get the answers to the ACMG criteria for this classification
		classification_answers = ClassificationAnswer.objects.filter(classification=classification).order_by('classification_question__order')

		comments = UserComment.objects.filter(classification=classification)

		sample_form = ClassificationInformationSecondCheckForm(classification_pk=classification.pk)

		acmg_result_first = classification.calculate_acmg_score_first()[0]

		acmg_result_second = classification.calculate_acmg_score_second()

		return render(request, 'acmg_db/second_check.html', {'classification': classification,
									 'classification_answers': classification_answers,
									 'comments': comments,
									 'answers': classification_answers,
									 'sample_form': sample_form,
									 'acmg_result_first': acmg_result_first,
									 'acmg_result_second': acmg_result_second,
									 'previous_classifications': previous_classifications})

def signup(request):
	"""
	Allow users to sign up
	User accounts are inactive by default - an admin must activate it using the admin page.

	"""

	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			user.is_active = False
			user.save()
			return redirect('home')
	else:
		form = UserCreationForm()
		return render(request, 'acmg_db/signup.html', {'form': form})






