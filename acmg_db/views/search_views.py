import re

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseNotFound
from django.db.models import Prefetch

from acmg_db.models import *
from acmg_db.forms import SearchForm, CNVSearchForm, CNVAdvancedSearchForm
from acmg_db.utils.variant_utils import get_variant_hash


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
	
#----------
def cnv_search(request):
	"""
	Page to allow user to search for CNVs, samples, and genes.
	"""

	# make empty form
	form = CNVSearchForm()
	adv_form = CNVAdvancedSearchForm()

	message = None

	# if form submitted
	if request.method == 'POST':
		
		if 'search_input' in request.POST:
			
			form = CNVSearchForm(request.POST)

			if form.is_valid():
				
				search_input = form.cleaned_data['search_input'].upper().strip()

				# check if we've searched for sample
				x = re.search("^\d{2}M\d{5}", search_input)

				if x != None:

					samples = CNVSample.objects.filter(sample_name= search_input)

					if len(samples) == 0:

						message = f'Cannot find a sample with id {search_input}'
						return render(request, 'acmg_db/cnv_search.html', {'form': form, 'adv_form' : adv_form, 'message': message})	

					else:	

						return redirect('cnv_view_sample', pk=search_input)

				# check if we've searched for a CNV.
				x = re.search("^(X|Y|\d+):\d+-\d+", search_input)
				
				if x != None:
					
					cnv = CNVVariant.objects.filter(full=search_input)
					
					if len(cnv) == 0:

						message = f'Cannot find a CNV with id {search_input}'
						return render(request, 'acmg_db/cnv_search.html', {'form': form, 'adv_form' : adv_form, 'message': message})
					else:
						return redirect('view_cnv_search', pk=search_input)

				# otherwise assume we tried to search for a gene
				else:

					gene = CNVGene.objects.filter(gene=search_input)

					if len(gene) == 0:

						message = f'Cannot find a gene with name {search_input}'

						return render(request, 'acmg_db/cnv_search.html', {'form': form, 'adv_form' : adv_form, 'message': message})
					
					else:
						return redirect('cnv_view_gene', pk = search_input)

		if 'chromosome' in request.POST:
			
			form = CNVAdvancedSearchForm(request.POST)

			if form.is_valid():
					
				chromosome = form.cleaned_data['chromosome']
				start = form.cleaned_data['start']
				stop = form.cleaned_data['stop']
				
				pk = chromosome+":"+start+"-"+stop
					
				cnv_var = CNVVariant.objects.filter(chromosome=chromosome, start__gte=start, stop__lte=stop)
					
				if len(cnv_var) == 0:

					message = f'Cannot find a CNV on chromosome {chromosome} between {start} and {stop}'

					return render(request, 'acmg_db/cnv_search.html', {'form': form, 'adv_form' : adv_form, 'message': message})
					
				else:
						
					return redirect('cnv_view_region', pk = pk)
					
					
	
	return render(request, 'acmg_db/cnv_search.html', {'form': form, 'adv_form': adv_form,'message': message})
	
#-----------
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

#-----------
@transaction.atomic
@login_required
def cnv_view_gene(request, pk):
	"""
	Show all completed CNV classifications for a gene.

	"""
	genes = CNVGene.objects.filter(gene=pk, cnv__status__in=['2','3']).order_by('cnv__second_check_date')

	return render(request, 'acmg_db/cnv_view_gene.html', {'genes': genes})

#--------
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

#--------
@transaction.atomic
@login_required
def cnv_view_sample(request, pk):
	"""
	Show all completed classifications for a sample.
	"""
	samples = CNVSample.objects.filter(sample_name = pk)

	if len(samples) == 0:

		return HttpResponseNotFound(f'No sample found for this id: {pk}')

	all_cnvs = []

	# A sample pk is worksheet_id + '-' + sample_id + '-' + analysis performed
	# so loop through and get all classifications which match just the sample id bit
	for sample in samples:

		cnv = list(CNV.objects.filter(sample = sample, status__in=['2','3']))

		all_cnvs = all_cnvs + cnv

	return render(request, 'acmg_db/cnv_view_sample.html', {'samples': samples, 'all_cnvs': all_cnvs, 'sample_name': pk})
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_cnv_search(request, pk):
	"""
	Page to view information about a specific CNV.

	"""
	
	cnvs = CNV.objects.filter(cnv__full = pk).order_by('-second_check_date')

	return render (request, 'acmg_db/view_cnv_search.html', {'cnvs': cnvs})
	
#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def cnv_view_region(request, pk):
	"""
	Page to view information about a specific CNV.

	"""
	#split pk into chromosome, start and stop
	chromosome = pk.split(":")[0]
	coord = pk.split(":")[1]
	start = coord.split("-")[0]
	stop = coord.split("-")[1]
	
	print(chromosome)
	print(start)
	print(stop)
	
	cnv_var = CNVVariant.objects.filter(chromosome=chromosome, start__gte=start, stop__lte=stop).prefetch_related(
		Prefetch(
			'cnv_classification', 
			queryset=CNV.objects.filter(
					status__in=['2', '3']
				).order_by('-second_check_date'), 
			to_attr='cnv_classification_cache'),
	).order_by('chromosome', 'start')
	
	# loop through each variant to parse data
	cnv_data = []
	for cnv in cnv_var:
		
		
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

	return render (request, 'acmg_db/cnv_view_region.html', {'cnvs': cnv_data, 'chromosome' : chromosome, 'start': start, 'stop': stop})
