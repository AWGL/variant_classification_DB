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
	
	def test_process_cnv(self):
		
		cnv1 = "8:100-200"
		cnv2 = "5:111111-2222222"
		cnv3 = "Y:1-1000000"
		cnv4 = "X:500-501"
	
		self.assertEqual(process_cnv_input(cnv1), ['8','100','200'])
		self.assertEqual(process_cnv_input(cnv2), ['5','111111','2222222'])
		self.assertEqual(process_cnv_input(cnv3), ['Y','1','1000000'])
		self.assertEqual(process_cnv_input(cnv4), ['X','500','501'])
