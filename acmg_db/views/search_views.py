from ..models import *
from ..forms import SearchForm
from ..utils.variant_utils import get_variant_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound
import re

@transaction.atomic
@login_required
def search(request):
	"""
	Page to allow user to search for samples, genes and variants.
	"""

	# make empty form
	form = SearchForm()

	message = None

	# if form submitted
	if request.method == 'POST':
		form = SearchForm(request.POST)

		if form.is_valid():
			
			search_input = form.cleaned_data['search_input'].upper().strip()

			# check if we've searched for sample
			x = re.search("^\d{2}M\d{5}", search_input)

			if x != None:

				samples = Sample.objects.filter(sample_name_only= search_input)

				if len(samples) == 0:

					message = f'Cannot find a sample with id {search_input}'
					return render(request, 'acmg_db/search.html', {'form': form, 'message': message})	

				else:	

					return redirect('view_sample', pk=search_input)

			# check if we've searched for a variant.
			x = re.search("^(X|Y|\d+):\d+(A|T|G|C)+>(A|T|G|C)+", search_input)

			if x != None:

				chromosome = search_input.split(':')[0]

				position = re.findall('\d+',search_input.split(':')[1])[0]

				ref = re.sub('[0-9]', '', search_input.split(':')[1].split('>')[0])

				alt = re.sub('[0-9]', '', search_input.split(':')[1].split('>')[1])

				var_hash = get_variant_hash(chromosome, position,ref, alt)

				try:

					variant = Variant.objects.get(variant_hash=var_hash)

				except:

					message = f'Cannot find a variant with id {search_input}'
					return render(request, 'acmg_db/search.html', {'form': form, 'message': message})

				return redirect('view_variant', pk=var_hash)

			# otherwise assume we tried to search for a gene
			try:

				gene = Gene.objects.get(name=search_input)

			except:

				message = f'Cannot find a gene with name {search_input}'

				return render(request, 'acmg_db/search.html', {'form': form, 'message': message})

			return redirect('view_gene', pk = gene.name)


	return render(request, 'acmg_db/search.html', {'form': form, 'message': message})


@transaction.atomic
@login_required
def view_gene(request, pk):
	"""
	Show all completed classifications for a gene.

	"""

	gene = get_object_or_404(Gene, pk=pk)

	transcripts_variants = TranscriptVariant.objects.filter(transcript__gene=gene)

	variants = [transcripts_variant.variant for transcripts_variant in transcripts_variants]

	variants = list(set(variants))

	most_recent_classifications = [[variant, variant.most_recent_classification()] for variant in variants]

	all_variants = list(filter(lambda x: x[1][0] != None, most_recent_classifications))

	return render(request, 'acmg_db/view_gene.html', {'gene': gene, 'all_variants': all_variants})

@transaction.atomic
@login_required
def view_sample(request, pk):
	"""
	Show all completed classifications for a sample.
	"""
	samples = Sample.objects.filter(sample_name_only= pk)

	if len(samples) == 0:

		return HttpResponseNotFound(f'No sample found for this id: {pk}')

	all_classifications = []

	# A sample pk is worksheet_id + '-' + sample_id + '-' + analysis performed
	# so loop through and get all classifications which match just the sample id bit
	for sample in samples:

		classifications = list(Classification.objects.filter(sample = sample))

		all_classifications = all_classifications + classifications

	return render(request, 'acmg_db/view_sample.html', {'samples': samples, 'all_classifications': all_classifications, 'sample_name': pk})