from io import TextIOWrapper

from ..forms import VariantFileUploadForm, ManualUploadForm
from ..models import *
from .first_check_views import first_check
from ..utils.variant_utils import load_worksheet, get_vep_info_local, get_variant_info_mutalzer, process_variant_input

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def auto_input(request):
	"""
	Allows users to upload a file of variants to classify.

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	# Inititate the upload form and context dict to pass to template
	form = VariantFileUploadForm(options=PANEL_OPTIONS)
	context = {
		'form': form, 
		'error': None,
		'warn': None,
		'success': None,
		'params': None
	}

	if request.POST:

		form = VariantFileUploadForm(request.POST, request.FILES, options=PANEL_OPTIONS)

		if form.is_valid():

			# get panel
			analysis_performed_pk = form.cleaned_data['panel_applied'].lower()
			panel_obj = get_object_or_404(Panel, panel = analysis_performed_pk)

			# get affected with
			affected_with = form.cleaned_data['affected_with']

			# process tsv file
			raw_file = request.FILES['variant_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			df, meta_dict = load_worksheet(utf_file)

			# Get key information from the dataframe
			# We have checked that there is only one sample/worksheet in the df 
			unique_variants =  df['Variant'].unique()
			worksheet_id = df['WorklistId'].unique()[0]
			sample_id = df['#SampleId'].unique()[0]

			# add worksheet
			worksheet_obj, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)

			# add sample
			try:
				sample_obj = Sample.objects.get(name=worksheet_id + '-' + sample_id + '-' + analysis_performed_pk)

				# throw error if the sample has been uploaded before with the same panel (wont throw error if its a different panel)
				context['error'] = [f'ERROR: {sample_obj.name} has already been uploaded with the {analysis_performed_pk} panel.']
				return render(request, 'acmg_db/auto_input.html', context)

			except Sample.DoesNotExist:
				sample_obj = Sample.objects.create(
						name = worksheet_id + '-' + sample_id + '-' + analysis_performed_pk,
						sample_name_only = sample_id,
						worklist = worksheet_obj,
						affected_with = affected_with,
						analysis_performed = panel_obj,
						analysis_complete = False,
						other_changes = ''
						)
				sample_obj.save()

			# Get VEP annotations
			vep_info_dict = {
				'reference_genome' : settings.REFERENCE_GENOME,
				'vep_cache': settings.VEP_CACHE,
				'temp_dir': settings.VEP_TEMP_DIR
			}

			variant_annotations = get_vep_info_local(unique_variants, vep_info_dict, sample_id)

			# Loop through each variant and add to the database
			for variant in variant_annotations:

				var = variant[1]
				variant_data = process_variant_input(var)

				key = variant_data[5]
				variant_hash = variant_data[0]
				chromosome = variant_data[1]
				position = variant_data[2]
				ref = variant_data[3]
				alt = variant_data[4]
					
				variant_obj, created = Variant.objects.get_or_create(
						key = key,
						variant_hash = variant_hash,
						chromosome = chromosome,
						position = position,
						ref = ref,
						alt = alt
						)

				if 'transcript_consequences' in variant[0]:

					consequences = variant[0]['transcript_consequences']

				elif 'intergenic_consequences' in variant[0]:

					consequences = variant[0]['intergenic_consequences']

				else:

					raise Exception(f'Could not get the consequences for variant {variant}')

				selected = None

				# Loop through each consequence/transcript
				for consequence in consequences:

					if 'transcript_id' in consequence:

						transcript_id = consequence['transcript_id']

					else:

						transcript_id = 'None'

					transcript_hgvsc = consequence.get('hgvsc')
					transcript_hgvsp = consequence.get('hgvsp')
					gene_symbol = consequence.get('gene_symbol', 'None')
					exon = consequence.get('exon', 'NA')
					impact = consequence.get('consequence_terms')
					impact = '|'.join(impact)


					gene_obj, created = Gene.objects.get_or_create(
						name = gene_symbol
						)

					transcript_obj, created = Transcript.objects.get_or_create(
							name = transcript_id,
							gene = gene_obj
						)

					transcript_variant_obj, created = TranscriptVariant.objects.get_or_create(
						variant = variant_obj,
						transcript = transcript_obj,
						hgvs_c = transcript_hgvsc,
						hgvs_p = transcript_hgvsp,
						exon = exon,
						consequence = impact

						)
					# Find the transcript that VEP has picked
					if 'pick' in consequence:

						selected = transcript_variant_obj

				new_classification_obj = Classification.objects.create(
					variant= variant_obj,
					sample = sample_obj,
					creation_date = timezone.now(),
					user_creator = request.user,
					status = '0',
					is_trio_de_novo = False,
					first_final_class = '7',
					second_final_class = '7',
					selected_transcript_variant = selected
					)

				new_classification_obj.save()

			success = ['Worksheet {} - Sample {} - Upload completed '.format(worksheet_id, sample_id)]
			params = '?worksheet={}&sample={}'.format(worksheet_id, sample_id)

			context = {
					'form': form, 
					'success': success,
					'params': params
					}


	return render(request, 'acmg_db/auto_input.html', context)


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def manual_input(request):
	"""
	The view for the manual input page.

	Allows users to create a new classification for a variant.
	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	form = ManualUploadForm(options=PANEL_OPTIONS)
	context = {
		'form': form,
		'error': [], 
	}

	# If the user has clicked submit
	if request.POST:

		form = ManualUploadForm(request.POST, options=PANEL_OPTIONS)

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
			analysis_performed_query = cleaned_data['analysis_performed'].strip().lower()
			other_changes_query = cleaned_data['other_changes'].strip()
			worklist_query = cleaned_data['worklist'].strip()
			consequence_query = cleaned_data['consequence'].strip()
		
			# Validate the variant using Mutalyzer - i.e. is the variant real?
			# We only check if the chr-pos-ref-alt is real not if gene etc is correct.
			variant_info = get_variant_info_mutalzer(search_query, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)

			if variant_info[0] == True:

				# Add variant to DB if not already present
				# Get variant information e.g. chr, pos, ref, alt from the input

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

				panel = get_object_or_404(Panel, panel=analysis_performed_query)

				# Get or create working strangely on samples so create it the old fashioned way.
				try:

					sample_obj = Sample.objects.get(name=worklist_query + '-' + sample_name_query + '-' + analysis_performed_query)

				except Sample.DoesNotExist:

					sample_obj = Sample.objects.create(
						name = worklist_query + '-' + sample_name_query + '-' + analysis_performed_query,
						sample_name_only = sample_name_query,
						worklist = worklist,
						affected_with = affected_with_query,
						analysis_performed = panel,
						analysis_complete = False,
						other_changes = other_changes_query
							)

					sample_obj.save()

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
					exon = exon_query,
					consequence = consequence_query
				)

				new_classification_obj = Classification.objects.create(
					variant= variant,
					sample = sample_obj,
					creation_date = timezone.now(),
					user_creator = request.user,
					status = '0',
					is_trio_de_novo = False,
					first_final_class = '7',
					second_final_class = '7',
					selected_transcript_variant = transcript_variant
				)

				new_classification_obj.save()
				
				# Go to the new_classification page.
				return redirect(first_check, new_classification_obj.pk)

			else:

				context['error'] = variant_info[1][0]

				return render(request, 'acmg_db/manual_input.html', context)


	return render(request, 'acmg_db/manual_input.html', context)
