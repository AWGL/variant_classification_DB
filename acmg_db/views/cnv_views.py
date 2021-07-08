from io import TextIOWrapper
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from acmg_db.forms import ManualUploadForm, CNVFileUploadForm
from acmg_db.models import *
from acmg_db.utils.variant_utils import load_worksheet, get_vep_info_local, process_variant_input
from acmg_db.utils.cnv_utils import load_cnv
from acmg_db.utils.acmg_classifier import guideline_version

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_home(request):
	"""
	Allows users to upload a file of CNVs to classify.

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	# Inititate the upload form and context dict to pass to template
	form = CNVFileUploadForm(options=PANEL_OPTIONS)
	context = {
		'form': form, 
		'error': None,
		'warn': None,
		'success': None,
		'params': None
	}

	if request.POST:

		form = CNVFileUploadForm(request.POST, request.FILES, options=PANEL_OPTIONS)

		if form.is_valid():

			# get panel
			analysis_performed_pk = form.cleaned_data['panel_applied'].lower()
			panel_obj = get_object_or_404(Panel, panel = analysis_performed_pk)

			# get affected with
			affected_with = form.cleaned_data['affected_with']
			

			# process tsv file
			raw_file = request.FILES['CNV_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			df, meta_dict = load_cnv(utf_file)

			# Get key information from the metadata
			worksheet_id = meta_dict.get('worksheet_id')
			sample_id = meta_dict.get('sample_id')
			genome = meta_dict.get('genome')		


			# add worksheet
			worksheet_obj, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)
			
			# add cnv sample
				
			try:
				CNVSample_obj = CNVSample.objects.get(sample_name=sample_id,worklist = worksheet_id)

				# throw error if the sample has been uploaded before with the same panel (wont throw error if its a different panel)
				context['error'] = [f'ERROR: {CNVSample_obj.sample_name} has already been uploaded from {worksheet_id}.']
				return render(request, 'acmg_db/cnv_home.html', context)

			except CNVSample.DoesNotExist:
				CNVSample_obj = CNVSample.objects.create(
						sample_name = sample_id,
						worklist = worksheet_obj,
						affected_with = affected_with,
						analysis_performed = panel_obj,
						analysis_complete = False,
						genome = genome
						)
				CNVSample_obj.save()
			
			# add cnv variant, taking information from dataframe	
			for index, row in df.iterrows():
				
				#Set CNV
				cnv = row['ISCN Notation']
				#Take anything before p/q as chromosome
				cnv = cnv.split(" ")
				pattern = re.compile(r".+(?=p)|.+(?=q)")
				chrom = pattern.search(cnv[1]).group()
				
				#Take numbers in brackets as start/stop
				start = re.search(r'\((.*?)_', cnv[1]).group(1)
				stop = re.search(r'_(.*?)\)', cnv[1]).group(1)
			
				#Put together to make final CNV
				final_cnv = chrom+":"+start+"-"+stop
				
				#Set Gain/Loss
				gain_loss = row['Gain/Loss']
				
				CNV_obj = CNV.objects.create(
						sample = CNVSample_obj,
						cnv = final_cnv,
						gain_loss = gain_loss,
						)
				CNV_obj.save()

			# Get VEP annotations
			# Set dictionary depending on Reference genome input from form
			#if genome == "GRCh37":
			#	vep_info_dict = {
			#		'reference_genome' : settings.REFERENCE_GENOME_37,
			#		'vep_cache': settings.VEP_CACHE_37,
			#		'temp_dir': settings.VEP_TEMP_DIR,
			#		'assembly': settings.ASSEMBLY_37,
			#		'version': settings.VEP_VERSION_37
			#	}
			#elif genome == "GRCh38":
			#	vep_info_dict = {
			#		'reference_genome': settings.REFERENCE_GENOME_38,
			#		'vep_cache': settings.VEP_CACHE_38,
		#			'temp_dir': settings.VEP_TEMP_DIR,
		#			'assembly': settings.ASSEMBLY_38,
		#			'version': settings.VEP_VERSION_38
		#		}
#
#			variant_annotations = get_vep_info_local(unique_variants, vep_info_dict, sample_id)
#
#			# Loop through each variant and add to the database
#			for variant in variant_annotations:
#
#				var = variant[1]
#				variant_data = process_variant_input(var)
#
#				variant_hash = variant_data[0]
#				chromosome = variant_data[1]
#				position = variant_data[2]
#				ref = variant_data[3]
#				alt = variant_data[4]
#					
#				variant_obj, created = Variant.objects.get_or_create(
#						variant_hash = variant_hash,
#						chromosome = chromosome,
#						position = position,
#						ref = ref,
#						alt = alt,
#						genome = genome
#						)
#
#				if 'transcript_consequences' in variant[0]:
#
#					consequences = variant[0]['transcript_consequences']
#
#				elif 'intergenic_consequences' in variant[0]:
#
#					consequences = variant[0]['intergenic_consequences']
#
#				else:
#
#					raise Exception(f'Could not get the consequences for variant {variant}')
#
#				selected = None
#
#				# Loop through each consequence/transcript
#				for consequence in consequences:
#
#					if 'transcript_id' in consequence:
#
#						transcript_id = consequence['transcript_id']
#
#					else:
#
#						transcript_id = 'None'
#
#					transcript_hgvsc = consequence.get('hgvsc')
#					transcript_hgvsp = consequence.get('hgvsp')
#					gene_symbol = consequence.get('gene_symbol', 'None')
#					exon = consequence.get('exon', 'NA')
#					impact = consequence.get('consequence_terms')
#					impact = '|'.join(impact)
#
#
#					gene_obj, created = Gene.objects.get_or_create(
#						name = gene_symbol
#						)
#
#					transcript_obj, created = Transcript.objects.get_or_create(
#							name = transcript_id,
#							gene = gene_obj
#						)
#
#					transcript_variant_obj, created = TranscriptVariant.objects.get_or_create(
#						variant = variant_obj,
#						transcript = transcript_obj,
#						hgvs_c = transcript_hgvsc,
#						hgvs_p = transcript_hgvsp,
#						exon = exon,
#						consequence = impact
#						)
#
#					# only add the vep version if its a new transcript, otherwise there will be duplicates for each vep version
#					if genome == "GRCh37":
#						vep_version = settings.VEP_VERSION_37
#					elif genome == "GRCh38":
#						vep_version = settings.VEP_VERSION_38
#						
#					if created:
#						transcript_variant_obj.vep_version = vep_version
#						transcript_variant_obj.save()
#
#					# Find the transcript that VEP has picked
#					if 'pick' in consequence:
#
#						selected = transcript_variant_obj
#
#				# process the genotype
#				genotype = variant_genotype_dict[f'{variant_obj.chromosome}:{variant_obj.position}{variant_obj.ref}#>{variant_obj.alt}']
#
#
#				# for FH TSVs in which the genotype field is different e.g. A/G rather than HET
#				if '/' in genotype:
#
#					alt = variant_obj.alt
#
#					genotype = genotype.split('/')
#
#					if genotype.count(alt) == 1:
#
#						genotype = 'HET'
#
#					elif genotype.count(alt) == 2:
#
#						genotype = 'HOM'
#
#					else:
#						# something else set to None
#						genotype = None
#
#				if genotype == 'HET':
#
#					genotype = 1
#
#				elif genotype == 'HOM' or genotype == 'HOM_ALT':
#
#					genotype = 2
#
#				else:
#
#					genotype = None
#
#				new_classification_obj = Classification.objects.create(
#					variant= variant_obj,
#					sample = sample_obj,
#					creation_date = timezone.now(),
#					user_creator = request.user,
#					status = '0',
#					is_trio_de_novo = False,
#					first_final_class = '7',
#					second_final_class = '7',
#					selected_transcript_variant = selected,
#					genotype=genotype,
#					guideline_version=guideline_version,
#					vep_version=vep_version,
#					genome = genome,
#					)
#
#				new_classification_obj.save()
#
			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}&sample={}&panel={}'.format(worksheet_id, sample_id, analysis_performed_pk)

			context = {
					'form': form, 
					'success': success,
					'params': params
					}


	return render(request, 'acmg_db/cnv_home.html', context)


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_pending(request):
	"""
	Page to view CNV classifications that havent yet been completed

	Use select_related to perform SQL join for all data we need, so that we only hit the database 
	once - https://docs.djangoproject.com/en/3.0/ref/models/querysets/#select-related
	"""

	cnvs = CNV.objects.filter(sample__analysis_complete=False)

	return render(request, 'acmg_db/cnv_pending.html', {'cnvs': cnvs})

