from io import TextIOWrapper
import re
import simplejson as json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q, Prefetch

from acmg_db.forms import CNVFileUploadForm, CNVBluefuseUploadForm, CNVManualUpload, ArchiveCNVClassificationForm, CNVAssignSecondCheckToMeForm, CNVSendBackToFirstCheckForm, CNVResetClassificationForm
from acmg_db.models import *
from acmg_db.utils.variant_utils import load_worksheet,  process_variant_input
from acmg_db.utils.cnv_utils import load_cnv, load_bluefuse, get_vep_info_local_cnv
from acmg_db.utils.acmg_classifier import guideline_version

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_import(request):

	return render(request, 'acmg_db/cnv_import.html')

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
			
			# get platform
			platform = form.cleaned_data['platform']
			
			# get worksheet
			worksheet_id = form.cleaned_data['worksheet']
			
			# process tsv file
			raw_file = request.FILES['CNV_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			df, meta_dict = load_cnv(utf_file)

			# Get key information from the metadata
			#worksheet_id = meta_dict.get('worksheet_id') ARRAY BARCODE IDENTIFIER - NOT CURRENTLY USED
			sample_id = meta_dict.get('sample_id')
			genome = meta_dict.get('genome')
			cyto_id = meta_dict.get('cyto_id')		


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
						platform = platform,
						cyto=cyto_id
						)
				CNVSample_obj.save()
			
			unique_cnvs = []
			# add cnv variant, taking information from dataframe	
			for index, row in df.iterrows():
				
				#Set CNV
				cnv = row['ISCN Notation']
				#Take anything before p/q as chromosome
				cnv = cnv.split(" ")
				#Had a case where chromosome arm appeared twice so need to handle that. 
				#Unable to get regular expression matching to work, so instead will split based on p/q
				if cnv[1].count('p') != 1 or cnv[1].count('q') != 1:
					if 'p' in cnv[1]:
						r  = cnv[1].split("p")
						chrom = r[0]
					elif 'q' in cnv[1]:
						r = cnv[1].split("q")
						chrom = r[0]	
				else:
					pattern = re.compile(r".+(?=p)|.+(?=q)")
					chrom = pattern.search(cnv[1]).group()
					
				
				#Take numbers in brackets as start/stop
				start = re.search(r'\((.*?)_', cnv[1]).group(1)
				stop = re.search(r'_(.*?)\)', cnv[1]).group(1)
				
				#Getting cytogenetic location
				cyto_loc = (cnv[1].split("("))[0]
				
				#Calculate length
				length = int(stop)-int(start)
				
				
				#Put together to make final CNV
				final_cnv = chrom+":"+start+"-"+stop
				
				#Set Gain/Loss
				gain_loss = row['Gain/Loss']
				
				if final_cnv not in unique_cnvs:
					unique_cnvs.append(final_cnv)
				
				
				CNVVariant_obj, created = CNVVariant.objects.get_or_create(
							full = final_cnv,
							chromosome = chrom,
							start = start,
							stop = stop,
							length = length,
							genome = genome,
							cyto_loc = cyto_loc,
							max_start = start,
							max_stop = stop,
							)
								
							
				CNV_obj = CNV.objects.create(
						sample = CNVSample_obj,
						cnv = CNVVariant_obj,
						gain_loss = gain_loss,
						method = gain_loss,
						status = 0,
						creation_date = timezone.now(),
						user_creator = request.user,
						)
				CNV_obj.save()
			
					
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

			variant_annotations = get_vep_info_local_cnv(unique_cnvs, vep_info_dict, sample_id)

			# Loop through each variant and add gene to the database
			for variant in variant_annotations:
				
				cnv_obj = CNV.objects.get(cnv__full=variant[1],sample__sample_name=sample_id, sample__worklist=worksheet_id)
				
				if 'transcript_consequences' in variant[0]:

					consequences = variant[0]['transcript_consequences']

				elif 'intergenic_consequences' in variant[0]:

					consequences = variant[0]['intergenic_consequences']

				else:

					raise Exception(f'Could not get the consequences for variant {variant}')

				# Loop through each consequence/transcript and get gene identifiers
				for consequence in consequences:
					gene_symbol = consequence.get('gene_symbol', 'None')

					gene, created = Gene.objects.get_or_create(name=gene_symbol)
					
					# if statement to prevent multiple identical genes being added. 
					if not CNVGene.objects.filter(cnv=cnv_obj,gene=gene).exists():
						cnvgene_obj = CNVGene.objects.create(
							gene = gene,
							cnv = cnv_obj
							)
						cnvgene_obj.save()

			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}'.format(worksheet_id)

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

	cnvs = CNV.objects.filter(Q(status='0') | Q(status='1'))

	return render(request, 'acmg_db/cnv_pending.html', {'cnvs': cnvs})
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_manual(request):
	"""
	The view for the manual CNV input page.

	Allows users to create a new classification for a CNV.
	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	form = CNVManualUpload(options=PANEL_OPTIONS)
	context = {
		'form': form,
		'error': [], 
	}

	
	if request.POST:

		form = CNVManualUpload(request.POST, options=PANEL_OPTIONS)

		if form.is_valid():

			# get panel
			analysis_performed_pk = form.cleaned_data['panel_applied'].lower()
			panel_obj = get_object_or_404(Panel, panel = analysis_performed_pk)

			# get affected with
			affected_with = form.cleaned_data['affected_with'].strip()
			
			#get worksheet
			worksheet_id = form.cleaned_data['worklist'].strip()
			
			#get platform
			platform = form.cleaned_data['platform'].strip()
			
			#get sample
			sample_id = form.cleaned_data['sample_name'].strip().upper().replace(' ', '_')
			
			#get cyto ID
			cyto_id = form.cleaned_data['cyto'].strip()
			
			#get cytogenetic location
			cyto_loc = form.cleaned_data['cyto_loc'].strip()
			
			# sanitise input
			for character in list(sample_id):
				if character not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_':
					context = {
						'form': form,
						'error': f'Invalid character in sample name field: {character}',
					}
					return render(request, 'acmg_db/cnv_manual.html', context)
					
			#get gain/loss
			gain_loss_info = form.cleaned_data['gain_loss']
			
			# get reference genome
			genome = form.cleaned_data['genome']

			# get CNV
			final_cnv = form.cleaned_data['CNV'].strip()
			# sanitise input
			for character in list(final_cnv):
				if character not in 'ACGT0123456789XYM-:':
					context = {
						'form': form,
						'error': f'Invalid character in CNV field: {character}',
					}
					return render(request, 'acmg_db/cnv_manual.html', context)
					
			#Break up CNV to get chromosome, start/stop and length
			chrom = final_cnv.split(":")[0]
			final_locs = final_cnv.split(":")[1]
			start = final_locs.split("-")[0]
			stop = final_locs.split("-")[1]
			length = int(stop)-int(start)
			
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
						platform = platform,
						cyto = cyto_id
						)
				CNVSample_obj.save()
			
			# add cnv variant object	
			CNVVariant_obj, created = CNVVariant.objects.get_or_create(
							full = final_cnv,
							chromosome = chrom,
							start = start,
							stop = stop,
							length = length,
							genome = genome,
							cyto_loc = cyto_loc,
							max_start = start,
							max_stop = stop,
							)
							
			# add CNV classification object
			CNV_obj = CNV.objects.create(
					sample = CNVSample_obj,
					cnv = CNVVariant_obj,
					gain_loss = gain_loss_info,
					method = gain_loss_info,
					status = 0,
					creation_date = timezone.now(),
					user_creator = request.user,
					)
			CNV_obj.save()

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
			unique_cnvs = [final_cnv]
			try:
				variant_annotations = get_vep_info_local_cnv(unique_cnvs, vep_info_dict, sample_id)
			except:

				context = {
					'form': form,
					'error': 'VEP annotation failed. Are you sure this a correct variant? Are you sure the correct reference genome has been selected?',
				}
				return render(request, 'acmg_db/manual_input.html', context)

			# Loop through each variant and add gene to the database
			for variant in variant_annotations:
				
				cnv_obj = CNV.objects.get(cnv__full=variant[1],sample__sample_name=sample_id,sample__worklist=worksheet_id)
				
				if 'transcript_consequences' in variant[0]:

					consequences = variant[0]['transcript_consequences']

				elif 'intergenic_consequences' in variant[0]:

					consequences = variant[0]['intergenic_consequences']

				else:

					raise Exception(f'Could not get the consequences for variant {variant}')

				# Loop through each consequence/transcript and get gene identifiers
				for consequence in consequences:
					gene_symbol = consequence.get('gene_symbol', 'None')

					gene, created = Gene.objects.get_or_create(name=gene_symbol)
					
					# if statement to prevent multiple identical genes being added. 
					if not CNVGene.objects.filter(cnv=cnv_obj,gene=gene).exists():
						cnvgene_obj = CNVGene.objects.create(
							gene = gene,
							cnv = cnv_obj
							)
						cnvgene_obj.save()
						
			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}'.format(worksheet_id)

			context = {
					'form': form, 
					'success': success,
					'params': params
					}
	
	

	return render(request, 'acmg_db/cnv_manual.html', context)

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_bluefuse(request):

	"""
	Allows users to upload a file of CNVs to classify. File must be from BlueFuse.

	"""

	PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]

	# Inititate the upload form and context dict to pass to template
	form = CNVBluefuseUploadForm(options=PANEL_OPTIONS)
	context = {
		'form': form, 
		'error': None,
		'warn': None,
		'success': None,
		'params': None
	}

	if request.POST:

		form = CNVBluefuseUploadForm(request.POST, request.FILES, options=PANEL_OPTIONS)

		if form.is_valid():

			# get panel
			analysis_performed_pk = form.cleaned_data['panel_applied'].lower()
			panel_obj = get_object_or_404(Panel, panel = analysis_performed_pk)

			# get affected with
			affected_with = form.cleaned_data['affected_with']
			
			# get platform
			platform = form.cleaned_data['platform']
			
			# get worksheet
			worksheet_id = form.cleaned_data['worksheet']
			
			# process tsv file
			raw_file = request.FILES['CNV_file']
			utf_file = TextIOWrapper(raw_file, encoding='utf-8')
			df, meta_dict = load_bluefuse(utf_file)

			# Get key information from the metadata
			sample_id = meta_dict.get('sample_id')
			genome = meta_dict.get('genome')
			cyto_id = meta_dict.get('cyto_id')	

			# add worksheet
			worksheet_obj, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)
			
			# add cnv sample
				
			try:
				CNVSample_obj = CNVSample.objects.get(sample_name=sample_id,worklist = worksheet_id)

				# throw error if the sample has been uploaded before with the same panel (wont throw error if its a different panel)
				context['error'] = [f'ERROR: {CNVSample_obj.sample_name} has already been uploaded from {worksheet_id}.']
				return render(request, 'acmg_db/cnv_bluefuse.html', context)

			except CNVSample.DoesNotExist:
				CNVSample_obj = CNVSample.objects.create(
						sample_name = sample_id,
						worklist = worksheet_obj,
						affected_with = affected_with,
						analysis_performed = panel_obj,
						analysis_complete = False,
						platform = platform,
						cyto=cyto_id
						)
				CNVSample_obj.save()
			
			unique_cnvs = []
			# add cnv variant, taking information from dataframe	
			for index, row in df.iterrows():
			
				#print(row)	
				#Set CNV
				start = row['Start']
				start = start.replace(',', '')
				start = int(start)
						
				stop = row['End']
				stop = stop.replace(',', '')
				stop = int(stop)
				
				chrom = row['Chromosome']
				
				#Getting cytogenetic location
				cyto_loc = row['Start Cyto']
				
				#Calculate length
				length = row['Size (bp)']
				length = length.replace(',', '')
				length = int(length)
								
				#Put together to make final CNV
				final_cnv = chrom+":"+str(start)+"-"+str(stop)
				
				#Set Gain/Loss
				gain_loss = (row['Type']).lower()
				gain_loss = gain_loss.title()
				print(gain_loss)
				
				#Settings incase type is LOH
				if gain_loss == "Loh":
					method = "Loss"
				else:
					method = gain_loss
				print(method)
				
				#Get max sizes
				max_start = row['max_start']
				max_start = max_start.replace(',', '')
				max_start = int(max_start)
				max_stop = row['max_stop']
				max_stop = max_stop.replace(',', '')
				max_stop = int(max_stop)
				
				print(final_cnv)
				
				if final_cnv not in unique_cnvs:
					unique_cnvs.append(final_cnv)
				
				
				CNVVariant_obj, created = CNVVariant.objects.get_or_create(
							full = final_cnv,
							chromosome = chrom,
							start = start,
							stop = stop,
							length = length,
							genome = genome,
							cyto_loc = cyto_loc,
							max_start = max_start,
							max_stop = max_stop,
							)
								
							
				CNV_obj = CNV.objects.create(
						sample = CNVSample_obj,
						cnv = CNVVariant_obj,
						gain_loss = gain_loss,
						method = method,
						status = 0,
						creation_date = timezone.now(),
						user_creator = request.user,
						)
				CNV_obj.save()
			
					
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

			variant_annotations = get_vep_info_local_cnv(unique_cnvs, vep_info_dict, sample_id)

			# Loop through each variant and add gene to the database
			for variant in variant_annotations:
				
				cnv_obj = CNV.objects.get(cnv__full=variant[1],sample__sample_name=sample_id, sample__worklist=worksheet_id)
				
				if 'transcript_consequences' in variant[0]:

					consequences = variant[0]['transcript_consequences']

				elif 'intergenic_consequences' in variant[0]:

					consequences = variant[0]['intergenic_consequences']

				else:

					raise Exception(f'Could not get the consequences for variant {variant}')

				# Loop through each consequence/transcript and get gene identifiers
				for consequence in consequences:
					gene_symbol = consequence.get('gene_symbol', 'None')

					gene, created = Gene.objects.get_or_create(name=gene_symbol)
					
					# if statement to prevent multiple identical genes being added. 
					if not CNVGene.objects.filter(cnv=cnv_obj,gene=gene).exists():
						cnvgene_obj = CNVGene.objects.create(
							gene = gene,
							cnv = cnv_obj
							)
						cnvgene_obj.save()

			success = ['Worksheet {} - Sample {} - {} panel - Upload completed '.format(worksheet_id, sample_id, analysis_performed_pk)]
			params = '?worksheet={}'.format(worksheet_id)

			context = {
					'form': form, 
					'success': success,
					'params': params
					}
			
	return render(request, 'acmg_db/cnv_bluefuse.html', context)
	
#------------
@transaction.atomic
@login_required
def view_cnvs(request):
	"""
	Page to view all unique CNVs classified in the lab

	"""
	
	# Get all CNVs which are complete or archived, ordered by second check date
	#all_cnvs_query = CNV.objects.filter(status__in=['2','3']).order_by('-second_check_date')

	
	
	# query all variants, prefetch related classification objects and associated transcript/ gene objects
	all_cnv_variants_query = CNVVariant.objects.prefetch_related(
		Prefetch(
			'cnv_classification', 
			queryset=CNV.objects.filter(
					status__in=['2', '3']
				).order_by('-second_check_date'), 
			to_attr='cnv_classification_cache'),
	).order_by('chromosome', 'start')
	
	
	# loop through each variant to parse data
	cnv_data = []
	for cnv in all_cnv_variants_query:
		
		
		# skip if there are no linked classifications
		if len(cnv.cnv_classification_cache) > 0:

			# parse info
			most_recent_obj = cnv.cnv_classification_cache[0]
			most_recent_class = most_recent_obj.display_final_classification()
					
			cnv_id = most_recent_obj.cnv.full
			
			# get list of all unique classifications
			all_classes_set = set()
			for classification in cnv.cnv_classification_cache:
				all_classes_set.add(classification.display_final_classification())

			# add dict containing variant info to list
			cnv_data.append({
				'cnv': cnv_id,
				'num_classifications': len(cnv.cnv_classification_cache), 
				'most_recent_obj': most_recent_obj, 
				'most_recent_date': most_recent_obj.second_check_date, 
				'most_recent_class': most_recent_obj.display_final_classification(), 
				'all_classes': '|'.join(all_classes_set),
				'genome': most_recent_obj.cnv.genome,
			})
	
	return render(request, 'acmg_db/view_cnvs.html', {'cnv_data': cnv_data})
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_cnv_delete_comment(request):
	"""
	View to allow users to delete comments.

	"""

	if request.is_ajax():

		comment_pk = request.POST.get('comment_pk').strip()
		comment = get_object_or_404(CNVUserComment, pk=comment_pk)

		cnv_pk = request.POST.get('cnv_pk').strip()
		cnv = get_object_or_404(CNV, pk=cnv_pk)

		# only the user who created the comment can delete
		if request.user == comment.user:

			# only allow if classification is not complete
			if cnv.status == '0' or cnv.status == '1':

				comment.delete()

				comments = CNVUserComment.objects.filter(classification=cnv, visible=True)

				html = render_to_string('acmg_db/ajax_comments.html',
										{'comments': comments, 'user': request.user})

				return HttpResponse(html)

		else:

				comments = CNVUserComment.objects.filter(classification=cnv, visible=True)

				html = render_to_string('acmg_db/ajax_comments.html',
										{'comments': comments, 'user': request.user})

				return HttpResponse(html)



	else:

			raise PermissionDenied('You do not have permission to delete this comment.')
			
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_view_classification(request, pk):
	"""
	View a read only version of a classification of a CNV

	"""

	cnv = get_object_or_404(CNV, pk=pk)
	
	# Allow users to archive the classification
	if request.method == 'POST':

		if 'submit-archive' in request.POST:

			if cnv.status == '2':

				form = ArchiveCNVClassificationForm(request.POST, cnv_pk = cnv.pk)

				if form.is_valid():

					# Update status to archived
					cleaned_data = form.cleaned_data
					cnv.status = '3'
					cnv.save()
					return redirect('cnv_pending')

			else:

				raise PermissionDenied('You do not have permission to archive the classification.')
		
		
		
		# Allow users to assign the second check to themselves
		elif 'submit-assign' in request.POST:

			# Only allow user to reset if status is first or second analysis
			if cnv.status == '1' and cnv.user_second_checker != request.user:

				form = CNVAssignSecondCheckToMeForm(request.POST, cnv_pk = cnv.pk)

				if form.is_valid():

					cnv = get_object_or_404(CNV, pk=form.cnv_pk)

					cnv.user_second_checker = request.user
					cnv.save()

					return redirect('cnv_pending')

			else:

				raise PermissionDenied('You do not have permission to assign the second check to yourself.')	
		
		# Allow users to send back to first check
		elif 'submit-sendback' in request.POST:

			# Only allow user to reset if status is second check and the user is None, the first checker or 2nd checker
			if cnv.status == '1' and (cnv.user_second_checker == request.user or cnv.user_first_checker == request.user):

				form = CNVSendBackToFirstCheckForm(request.POST, cnv_pk = cnv.pk)

				if form.is_valid():

					cnv = get_object_or_404(CNV, pk=form.cnv_pk)

					# delete any second check answers
					if cnv.method == "Gain":
						cnv_answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
					elif cnv.method == "Loss":
						cnv_answers = CNVLossClassificationAnswer.objects.filter(cnv=cnv)

					for c_answer in cnv_answers:

						c_answer.score_second = False
						c_answer.comment_second = ""
						c_answer.save()

					# delete any second check comments
					cnv_comments = CNVUserComment.objects.filter(classification =cnv, user= cnv.user_second_checker)
					cnv_comments.delete()

					# reset other attributes
					cnv.first_check_date = None
					cnv.second_check_date = None
					cnv.user_second_checker = None
					cnv.status = '0'
					cnv.second_final_class = '5'
					cnv.save()

					return redirect('cnv_pending')

			else:

				raise PermissionDenied('You do not have permission to assign the second check to yourself.')	
		

		# Allow users to reset a classification
		elif 'submit-reset' in request.POST:

			# Only allow user to reset if status is first or second analysis
			if cnv.status == '0' or cnv.status == '1':

				form = CNVResetClassificationForm(request.POST, cnv_pk = cnv.pk)

				if form.is_valid():

					cnv = get_object_or_404(CNV, pk=form.cnv_pk)

					cnv.first_check_date = None
					cnv.second_check_date = None
					cnv.user_first_checker = None
					cnv.user_second_checker = None
					cnv.status = '0'
					cnv.genuine = '0'
					cnv.first_final_class = '5'
					cnv.second_final_class = '5'
					cnv.save()

					comments = CNVUserComment.objects.filter(classification=cnv)
					comments.delete()
					
					if cnv.method == "Gain":
						answers = CNVGainClassificationAnswer.objects.filter(cnv=cnv)
					elif cnv.method == "Loss":
						answers = CNVLossClassificationAnswer.objects.filter(cnv=cnv)
					answers.delete()

					return redirect('cnv_pending')

			else:

				raise PermissionDenied('You do not have permission to reset the classification.')
		

		
	if cnv.method == "Gain":
		cnv_answers = (CNVGainClassificationAnswer.objects.filter(cnv=cnv))
	elif cnv.method == "Loss":
		cnv_answers = (CNVLossClassificationAnswer.objects.filter(cnv=cnv))
		
	cnv_history = cnv.history.all()
	cnv_sample_history = cnv.sample.history.all()
	history = (cnv_history | cnv_sample_history).order_by('-timestamp')
	archive_form = ArchiveCNVClassificationForm(cnv_pk = cnv.pk)
	assign_form = CNVAssignSecondCheckToMeForm(cnv_pk = cnv.pk)
	sendback_form = CNVSendBackToFirstCheckForm(cnv_pk = cnv.pk)
	reset_form = CNVResetClassificationForm(cnv_pk = cnv.pk)	
	comments = CNVUserComment.objects.filter(classification=cnv, visible=True)
		
	return render(request, 'acmg_db/cnv_view_classification.html', 
			{	
				'cnv': cnv,
				'cnv_answers': cnv_answers,
				'comments': comments,
				'archive_form': archive_form,
				'reset_form': reset_form,
				'assign_form': assign_form,
				'sendback_form': sendback_form,
				'history': history
			}
		)

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_cnv(request, pk, ref):
	"""
	Page to view information about a specific CNV.

	"""
	
	cnvs = CNV.objects.filter(cnv__full = pk, cnv__genome =ref).order_by('-second_check_date')

	return render (request, 'acmg_db/view_cnv.html', {'cnvs': cnvs})
	

