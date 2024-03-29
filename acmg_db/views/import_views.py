from io import TextIOWrapper

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from acmg_db.forms import VariantFileUploadForm, ManualUploadForm
from acmg_db.models import *
from acmg_db.utils.variant_utils import load_worksheet, get_vep_info_local, process_variant_input
from acmg_db.utils.acmg_classifier import guideline_version



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

			# get reference genome
			if 'Reference' in df:
				genome = df['Reference'].unique()[0]
			else:
				genome = 'GRCh37'		

			# create dict of links between variant and genotype
			variant_genotype_dict = {}

			for row in df.itertuples():

				variant_genotype_dict[row.Variant] = row.Genotype


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
						other_changes = '',
						genome = genome
						)
				sample_obj.save()

			# Get VEP annotations
			# Set dictionary depending on Reference genome input from form
			if genome == "GRCh37":
				vep_info_dict = {
					'reference_genome' : settings.REFERENCE_GENOME_37,
					'vep_cache': settings.VEP_CACHE_37,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_37,
					'version': settings.VEP_VERSION_37
				}
			elif genome == "GRCh38":
				vep_info_dict = {
					'reference_genome': settings.REFERENCE_GENOME_38,
					'vep_cache': settings.VEP_CACHE_38,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_38,
					'version': settings.VEP_VERSION_38
				}

			variant_annotations = get_vep_info_local(unique_variants, vep_info_dict, sample_id)


			# set vep version
			if genome == "GRCh37":
				vep_version = settings.VEP_VERSION_37
			elif genome == "GRCh38":
				vep_version = settings.VEP_VERSION_38


			# Loop through each variant and add to the database
			for variant in variant_annotations:

				var = variant[1]
				variant_data = process_variant_input(var, genome)

				variant_hash = variant_data[0]
				chromosome = variant_data[1]
				position = variant_data[2]
				ref = variant_data[3]
				alt = variant_data[4]
					
				variant_obj, created = Variant.objects.get_or_create(
						variant_hash = variant_hash,
						chromosome = chromosome,
						position = position,
						ref = ref,
						alt = alt,
						genome = genome
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

					
					gene_obj = Gene.objects.filter(name = gene_symbol)

					if len(gene_obj) == 0:
						
						gene_obj = Gene(name = gene_symbol)
						gene_obj.save()
					else:
	
						gene_obj = gene_obj[0]


					transcript_obj = Transcript.objects.filter(name=transcript_id, gene=gene_obj)

					if len(transcript_obj) == 0:
					
						transcript_obj = Transcript(name=transcript_id, gene=gene_obj)
						transcript_obj.save()

					else:

						transcript_obj = transcript_obj[0]


					transcript_variant_obj = TranscriptVariant.objects.filter(variant=variant_obj, transcript=transcript_obj)
					
					if len(transcript_variant_obj) == 0:
						
						transcript_variant_obj = TranscriptVariant(variant = variant_obj,
											transcript = transcript_obj,
                                                					hgvs_c = transcript_hgvsc,
                                                					hgvs_p = transcript_hgvsp,
                                                					exon = exon,
                                                					consequence = impact)

						transcript_variant_obj.vep_version = vep_version
						transcript_variant_obj.save()
					
					else:

						transcript_variant_obj = transcript_variant_obj[0]


					# Find the transcript that VEP has picked
					if 'pick' in consequence:

						selected = transcript_variant_obj

				# process the genotype
				genotype = variant_genotype_dict[f'{variant_obj.chromosome}:{variant_obj.position}{variant_obj.ref}>{variant_obj.alt}']


				# for FH TSVs in which the genotype field is different e.g. A/G rather than HET
				if '/' in genotype:

					alt = variant_obj.alt

					genotype = genotype.split('/')

					if genotype.count(alt) == 1:

						genotype = 'HET'

					elif genotype.count(alt) == 2:

						genotype = 'HOM'

					else:
						# something else set to None
						genotype = None

				if genotype == 'HET':

					genotype = 1

				elif genotype == 'HOM' or genotype == 'HOM_ALT':

					genotype = 2

				else:

					genotype = None

				new_classification_obj = Classification.objects.create(
					variant= variant_obj,
					sample = sample_obj,
					creation_date = timezone.now(),
					user_creator = request.user,
					status = '0',
					is_trio_de_novo = False,
					first_final_class = '7',
					second_final_class = '7',
					selected_transcript_variant = selected,
					genotype=genotype,
					guideline_version=guideline_version,
					vep_version=vep_version
					)

				new_classification_obj.save()

			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}&sample={}&panel={}'.format(worksheet_id, sample_id, analysis_performed_pk)

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


	if request.POST:

		form = ManualUploadForm(request.POST, options=PANEL_OPTIONS)

		if form.is_valid():

			# get panel
			analysis_performed_pk = form.cleaned_data['panel_applied'].lower()
			panel_obj = get_object_or_404(Panel, panel = analysis_performed_pk)

			# get affected with
			affected_with = form.cleaned_data['affected_with'].strip()
			
			# get reference genome
			genome = form.cleaned_data['genome']

			# get genotype

			genotype = form.cleaned_data['genotype']

			if genotype == 'Het':
				genotype = 1

			elif genotype  == 'Hom':
				genotype = 2

			elif genotype == 'Hemi':
				genotype = 3

			elif genotype == 'Mosaic':
				genotype = 4

			else:
				genotype = None

			# get variant
			variants = form.cleaned_data['variant'].strip().upper()
			# sanitise input
			for character in list(variants):
				if character not in 'ACGT0123456789XYM>:':
					context = {
						'form': form,
						'error': f'Invalid character in variant field: {character}',
					}
					return render(request, 'acmg_db/manual_input.html', context)

			# put variant into list - just so we can reuse code from above

			unique_variants = [variants]

			# get worksheet
			worksheet_id = form.cleaned_data['worklist'].strip().upper().replace(' ', '_')
			# sanitise input
			for character in list(worksheet_id):
				if character not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_':
					context = {
						'form': form,
						'error': f'Invalid character in worksheet field: {character}',
					}
					return render(request, 'acmg_db/manual_input.html', context)

			#get sample 
			sample_id = form.cleaned_data['sample_name'].strip().upper().replace(' ', '_')
			# sanitise input
			for character in list(sample_id):
				if character not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_':
					context = {
						'form': form,
						'error': f'Invalid character in sample name field: {character}',
					}
					return render(request, 'acmg_db/manual_input.html', context)


			# add worksheet
			worksheet_obj, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)

			# add sample
			try:
				sample_obj = Sample.objects.get(name=worksheet_id + '-' + sample_id + '-' + analysis_performed_pk)

				# throw error if the sample has been uploaded before with the same panel (wont throw error if its a different panel)
				#context['error'] = [f'ERROR: {sample_obj.name} has already been uploaded with the {analysis_performed_pk} panel.']
				#return render(request, 'acmg_db/manual_input.html', context)

			except Sample.DoesNotExist:
				sample_obj = Sample.objects.create(
						name = worksheet_id + '-' + sample_id + '-' + analysis_performed_pk,
						sample_name_only = sample_id,
						worklist = worksheet_obj,
						affected_with = affected_with,
						analysis_performed = panel_obj,
						analysis_complete = False,
						other_changes = '',
						genome = genome,
						)
				sample_obj.save()

			# Get VEP annotations
			if genome == "GRCh37":
				vep_info_dict = {
					'reference_genome' : settings.REFERENCE_GENOME_37,
					'vep_cache': settings.VEP_CACHE_37,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_37,
					'version': settings.VEP_VERSION_37
				}
			elif genome == "GRCh38":
				vep_info_dict = {
					'reference_genome': settings.REFERENCE_GENOME_38,
					'vep_cache': settings.VEP_CACHE_38,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_38,
					'version': settings.VEP_VERSION_38
				}

			try:
				variant_annotations = get_vep_info_local(unique_variants, vep_info_dict, sample_id)
			except:

				context = {
					'form': form,
					'error': 'VEP annotation failed. Are you sure this a correct variant? Are you sure the correct reference genome has been selected?',
				}
				return render(request, 'acmg_db/manual_input.html', context)


			# Loop through each variant and add to the database
			for variant in variant_annotations:

				var = variant[1]
				variant_data = process_variant_input(var, genome)

				variant_hash = variant_data[0]
				chromosome = variant_data[1]
				position = variant_data[2]
				ref = variant_data[3]
				alt = variant_data[4]
					
				variant_obj, created = Variant.objects.get_or_create(
						variant_hash = variant_hash,
						chromosome = chromosome,
						position = position,
						ref = ref,
						alt = alt,
						genome = genome,
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

					# only add the vep version if its a new transcript, otherwise there will be duplicates for each vep version
					if genome == "GRCh37":
						vep_version = settings.VEP_VERSION_37
					elif genome == "GRCh38":
						vep_version = settings.VEP_VERSION_38
					
					if created:
						transcript_variant_obj.vep_version = vep_version
						transcript_variant_obj.save()

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
					selected_transcript_variant = selected,
					genotype = genotype,
					guideline_version=guideline_version,
					vep_version=vep_version
					)

				new_classification_obj.save()

			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}&sample={}&panel={}'.format(worksheet_id, sample_id, analysis_performed_pk)

			context = {
					'form': form, 
					'success': success,
					'params': params
					}
	


	return render(request, 'acmg_db/manual_input.html', context)
