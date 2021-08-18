"""
Tests for CNV ACMG Classifier
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from acmg_db.models import *
from acmg_db.utils.cnv_utils import process_cnv_input, cnv_previous_classifications

class TestProcessCNV(TestCase):
	"""
	Testing process_cnv_input from utils
	"""
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
	def test_process_cnv(self):
		
		cnv1 = "8:100-200"
		cnv2 = "5:111111-2222222"
		cnv3 = "Y:1-1000000"
		cnv4 = "X:500-501"
	
		self.assertEqual(process_cnv_input(cnv1), ['8','100','200'])
		self.assertEqual(process_cnv_input(cnv2), ['5','111111','2222222'])
		self.assertEqual(process_cnv_input(cnv3), ['Y','1','1000000'])
		self.assertEqual(process_cnv_input(cnv4), ['X','500','501'])

class TestProcessCNV(TestCase):	
	"""
	Testing the identication of overlapping previous classifications with 50% reciprocal overlap
	"""
		
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
		# 'New'CNV set up
		CNVSample.objects.get_or_create(sample_name = '11M11111', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', platform = 'SNP Array', cyto = 'C11-1111')
		
		CNVVariant.objects.get_or_create(full = 'X:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='11M11111'),
					cnv = CNVVariant.objects.get(pk = 1),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user
		)
		
		CNVGene.objects.get_or_create(
						gene = 'TEST',
						cnv = CNV.objects.get(pk = 1)
		)
		
		# Existing CNV	(already classified) set up
		
		CNVSample.objects.get_or_create(sample_name = '22M22222', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', platform = 'SNP Array', cyto = 'C22-2222')
		
		# Identical CNV to 'New'
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 1),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing CNV entirely within new CNV
		CNVVariant.objects.get_or_create(full = 'X:134567:223456', chromosome = 'X', start = '134567', stop = '223456', length = '88889', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 2),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# New CNV entirely within existing CNV
		CNVVariant.objects.get_or_create(full = 'X:112345:245678', chromosome = 'X', start = '112345', stop = '245678', length = '133333', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 3),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		
		# Existing CNV starts and stops after new
		CNVVariant.objects.get_or_create(full = 'X:134567:245678', chromosome = 'X', start = '134567', stop = '245678', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 4),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing CNV starts and stops before new
		CNVVariant.objects.get_or_create(full = 'X:112345:223456', chromosome = 'X', start = '112345', stop = '223456', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 5),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing overlaps but not by 50% reciprocal overlap
		CNVVariant.objects.get_or_create(full = 'X:234560:234570', chromosome = 'X', start = '234560', stop = '234570', length = '10', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 6),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing doesn't overlap
		CNVVariant.objects.get_or_create(full = 'X:345678:456789', chromosome = 'X', start = '345678', stop = '456789', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 7),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing has same coordinates but different chromosome, therefore doesn't overlap
		CNVVariant.objects.get_or_create(full = '1:123456:234567', chromosome = '1', start = '123456', stop = '234567', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 8),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
		# Existing is identical but from different reference genome, therefore doesn't overlap
		CNVVariant.objects.get_or_create(full = '1:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111', genome = 'GRCh38')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='22M22222'),
					cnv = CNVVariant.objects.get(pk = 9),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = '2',
					genuine = '1'
		)
		
	def test_previous_cnv(self):
		
		cnv_obj = CNV.objects.get(pk=1)
		
		previous,previous_full = cnv_previous_classifications(cnv_obj)
		
		self.assertEqual(len(previous), 5)
		self.assertEqual(len(previous_full), 5)
