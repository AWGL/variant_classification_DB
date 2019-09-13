import unittest
from acmg_db.utils.variant_utils import *
from django.conf import settings


class TestVariantUtils(unittest.TestCase):


	def test_process_variant_input(self):

		input1 = '17:41197732GGGGGATGC>ATGC'
		input2 = '17:41197732AAAAG>ATTTTT'
		input3 = '1:41197732G>A'
		input4 = 'X:41197732G>AAA'
		input5 = 'M:41197732G>A'
		input6 = 'Y:41197732G>A'
		input7 = '13:4GTGAC>ATGC'

		self.assertEqual(process_variant_input(input1), ['e619796bddad0e522b9a127c3bea7906492173156fe5d566982ac06294a1c6b1', '17', '41197732', 'GGGGGATGC', 'ATGC', '17-41197732-GGGGGATGC-ATGC'])
		self.assertEqual(process_variant_input(input2), ['2bd177ad77d08a7d8ee305a6e5c8912a464186bddeaf0b3efe3557106c44d45d', '17', '41197732', 'AAAAG', 'ATTTTT', '17-41197732-AAAAG-ATTTTT'])
		self.assertEqual(process_variant_input(input3), ['1803ac07aaa1a21494fde4ddf6b2f154ac569e2dbb195c0d4428b21a74580e73', '1', '41197732', 'G', 'A', '1-41197732-G-A'])
		self.assertEqual(process_variant_input(input4), ['3b71486b09ad5b9c88a5604c6847eab432f1e419da68e01f9f49d628073ea567', 'X', '41197732', 'G', 'AAA', 'X-41197732-G-AAA'])
		self.assertEqual(process_variant_input(input5), ['8e6e0816a10135d2d295f2b42990e39e3037abe857bc1b0cdfb695905a61439c', 'M', '41197732', 'G', 'A', 'M-41197732-G-A'])
		self.assertEqual(process_variant_input(input6), ['e95a1742404bcc3c3c8f2ee44696b792a0cb634688a4349fa65195f5871ca027', 'Y', '41197732', 'G', 'A', 'Y-41197732-G-A'])
		self.assertEqual(process_variant_input(input7), ['cb5a43b1cc81e1ca7aaf6765ed8f3b76de40c83c81923399779f56086ba31303', '13', '4', 'GTGAC', 'ATGC', '13-4-GTGAC-ATGC'])

	
	def test_get_variant_info_mutalzer(self):

		input1 = 'hello'
		input2 = 'chr17:41197732GT>A' #should be 17:41197732GT>A i.e no chr
		input3 = '17:41197732GT>A' # valid
		input4 = 'X:32536115C>T' # valid


		self.assertEqual(get_variant_info_mutalzer(input1, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)[0], False)
		self.assertEqual(get_variant_info_mutalzer(input2, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)[0], False)
		self.assertEqual(get_variant_info_mutalzer(input3, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)[0], True)
		self.assertEqual(get_variant_info_mutalzer(input4, settings.MUTALYZER_URL, settings.MUTALYZER_BUILD)[0], True)
	



if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestVariantUtils)