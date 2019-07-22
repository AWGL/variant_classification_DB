from django.core.management.base import BaseCommand, CommandError
from acmg_db.models import *
import csv

class Command(BaseCommand):

	help = "dump variant and variant transcript tables."

	def add_arguments(self, parser):

		parser.add_argument('test', nargs =1, type = str)


	def handle(self, *args, **options):

		variants = Variant.objects.all()

		classifications = Classification.objects.all()

		variant_transcripts = TranscriptVariant.objects.all()

		with open('classification_map.csv', mode='w') as classification_csv:

			classification_writer = csv.writer(classification_csv, delimiter=',')

			for classification in classifications:

				pk = classification.pk

				variant_pk = classification.variant.pk
				variant_hash = classification.variant.variant_hash

				classification_writer.writerow([pk, variant_pk, variant_hash])


		with open('transcript_variant_map.csv', mode='w') as transcript_variant_csv:

			transcript_variant_writer = csv.writer(transcript_variant_csv, delimiter=',')

			for variant_transcript in variant_transcripts:

				pk = variant_transcript.pk

				variant_pk = variant_transcript.variant.pk
				variant_hash = variant_transcript.variant.variant_hash

				transcript_variant_writer.writerow([pk, variant_pk, variant_hash])