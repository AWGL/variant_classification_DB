from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.conf import settings
from .models import *
from .utils.variant_utils import *
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseForbidden
import json
import base64
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
	"""
	The view for the home page.

	Allows users to create a new classification for a variant.


	"""

	form = SearchForm()

	# If the user has searched for something
	if request.GET.get("search") != "" and request.GET.get("search") != None:

		search_query = request.GET.get("search")

		search_query = search_query.strip()

		variant_info = validate_variant(search_query, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD )

		# If the variant has failed validation return to search screen and display error.
		if variant_info[0] == False:

			return render(request, 'acmg_db/home.html', {'form': form,
										 'error': variant_info[1][0]})
		else:

			# Add variant to DB if not already present

			# Get varaint information e.g. chr, pos, ref, alt from the input

			variant_data = process_variant(search_query)

			variant_hash = variant_data[0]
			chromosome = variant_data[1]
			position = variant_data[2]
			ref = variant_data[3]
			alt = variant_data[4]
			key = variant_data[5]

			variant, created = Variant.objects.get_or_create(
    				key = key,
    				variant_hash = variant_hash,
    				chromosome = chromosome,
    				position = position,
    				ref = ref,
    				alt = alt
					)

			# Loop through each transcript and gene in the variant info list and add to DB \
			# if we have not seen it before.
			for variant_transcript in variant_info[1]:


				gene, created = Gene.objects.get_or_create(
					name = variant_transcript[1]
					)

				transcript, created = Transcript.objects.get_or_create(
					name = variant_transcript[0].split(':')[0],
					gene = gene
					)
				
				transcript_variant, created = TranscriptVariant.objects.get_or_create(
					variant = variant,
					transcript = transcript,
					hgvs_c = variant_transcript[0],
					hgvs_p = variant_transcript[2]
					)


			new_classication = Classification.objects.create(
				variant= variant,
				creation_date = timezone.now(),
				user_creator = request.user,
				status = '0'
				)

			new_classication.save()

			new_classication.initiate_classification()


			return redirect(new_classification, new_classication.pk)


	return render(request, 'acmg_db/home.html', {'form': form, 'error': None})



def new_classification(request, pk):
	"""
	Page for entering new classifications


	"""

	classification = get_object_or_404(Classification, pk=pk)
	variant = classification.variant


	#reject if wrong status or user
	if classification.status != '0' or request.user != classification.user_creator:

		return HttpResponseForbidden()

	else:

		if request.method == 'POST':

			sample_form = SampleInformationForm(request.POST, classification_pk = classification.pk)

			if sample_form.is_valid():

				cleaned_data = sample_form.cleaned_data

				if cleaned_data['transcript_variants'] == 'None':

					gene, created = Gene.objects.get_or_create(
						name = 'None'
						)

					transcript, created = Transcript.objects.get_or_create(
						name = 'None',
						gene = gene
						)

					transcript_variants = TranscriptVariant.objects.filter(
						variant = variant,
						transcript = transcript,
						)

					if len(transcript_variants) == 0:

						transcript_variant = TranscriptVariant(variant=variant,
							transcript= transcript)

						transcript_variant.save()

					else:

						transcript_variant = transcript_variants[0]


				else:

					transcript_variant = get_object_or_404(TranscriptVariant, pk =cleaned_data['transcript_variants'])

				classification.sample_lab_number = cleaned_data['sample_lab_number']
				classification.analysis_performed = cleaned_data['analysis_performed']
				classification.other_changes = cleaned_data['other_changes']
				classification.affected_with = cleaned_data['affected_with']
				classification.trio_de_novo = cleaned_data['trio_de_novo']
				classification.inheritance_pattern = cleaned_data['inheritance_pattern']
				classification.final_class = cleaned_data['final_classification']
				classification.selected_transcript_variant = transcript_variant
				classification.conditions = cleaned_data['conditions']
				classification.status = '1'

				classification.save()

				return redirect(home)

		else:


			transcript_variants = TranscriptVariant.objects.filter(variant=variant).exclude(transcript__name ='None')

			answers = ClassificationAnswer.objects.filter(classification=classification)

			comments = UserComment.objects.filter(classification=classification)

			sample_form = SampleInformationForm(classification_pk = classification.pk)

			result = classification.calculate_acmg_score()

			return render(request, 'acmg_db/new_classifications.html', {'answers': answers,
										 'classification': classification,
										 'variant': variant,
										 'transcript_variants': transcript_variants,
										 'comments': comments,
										 'sample_form': sample_form,
										 'result': result })


def ajax_acmg_classification(request):
	"""
	Gets the ajax results from the new_classifcations.html page \
	and stores them in the database - also returns the calculated result.
	

	"""

	if request.is_ajax():

		classification_answers = request.POST.get('classifications')

		classification_answers = json.loads(classification_answers)

		classification_pk = request.POST.get('classification_pk').strip()

		classification = get_object_or_404(Classification, pk =classification_pk)

		for classification_answer in classification_answers:

			pk = classification_answer.strip()

			classification_answer_obj = get_object_or_404(ClassificationAnswer, pk=pk)

			print (classification_answers[classification_answer])

			classification_answer_obj.strength = classification_answers[classification_answer][1].strip()

			classification_answer_obj.selected = classification_answers[classification_answer][2].strip()

			classification_answer_obj.save()

		result = classification.calculate_acmg_score()

		html = render_to_string('acmg_db/acmg_results.html', {'result': result})

	return HttpResponse(html)



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

def view_previous_classifications(request):
	"""
	Page to view previous classifications

	"""


	classifications = Classification.objects.all().order_by('-creation_date')

	return render(request, 'acmg_db/view_classifications.html', {'classifications': classifications})



def view_classification(request, pk):
	"""
	View a read only version of a classification of a variant


	"""

	classification = get_object_or_404(Classification, pk=pk)

	classification_answers = (ClassificationAnswer.objects.filter(classification=classification)
		.order_by('classification_question__order')
		.filter(selected=True))

	comments = UserComment.objects.filter(classification=classification)

	return render(request, 'acmg_db/view_classification.html', {'classification': classification,
									 'classification_answers': classification_answers,
									 'comments': comments})


def second_check(request, pk):
	"""
	Page for user to perform second check.


	"""

	classification = get_object_or_404(Classification, pk=pk)

	if request.method == 'POST':

		form = SecondCheckForm(request.POST, classification_pk=pk )

		if form.is_valid():

			data = form.cleaned_data

			accept_or_reject = data['accept']

			# if we have accepted the classification
			if accept_or_reject == '1':



				classification.status = '2'

				classification.second_check_date = timezone.now()
				classification.user_second_checker = request.user

				classification.save()

			else:

				classification.status = '0'
				classification.save()


			return redirect(home)

	else:

		classification_answers = (ClassificationAnswer.objects.filter(classification=classification)
		.order_by('classification_question__order')
		.filter(selected=True))

		comments = UserComment.objects.filter(classification=classification)

		second_check_form = SecondCheckForm(classification_pk=classification.pk)

		return render(request, 'acmg_db/second_check.html', {'classification': classification,
									 'classification_answers': classification_answers,
									 'comments': comments,
									 'second_check_form': second_check_form})

def add_transcript_variant(request):

	"""
	Page for the user to add a transcript variant if needed.


	"""

	pass









