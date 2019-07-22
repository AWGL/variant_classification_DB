from django.core.management.base import BaseCommand, CommandError
from acmg_db.models import *
import csv

class Command(BaseCommand):

	help = "fix variant pks"

	def add_arguments(self, parser):

		parser.add_argument('test', nargs =1, type = str)


	def handle(self, *args, **options):

		classifications = Classification.objects.all()

		variant_transcripts = TranscriptVariant.objects.all()

		with open('classification_map.csv', mode ='r') as csv_file:

			csv_reader = csv.reader(csv_file, delimiter=',')

			for row in csv_reader:

				print (row)

				classification = Classification.objects.get(pk=row[0])

				variant = Variant.objects.get(variant_hash=row[2])

				print (variant)
				print(classification)

				classification.variant = variant

				classification.save()


		with open('transcript_variant_map.csv', mode ='r') as csv_file:

			csv_reader = csv.reader(csv_file, delimiter=',')

			for row in csv_reader:

				transcript_variant = TranscriptVariant.objects.get(pk=row[0])

				variant = Variant.objects.get(variant_hash=row[2])

				print (variant)
				print(classification)

				transcript_variant.variant = variant

				transcript_variant.save()