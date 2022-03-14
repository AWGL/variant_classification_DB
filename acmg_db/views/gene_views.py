from django.shortcuts import render, get_object_or_404, redirect

from acmg_db.models import Gene, GenePhenotype
from acmg_db.forms import PhenotypeForm

def view_gene_phenotypes(request, pk):
	"""
	Page for viewing info on a gene

	"""

	gene = get_object_or_404(Gene, name=pk)

	gene_phenotypes = GenePhenotype.objects.filter(gene=gene)

	return render(request, 'acmg_db/view_gene_phenotypes.html', {'gene': gene, 'gene_phenotypes': gene_phenotypes})


def edit_gene_phenotype(request, pk):
	"""
	Edit a GenePhenotype object

	"""

	gene_phenotype =  get_object_or_404(GenePhenotype, pk=pk)


	if request.method == "POST":

		form = PhenotypeForm(request.POST, instance=gene_phenotype)

		if form.is_valid():

			gene_phenotype = form.save(commit=False)

			gene_phenotype.save()

			return redirect('view_gene_phenotypes', gene_phenotype.gene.pk)


	else:

		form = PhenotypeForm(instance=gene_phenotype)

	return render(request, 'acmg_db/edit_gene_phenotype.html', {'gene_phenotype': gene_phenotype, 'form': form})


def delete_gene_phenotype(request, pk):
	"""
	Delete a GenePhenotype object

	"""

	gene_phenotype =  get_object_or_404(GenePhenotype, pk=pk)

	gene_phenotype.delete()

	return redirect('view_gene_phenotypes', gene_phenotype.gene.pk)


