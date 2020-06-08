from ..models import *

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_variants(request):
	"""
	Page to view all unique variants classified in the lab

	"""
	# query all variants, prefetch related classification objects and associated transcript/ gene objects
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

	return render(request, 'acmg_db/view_variants.html', {'all_variants': variant_data})


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_variant(request, pk):
	"""
	Page to view information about a specific variant.

	"""

	variant = get_object_or_404(Variant, variant_hash = pk)

	classifications = Classification.objects.filter(variant = variant).order_by('-second_check_date')

	return render (request, 'acmg_db/view_variant.html', {'variant': variant, 'classifications': classifications})
