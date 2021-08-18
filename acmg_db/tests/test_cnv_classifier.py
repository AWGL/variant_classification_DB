"""
Tests for CNV ACMG Classifier
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse

from acmg_db.models import *
from acmg_db.utils.cnv_utils import calculate_acmg_class, cnv_previous_classifications

class TestCNVScoreGain(TestCase):

	# Loading ACMG CNV questions
	fixtures = ['CNV_Gain_ACMG_questions.json', 'CNV_Loss_ACMG_questions.json']
	
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
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
		
	# Test if CNV score calculator returns 0 if no data passed via ajax for scores	
	def test_acmg_cnv_score_first_na(self):
		
		cnv = CNV.objects.get(pk=1)
		
		self.assertEqual(cnv.calculate_acmg_score_first(), 'NA')
		
	def test_acmg_cnv_score_second_na(self):
		
		cnv = CNV.objects.get(pk=1)
		
		self.assertEqual(cnv.calculate_acmg_score_second(), 'NA')
		
	
	# Test that data sent via ajax is correct and first score is calculated correctly
	def test_acmg_cnv_score_first_gain(self):
		
		response = self.client.get('/cnv_first_check/1/')
		
		# Create POST data for ajax submission and check class is updated
		data = {'cnvs': [('{" 1":["0.33","Comment"]," 2":["0.33","None"]," 3":["0.34","None"]," 4":["0","None"]," 5":["0","None"]," 6":["0","None"]," 7":["0","None"]," 8":["0","None"]," 9":["0","None"]," 10":["0","None"]," 11":["0","None"]," 12":["0","None"]," 13":["0","None"]," 14":["0","None"]," 15":["0","None"]," 16":["0","None"]," 17":["0","None"]," 18":["0","None"]," 19":["0","None"]," 20":["0","None"]," 21":["0","None"]," 22":["0","None"]," 23":["0","None"]," 24":["0","None"]," 25":["0","None"]," 26":["0","None"]," 27":["0","None"]," 28":["0","None"]," 29":["0","None"]," 30":["0","None"]," 31":["0","None"]," 32":["0","None"]," 33":["0","None"]," 34":["0","None"]," 35":["0","None"]," 36":["0","None"]," 37":["0","None"]," 38":["0","None"]," 39":["0","None"]," 40":["0","None"]," 41":["0","None"]}')], 'cnv_pk': ['1']}
		response = self.client.post('/ajax/acmg_cnv_classification_first/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		
		cnv_obj = CNV.objects.get(pk=1)

		self.assertEqual(cnv_obj.calculate_acmg_score_first(), 1.00)
	

#Testing for second checker		
class TestCNVScoreGainSecond(TestCase):

	# Loading ACMG CNV questions
	fixtures = ['CNV_Gain_ACMG_questions.json', 'CNV_Loss_ACMG_questions.json']
	
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
		CNVSample.objects.get_or_create(sample_name = '11M11111', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', platform = 'SNP Array', cyto = 'C11-1111')
		
		CNVVariant.objects.get_or_create(full = 'X:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='11M11111'),
					cnv = CNVVariant.objects.get(pk = 1),
					gain_loss = 'Gain',
					method = 'Gain',
					user_creator = self.user,
					status = "1"
		)
		
		CNVGene.objects.get_or_create(
						gene = 'TEST',
						cnv = CNV.objects.get(pk = 1)
		)
		
	
	def test_acmg_cnv_score_second_gain(self):
		
		response = self.client.get('/cnv_second_check/1/')
		
		# Create POST data for ajax submission and check class is updated
		data = {'cnvs': [('{" 1":["-1","Comment"]," 2":["0.5","None"]," 3":["1","None"]," 4":["0","None"]," 5":["0","None"]," 6":["0","None"]," 7":["0","None"]," 8":["0","None"]," 9":["0","None"]," 10":["0","None"]," 11":["0","None"]," 12":["0","None"]," 13":["0","None"]," 14":["0","None"]," 15":["0","None"]," 16":["0","None"]," 17":["0","None"]," 18":["0","None"]," 19":["0","None"]," 20":["0","None"]," 21":["0","None"]," 22":["0","None"]," 23":["0","None"]," 24":["0","None"]," 25":["0","None"]," 26":["0","None"]," 27":["0","None"]," 28":["0","None"]," 29":["0","None"]," 30":["0","None"]," 31":["0","None"]," 32":["0","None"]," 33":["0","None"]," 34":["0","None"]," 35":["0","None"]," 36":["0","None"]," 37":["0","None"]," 38":["0","None"]," 39":["0","None"]," 40":["0","None"]," 41":["0","None"]}')], 'cnv_pk': ['1']}
		response = self.client.post('/ajax/acmg_cnv_classification_second/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		
		cnv_obj = CNV.objects.get(pk=1)

		self.assertEqual(cnv_obj.calculate_acmg_score_second(), 0.5)
		
class TestCNVScoreLoss(TestCase):

	# Loading ACMG CNV questions
	fixtures = ['CNV_Gain_ACMG_questions.json', 'CNV_Loss_ACMG_questions.json']
	
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
		CNVSample.objects.get_or_create(sample_name = '11M11111', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', platform = 'SNP Array', cyto = 'C11-1111')
		
		CNVVariant.objects.get_or_create(full = 'X:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='11M11111'),
					cnv = CNVVariant.objects.get(pk = 1),
					gain_loss = 'Loss',
					method = 'Loss',
					user_creator = self.user
		)
		
		CNVGene.objects.get_or_create(
						gene = 'TEST',
						cnv = CNV.objects.get(pk = 1)
		)
		
	
	# Test that data sent via ajax is correct and first score is calculated correctly
	def test_acmg_cnv_score_first_loss(self):
		
		response = self.client.get('/cnv_first_check/1/')
		
		# Create POST data for ajax submission and check class is updated
		data = {'cnvs': [('{" 1":["0.33","Comment"]," 2":["0.33","None"]," 3":["0.34","None"]," 4":["0","None"]," 5":["0","None"]," 6":["0","None"]," 7":["0","None"]," 8":["0","None"]," 9":["0","None"]," 10":["0","None"]," 11":["0","None"]," 12":["0","None"]," 13":["0","None"]," 14":["0","None"]," 15":["0","None"]," 16":["0","None"]," 17":["0","None"]," 18":["0","None"]," 19":["0","None"]," 20":["0","None"]," 21":["0","None"]," 22":["0","None"]," 23":["0","None"]," 24":["0","None"]," 25":["0","None"]," 26":["0","None"]," 27":["0","None"]," 28":["0","None"]," 29":["0","None"]," 30":["0","None"]," 31":["0","None"]," 32":["0","None"]," 33":["0","None"]," 34":["0","None"]," 35":["0","None"]," 36":["0","None"]," 37":["0","None"]," 38":["0","None"]," 39":["0","None"]," 40":["0","None"]," 41":["0","None"]," 42":["0","None"]," 43":["0","None"]}')], 'cnv_pk': ['1']}
		response = self.client.post('/ajax/acmg_cnv_classification_first/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		
		cnv_obj = CNV.objects.get(pk=1)

		self.assertEqual(cnv_obj.calculate_acmg_score_first(), 1.00)

#Testing for second checker		
class TestCNVScoreLossSecond(TestCase):

	# Loading ACMG CNV questions
	fixtures = ['CNV_Gain_ACMG_questions.json', 'CNV_Loss_ACMG_questions.json']
	
	def setUp(self):

		self.user = User.objects.create_user('test', 'admin@test.com', 'hello123')
		self.client.login(username='test', password= 'hello123')
		
		Worklist.objects.get_or_create(name='12-12345')
		
		Panel.objects.get_or_create(panel='Array', added_by = self.user)
		
		CNVSample.objects.get_or_create(sample_name = '11M11111', worklist = Worklist.objects.get(name = '12-12345'), affected_with = 'phenotype', analysis_performed = Panel.objects.get(panel = 'Array'), analysis_complete = 'False', platform = 'SNP Array', cyto = 'C11-1111')
		
		CNVVariant.objects.get_or_create(full = 'X:123456:234567', chromosome = 'X', start = '123456', stop = '234567', length = '111111', genome = 'GRCh37')
		
		CNV.objects.get_or_create(
					sample = CNVSample.objects.get(sample_name='11M11111'),
					cnv = CNVVariant.objects.get(pk = 1),
					gain_loss = 'Loss',
					method = 'Loss',
					user_creator = self.user,
					status = "1"
		)
		
		CNVGene.objects.get_or_create(
						gene = 'TEST',
						cnv = CNV.objects.get(pk = 1)
		)
		
	
	def test_acmg_cnv_score_second_loss(self):
		
		response = self.client.get('/cnv_second_check/1/')
		
		# Create POST data for ajax submission and check class is updated
		data = {'cnvs': [('{" 1":["-1","Comment"]," 2":["0.5","None"]," 3":["1","None"]," 4":["0","None"]," 5":["0","None"]," 6":["0","None"]," 7":["0","None"]," 8":["0","None"]," 9":["0","None"]," 10":["0","None"]," 11":["0","None"]," 12":["0","None"]," 13":["0","None"]," 14":["0","None"]," 15":["0","None"]," 16":["0","None"]," 17":["0","None"]," 18":["0","None"]," 19":["0","None"]," 20":["0","None"]," 21":["0","None"]," 22":["0","None"]," 23":["0","None"]," 24":["0","None"]," 25":["0","None"]," 26":["0","None"]," 27":["0","None"]," 28":["0","None"]," 29":["0","None"]," 30":["0","None"]," 31":["0","None"]," 32":["0","None"]," 33":["0","None"]," 34":["0","None"]," 35":["0","None"]," 36":["0","None"]," 37":["0","None"]," 38":["0","None"]," 39":["0","None"]," 40":["0","None"]," 41":["0","None"]," 42":["0","None"]," 43":["0","None"]}')], 'cnv_pk': ['1']}
		response = self.client.post('/ajax/acmg_cnv_classification_second/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
		
		cnv_obj = CNV.objects.get(pk=1)

		self.assertEqual(cnv_obj.calculate_acmg_score_second(), 0.5)
		
class TestCNVClassifier(TestCase):

	def test_cnv_classifier(self):
		
		#Pathogenic
		self.assertEqual(calculate_acmg_class(1.00),"4")
		#Likely Pathogenic
		self.assertEqual(calculate_acmg_class(0.92),"3")
		#VUS
		self.assertEqual(calculate_acmg_class(0),"2")
		#Likely Benign
		self.assertEqual(calculate_acmg_class(-0.92),"1")
		#Benign
		self.assertEqual(calculate_acmg_class(-1.00),"0")
