from ..models import *

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_variants(request):
	"""
	Page to view all unique variants classified in the lab

	"""
	all_variants = Variant.objects.all().order_by('chromosome', 'position')

	# annotate each variant with information about how it was classified
	most_recent_classifications = [[variant, variant.most_recent_classification()] for variant in all_variants]

	# Filter out the variants with no classification
	most_recent_classifications = list(filter(lambda x: x[1][0] != None, most_recent_classifications))

	return render(request, 'acmg_db/view_variants.html', {'all_variants': most_recent_classifications})


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
