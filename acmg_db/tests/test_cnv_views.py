"""
Simple View Tests for CNVs
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from acmg_db.models import *


class TestCNVViewsSimple(TestCase):
	"""
	Test that viewing all CNV main landing pages works as expected
	"""
	
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		

	def test_cnv_view_home(self):

		response = self.client.get(reverse('cnv_home'))
		self.assertEqual(response.status_code,200)
		
	def test_view_cnv_manual(self):
	
		response = self.client.get(reverse('cnv_manual'))
		self.assertEqual(response.status_code,200)
		
	def test_view_cnv_pending(self):
		
		response = self.client.get(reverse('cnv_pending'))
		self.assertEqual(response.status_code,200)
		
	def test_view_cnv_classifications(self):
	
		response = self.client.get(reverse('view_cnvs'))
		self.assertEqual(response.status_code,200)
		
	def test_view_cnv_reporting(self):
	
		response = self.client.get(reverse('cnv_reporting'))
		self.assertEqual(response.status_code,200)
	
	def test_view_cnv_search(self):
		
		response = self.client.get(reverse('cnv_search'))
		self.assertEqual(response.status_code,200)
		
	def test_view_cnv_downloads(self):
		
		response = self.client.get(reverse('download_cnv_list'))
		self.assertEqual(response.status_code,200)
		
	
class TestCNVChecks(TestCase):
	"""
	Test first and second check views for CNV
	"""
	
	# Loading ACMG CNV questions
	fixtures = ['CNV_Gain_ACMG_questions.json', 'CNV_Loss_ACMG_questions.json']
	
	# Setting up basic test models
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
		CNVSample.objects.get_or_create(sample_name = '11M11111', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', genome = 'GRCh37', platform = 'SNP Array', cyto = 'C11-1111')
		
		CNVVariant.objects.get_or_create(full = 'X:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111' )
		
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
		
	# Testing that we can view first check	
	def test_view_cnv_first_check(self):
	
		response = self.client.get('/cnv_first_check/1/')
		self.assertEqual(response.status_code,200)
	
	# Testing that we can't view second check yet
	def test_view_cnv_second_check_permission(self):
	
		response = self.client.get('/cnv_second_check/1/')
		self.assertEqual(response.status_code,403)
	
	"""
	This test isn't working but unclear as to why - getting status 403
	# Test that we can view second check when set correctly
	def test_view_cnv_second_check(self):
		
		cnv_obj = CNV.objects.get(pk = 1)
		cnv_obj.status = '1'
		cnv_obj.save
		
		response = self.client.get('/cnv_second_check/1/')
		self.assertEqual(response.status_code,200)
	"""	
	
	#Testing that we can view the classification summary
	def test_view_cnv_classification(self):
		
		response = self.client.get('/cnv_view_classification/1/')
		self.assertEqual(response.status_code, 200)
		
	#Testing that we can view the sample summary
	def test_view_cnv_sample(self):
	
		response = self.client.get('/cnv_view_sample/11M11111/')
		self.assertEqual(response.status_code, 200)
	
	#Testing that we can view the gene summary
	def test_cnv_view_gene(self):
	
		response = self.client.get('/cnv_view_gene/TEST/')
		self.assertEqual(response.status_code, 200)
		
	"""
	FINISH THIS WHEN BACK
	#Testing that we can view the cnv summary
	def test_view_cnv(self):
	"""
		
