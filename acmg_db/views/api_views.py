import hashlib

from django.db import transaction
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from acmg_db.models import Panel, Worklist, Sample, Gene, Transcript, Variant, TranscriptVariant, Classification
from acmg_db.utils.variant_utils import get_vep_info_local, process_variant_input
from acmg_db.utils.acmg_classifier import guideline_version

class AddVariantsForAnalysis(APIView):
	"""
	View for adding variants for analysis via API

	"""
	
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		content = {'message': 'Hello, World!'}
		return Response(content)

	def post(self, request):
		"""
		Post data with variants

		variant_list: (list)- A list containing the variants to be added e.g. [[1:123A>G, 'HET'], [1:256A>G, 'HOM']]
		n_variants: (int) - An integer with the length of variants
		variant_hash: (str) - A sha256 hash of all the variants concated together - data integrity check
		analysis_performed: (str) - the type of analysis or panel applied
		sample_id: (str) - the panel applied
		worksheet_id: (str) - the worksheet id
		analysis_id: (int) - an analysis id
		genome: (str) - the reference genome used

		"""

		try:

			variant_list = request.data['variant_list']
			n_variants = request.data['n_variants']
			variant_hash = request.data['variant_hash']
			analysis_performed = request.data['analysis_performed']
			sample_id = request.data['sample_id']
			worksheet_id = request.data['worksheet_id']
			analysis_id = request.data['analysis_id']
			genome = request.data['reference']

		except KeyError:

			raise Exception('invalid post data')

		with transaction.atomic():

			# check the lengths match
			if len(variant_list) != n_variants:

				raise Exception('Length of variant list does not match set')


			# get hash of all joined variants
			variant_str = ''

			for variant in variant_list:

				variant_str = variant_str + variant[0]


			arrival_hash = hashlib.sha256(bytes(variant_str, 'utf-8')).hexdigest()

			#print (arrival_hash)

			# error if hashes dont match
			if variant_hash != arrival_hash:

				raise Exception('hashes do not match - error during data transfer')

			try:

				panel_obj = Panel.objects.get(panel= analysis_performed)

			except Panel.DoesNotExist:

				panel_obj = Panel.objects.create(panel=analysis_performed, added_by=request.user)
				panel_obj.save()

			sample_name = worksheet_id + '-' + sample_id + '-' + panel_obj.pk

			# add worksheet
			worksheet_obj, created = Worklist.objects.get_or_create(
					name = worksheet_id
					)


			# add sample
			try:
				sample_obj = Sample.objects.get(name=sample_name)

				raise Exception('already a sample with this id')

			except Sample.DoesNotExist:
				sample_obj = Sample.objects.create(
						name = sample_name,
						sample_name_only = sample_id,
						worklist = worksheet_obj,
						affected_with = 'input required',
						analysis_performed = panel_obj,
						analysis_complete = False,
						other_changes = '',
						genome = genome,
						)
				sample_obj.save()


			# Get VEP annotations
			if genome == 'GRCh37':
				vep_info_dict = {
					'reference_genome' : settings.REFERENCE_GENOME_37,
					'vep_cache': settings.VEP_CACHE_37,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_37,
					'version': settings.VEP_VERSION_37
				}
			elif genome == 'GRCh38':
				vep_info_dict = {
					'reference_genome': settings.REFERENCE_GENOME_38,
					'vep_cache': settings.VEP_CACHE_38,
					'temp_dir': settings.VEP_TEMP_DIR,
					'assembly': settings.ASSEMBLY_38,
					'version': settings.VEP_VERSION_38
				}

			# set vep version
			if genome == "GRCh37":
				vep_version = settings.VEP_VERSION_37
			elif genome == "GRCh38":
				vep_version = settings.VEP_VERSION_38

			just_variants = [variant[0] for variant in variant_list]


			variant_genotype_dict = {}

			for variant in variant_list:

				variant_genotype_dict[variant[0]] = variant[1]

			try:
				variant_annotations = get_vep_info_local(just_variants, vep_info_dict, sample_id)
			except:

				raise Exception('failed vep annotation')


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


					gene_obj, created = Gene.objects.get_or_create(
						name = gene_symbol
						)

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
						"""
						# only add the vep version if its a new transcript, otherwise there will be duplicates for each vep version
						if genome == "GRCh37":
							vep_version = settings.VEP_VERSION_37
						elif genome == "GRCh38":
							vep_version = settings.VEP_VERSION_38
						"""
						transcript_variant_obj.vep_version = vep_version
						transcript_variant_obj.save()
					
					else:

						transcript_variant_obj = transcript_variant_obj[0]


					# Find the transcript that VEP has picked
					if 'pick' in consequence:

						selected = transcript_variant_obj

				# process the genotype
				genotype = variant_genotype_dict[f'{variant_obj.chromosome}:{variant_obj.position}{variant_obj.ref}>{variant_obj.alt}']

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
					vep_version=vep_version,
					analysis_id = analysis_id
					)

				new_classification_obj.save()


			return Response('success')
