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
	# make empty dict for context
	form = VariantFileUploadForm()
	context = {
		'form': form, 
		'error': None,
		'warn': None,
		'success': None,
		'params': None
	}

	if request.POST:

		form = VariantFileUploadForm(request.POST, request.FILES)
		if form.is_valid():

			# get other options - change when I've figured out what they are
			analysis_performed = form.cleaned_data['analysis_performed']
			affected_with = form.cleaned_data['affected_with']

			# process tsv file
			raw_file = request.FILES['variant_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			
			df, meta_dict = load_worksheet(utf_file)
			variants_json, variants_dict = process_data(df, meta_dict)
			print(variants_json) # change - dont need json and python dict

			error = variants_dict["errors"]
			warn = variants_dict["warnings"]

			# if theres any errors, throw error and stop
			if len(error) > 0:
				error += ["ERROR: Didn't upload any files, check your input file and try again"]
				context['error'] = error
				context['warn'] = warn

			
			# else do the upload (warnings are thrown but upload continues)
			else:
				#### do upload here!!!!!
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
					analysis_performed = analysis_performed,
					analysis_complete = False,
					other_changes = ''
					)

				# TODO - make validation if worklist and sample have already been seen?

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
						name = gene_query
						)

					transcript_query = item['Transcript']
					transcript, created = Transcript.objects.get_or_create(
						name = transcript_query,
						gene = gene
						)
					# TODO: if the transcript is new, query refseq transcripts

					hgvs_c_query = item['HGVSc']
					hgvs_p_query = item['HGVSp']
					exon_query = 12   # TODO - Pull exon from report - location column  ################################################################
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
					new_classification_obj.initiate_classification()


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

	# If the user has searched for something
	if request.GET.get('variant') != '' and request.GET.get('variant') != None:


		# Get the user input from the form.
		search_query = request.GET.get('variant')
		search_query = search_query.strip()
		gene_query = request.GET.get('gene').strip()
		transcript_query = request.GET.get('transcript').strip()
		hgvs_c_query = request.GET.get('hgvs_c').strip()
		hgvs_p_query = request.GET.get('hgvs_p').strip()
		exon_query = request.GET.get('exon').strip()

		sample_name_query = request.GET.get('sample_name').strip()
		affected_with_query = request.GET.get('affected_with').strip()
		analysis_performed_query = request.GET.get('analysis_performed').strip()
		other_changes_query = request.GET.get('other_changes').strip()
		worklist_query = request.GET.get('worklist').strip()

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

		transcript, created = Transcript.objects.get_or_create(
			name = transcript_query,
			gene = gene
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

		new_classification_obj.initiate_classification()

		# Go to the new_classification page.
		return redirect(new_classification, new_classification_obj.pk)

	return render(request, 'acmg_db/manual_input.html', {'form': form, 'error': None})


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
	variant = classification.variant

	#reject if wrong status or user
	if classification.status != '0' or request.user != classification.user_creator:

		return HttpResponseForbidden()

	else:

		# If the user has submitted the SampleInformationForm
		if request.method == 'POST':

			sample_form = ClassificationInformationForm(request.POST, classification_pk = classification.pk)

			if sample_form.is_valid():

				# Update models
				cleaned_data = sample_form.cleaned_data
				classification.is_trio_de_novo = cleaned_data['is_trio_de_novo']
				classification.inheritance_pattern = cleaned_data['inheritance_pattern']
				classification.final_class = cleaned_data['final_classification']
				classification.conditions = cleaned_data['conditions']
				classification.status = '1'

				classification.save()

				return redirect(home)

		else:

			# Get all the previous classifications of this variant
			previous_classifications = Classification.objects.filter(variant=variant).exclude(pk=classification.pk).order_by('-second_check_date')

			# Get the answers to the ACMG criteria for this classification
			answers = ClassificationAnswer.objects.filter(classification=classification).order_by('classification_question__order')

			comments = UserComment.objects.filter(classification=classification)

			sample_form = ClassificationInformationForm(classification_pk = classification.pk)

			# Get the automated acmg score
			result = classification.calculate_acmg_score_first()

			return render(request, 'acmg_db/new_classifications.html', {'answers': answers,
										 'classification': classification,
										 'variant': variant,
										 'comments': comments,
										 'result': result,
										 'sample_form': sample_form,
										 'previous_classifications': previous_classifications
										 })

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
		result = classification.calculate_acmg_score_first()

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

		acmg_result_first = classification.calculate_acmg_score_first()

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
			classification.inheritance_pattern = cleaned_data['inheritance_pattern']
			classification.final_class = cleaned_data['final_classification']
			classification.conditions = cleaned_data['conditions']
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

		acmg_result_first = classification.calculate_acmg_score_first()

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






