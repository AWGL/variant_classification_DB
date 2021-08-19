import unittest
from acmg_db.utils.variant_utils import *
from django.conf import settings
from django.test import TestCase


class TestVariantUtils(unittest.TestCase):


	def test_process_variant_input(self):

		input1 = ('17:41197732GGGGGATGC>ATGC')
		input2 = ('17:41197732AAAAG>ATTTTT')
		input3 = ('1:41197732G>A')
		input4 = ('X:41197732G>AAA')
		input5 = ('M:41197732G>A')
		input6 = ('Y:41197732G>A')
		input7 = ('13:4GTGAC>ATGC')
		ref1 = ('GRCh37')
		ref2 = ('GRCh38')

		self.assertEqual(process_variant_input(input1,ref1), ['e619796bddad0e522b9a127c3bea7906492173156fe5d566982ac06294a1c6b1', '17', '41197732', 'GGGGGATGC', 'ATGC', '17-41197732-GGGGGATGC-ATGC'])
		self.assertEqual(process_variant_input(input2,ref2), ['abc7c2260d6991379ca3bafb2ce7a5381e14161136b9ff26742491d3761f4947', '17', '41197732', 'AAAAG', 'ATTTTT', '17-41197732-AAAAG-ATTTTT'])
		self.assertEqual(process_variant_input(input3,ref1), ['1803ac07aaa1a21494fde4ddf6b2f154ac569e2dbb195c0d4428b21a74580e73', '1', '41197732', 'G', 'A', '1-41197732-G-A'])
		self.assertEqual(process_variant_input(input4,ref2), ['95394400756ce41824f8a728f87722051f7d105aaa69f22955f535f660caa037', 'X', '41197732', 'G', 'AAA', 'X-41197732-G-AAA'])
		self.assertEqual(process_variant_input(input5,ref1), ['8e6e0816a10135d2d295f2b42990e39e3037abe857bc1b0cdfb695905a61439c', 'M', '41197732', 'G', 'A', 'M-41197732-G-A'])
		self.assertEqual(process_variant_input(input6,ref2), ['fead1b193511ee17dd92c6a554f664027005c7a5af5fd19536bfca7b338f2951', 'Y', '41197732', 'G', 'A', 'Y-41197732-G-A'])
		self.assertEqual(process_variant_input(input7,ref1), ['cb5a43b1cc81e1ca7aaf6765ed8f3b76de40c83c81923399779f56086ba31303', '13', '4', 'GTGAC', 'ATGC', '13-4-GTGAC-ATGC'])



if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestVariantUtils)
