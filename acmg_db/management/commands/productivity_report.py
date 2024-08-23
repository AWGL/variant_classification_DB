from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from acmg_db.models import *

import csv
from datetime import datetime, timedelta

class Command(BaseCommand):

    help = "Produce productivity report from CNVs classifications"

    def add_arguments(self, parser):

        parser.add_argument('--output_file', nargs=1, type=str)

    def handle(self, *args, **options):

        output = options['output_file'][0]

        out = open(output, "w")

        #Set capture date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=28)

        #Get all CNVs either first check or complete
        cnvs = CNV.objects.filter(Q(status='1')|Q(status='2'))

        for cnv in cnvs:
            
            #Get only those with a first checker date in the specified date range - last 28 days
            if cnv.first_check_date != None:

                within_timeframe = start_date.date() <= cnv.first_check_date.date() <= end_date.date()

                if within_timeframe:

                    if cnv.first_check_date != None:

                        out.write(f"{cnv.sample.sample_name},{cnv.user_first_checker},First_Check\n")

            #Get second checks
            if cnv.second_check_date != None:

                within_timeframe = start_date.date() <= cnv.second_check_date.date() <= end_date.date()

                if within_timeframe:

                    if cnv.second_check_date != None:

                        out.write(f"{cnv.sample.sample_name},{cnv.user_second_checker},Second_Check\n")

