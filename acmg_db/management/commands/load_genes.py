import csv
import ast

from django.core.management.base import BaseCommand, CommandError
from acmg_db.models import *
from django.db import transaction


class Command(BaseCommand):

	help = 'add gene info'

	def add_arguments(self, parser):

		parser.add_argument('--gene_file', nargs =1, type = str)

	def handle(self, *args, **options):

		data = options['gene_file'][0]

		with open(data) as csv_file:

			reader = csv.DictReader(csv_file)

			with transaction.atomic():

				for row in reader:

					symbol = row['symbol'].upper()

					hgnc_id = row['hgnc_id']

					phenotypes = row['parsed_phenotypes']

					existing_gene_obj = Gene.objects.filter(name=symbol)

					if len(existing_gene_obj) == 0:

						try:
							new_gene_obj = Gene(
								name = symbol,
								)

							new_gene_obj.save()

						except:

							raise Exception(f'Could not create gene {symbol}')


						if phenotypes == 'False':

							pass

						else:

							phenotypes = ast.literal_eval(phenotypes) 

							for phenotype in phenotypes:

								disease_name = phenotype.get('disease_name')
								inheritance = phenotype.get('inheritance')
								mapping_method = phenotype.get('mapping_method')
								mim_number = phenotype.get('mim_number')

								new_phenotype_obj = GenePhenotype(
									gene = new_gene_obj,
									disease_name = disease_name,
									inheritance = inheritance,
									manual=False)

								new_phenotype_obj.save()

					else:

						existing_gene_obj= existing_gene_obj[0]

						existing_phenotypes = GenePhenotype.objects.filter(gene= existing_gene_obj, manual=False)

						existing_phenotypes.delete()

						existing_gene_obj.save()

						if phenotypes == 'False':

							pass

						else:

							phenotypes = ast.literal_eval(phenotypes)

							for phenotype in phenotypes:

								disease_name = phenotype.get('disease_name')
								inheritance = phenotype.get('inheritance')


								new_phenotype_obj = GenePhenotype(
									gene = existing_gene_obj,
									disease_name = disease_name,
									inheritance = inheritance,
									manual=False
									)

								new_phenotype_obj.save()
