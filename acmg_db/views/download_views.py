import csv
import random
import os

from acmg_db.forms import DownloadVariantListForm
from acmg_db.models import *

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render
from django.db.models import Prefetch
from django.conf import settings
from django.http import HttpResponse

@transaction.atomic
@login_required
def download_variant_list(request):
	"""
	Page to download variant lists
	"""

	# make empty form
	form = DownloadVariantListForm()

	# if form submitted
	if request.method == 'POST':
		form = DownloadVariantListForm(request.POST)

		if form.is_valid():


			whitelist_classes = form.cleaned_data['white_list']
			blacklist_classes = form.cleaned_data['black_list']

			print (whitelist_classes, blacklist_classes)

			all_variants_query = Variant.objects.prefetch_related(
				Prefetch(
					'variant_classifications', 
					queryset=Classification.objects.filter(
							status__in=['2', '3']
						).select_related(
							'selected_transcript_variant', 
							'selected_transcript_variant__transcript', 
							'selected_transcript_variant__transcript__gene', 
						).order_by('-second_check_date'), 
					to_attr='variant_classification_cache'),
			).order_by('chromosome', 'position')
			
			# loop through each variant to parse data
			variant_data = []
			for variant in all_variants_query:

				# skip if there are no linked classifications
				if len(variant.variant_classification_cache) > 0:

					# parse info
					most_recent_obj = variant.variant_classification_cache[0]
					most_recent_class = most_recent_obj.get_second_final_class_display()
					if most_recent_obj.selected_transcript_variant.hgvs_c:
						hgvs_c = most_recent_obj.selected_transcript_variant.hgvs_c.split(':')[1]
					else:
						hgvs_c = None
					if most_recent_obj.selected_transcript_variant.hgvs_p:
						hgvs_p = most_recent_obj.selected_transcript_variant.hgvs_p.split(':')[1]
					else:
						hgvs_p = None
					transcript = most_recent_obj.selected_transcript_variant.transcript.name
					gene = most_recent_obj.selected_transcript_variant.transcript.gene.name

					# get list of all unique classifications
					all_classes_set = set()
					for classification in variant.variant_classification_cache:
						all_classes_set.add(classification.get_second_final_class_display())

					# add dict containing variant info to list
					variant_data.append({
						'variant_id': str(variant),
						'variant_hash': variant.variant_hash,
						'gene': gene,
						'transcript': transcript,
						'hgvs_c': hgvs_c,
						'hgvs_p': hgvs_p,
						'num_classifications': len(variant.variant_classification_cache), 
						'most_recent_obj': most_recent_obj, 
						'most_recent_date': most_recent_obj.second_check_date, 
						'most_recent_class': most_recent_obj.get_second_final_class_display(), 
						'all_classes': '|'.join(all_classes_set)
					})

			variant_list = []
			for variant in variant_data:

				variant_id = variant['variant_id']
				variant_annotation = variant['most_recent_class']

				if variant_annotation in whitelist_classes and variant_annotation in blacklist_classes:

					errors = ['Cannot be in both!']

					return render(request, 'acmg_db/download_variant_list.html', {'form': form, 'errors': errors}) 

				if variant_annotation in whitelist_classes:

					keep_or_discard = 'white'

				elif variant_annotation in blacklist_classes:

					keep_or_discard = 'black'


				else:

					keep_or_discard = 'none'


				variant_list.append([variant_id, keep_or_discard, variant_annotation])

			print (variant_list)

			file_name = f'variant_list_{request.user}_{random.randint(1,100000)}.csv'
			file_path = f'{settings.VEP_TEMP_DIR}/{file_name}'
			
			with open(file_path, mode='w') as variant_list_file:
				variant_list_writer = csv.writer(variant_list_file , delimiter=',')

				for row in variant_list:
					variant_list_writer.writerow(row)


			response = HttpResponse(open(file_path, 'rb').read())
			response['Content-Type'] = 'text/plain'
			response['Content-Disposition'] = f'attachment; filename={file_name}'

			os.remove(file_path)

			return response














	return render(request, 'acmg_db/download_variant_list.html', {'form': form})