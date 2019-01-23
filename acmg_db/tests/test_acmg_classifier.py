import unittest
from acmg_db.utils.acmg_classifier import *

class TestACMGRatings(unittest.TestCase):


	def test_pathogenic(self):

		test_1a_1 = ['PVS1', 'PS1']
		test_1a_2 = ['PVS1', 'PS2', 'BS1']
		test_1a_3 = ['PVS1', 'PS3', 'PS4', 'PS1']
		test_1a_4 = ['PVS1', 'PS3', 'PS4', 'PS2', 'PS1' ]
		test_1a_5 = ['PVS1', 'PS3', 'PS4', 'PS1', 'PM1', 'PM2', 'BP1' ]
		test_1a_6 = ['PVS1', 'PS3']
		test_1a_7 = ['PVS1', 'PS3' ,'BA1']
		test_1a_8 = ['PVS1', 'PS3' ,'PM2', 'BS1', 'PM1', 'BS2', 'BP3', 'BP4' ]
		
		test_1b_1 = ['PVS1', 'PM1', 'PM6']
		test_1b_2 = ['PVS1', 'PM1', 'PM6', 'PM3']
		test_1b_3 = ['PVS1', 'PM2', 'PM5']
		test_1b_4 = ['PVS1', 'PM1', 'PM3', 'BS1']
		test_1b_5 = ['PVS1', 'PM4', 'BP1', 'PM2']
		test_1b_6 = ['PM5', 'BP6', 'BA1' 'PM4', 'PM2', 'PM3', 'PVS1']
		
		test_1c_1 = ['PVS1', 'PM1', 'PP1']
		test_1c_2 = ['PM1', 'PP2', 'PVS1']
		test_1c_3 = ['PP5', 'PVS1', 'PM1']
		test_1c_4 = ['PVS1', 'BS1', 'PP3', 'PM2']
		test_1c_5 = ['PVS1', 'PP2', 'BA1', 'BS2', 'PM4']
		test_1c_6 = ['PM2', 'PP2', 'PP3', 'PP4', 'PSV1']
		
		test_1d_1 = ['PVS1', 'PP1', 'PP2', 'PP3']
		test_1d_2 = ['PVS1', 'PP2', 'PP4']
		test_1d_3 = ['PVS1', 'PP5', 'PP1', 'BA1', 'BS1', 'BS2', 'BS3']
		test_1d_4 = ['PVS1', 'BS3', 'PP2', 'PP4']
		test_1d_5 = ['PVS1', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5']
		test_1d_6 = ['PP3', 'PP1', 'PVS1']
		test_1d_7 = ['PP4', 'PVS1', 'PP5']

		test_2_1 = ['PS1', 'PS2', 'PS3']
		test_2_2 = ['PS1', 'PS2']
		test_2_3 = ['PS4', 'PS3']
		test_2_4 = ['PS1', 'PS2', 'PS3', 'PS4']
		test_2_5 = ['BS1', 'BS2', 'PS1', 'PS2', 'PS3', 'PS4']
		test_2_6 = ['PS1', 'BS1', 'PS2', 'BS3', 'PS3', 'PS4']
					
		test_3a_1 = ['PS1', 'PM1', 'PM2', 'PM3', 'PM4']
		test_3a_2 = ['PS1', 'PM1', 'PM2', 'PM3', 'PP1']
		test_3a_3 = ['PP3', 'PM1', 'PM2', 'PM3', 'PS2']
		test_3a_4 = ['PS1', 'PM1', 'PM2', 'PM3']
		test_3a_5 = ['BA1', 'BS1', 'BS2', 'PM1', 'PS3', 'BS3', 'PM2', 'PM3']

		test_3b_1 = ['PS1', 'PM1', 'PM2', 'PP3', 'PP4']
		test_3b_2 = ['PS1', 'PM1', 'PM2', 'PP3', 'PP1', 'PP2']
		test_3b_3 = ['PS4', 'PM2', 'PM3', 'PP4', 'PP5']
		test_3b_4 = ['PP4', 'PM1', 'PM3', 'PP2', 'PS3']
		test_3b_5 = ['PS1', 'PM1', 'PM2', 'PP3', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5']
		
		test_3c_1 = ['PS2', 'PM1', 'PP2', 'PP3', 'PP4', 'PP1']
		test_3c_2 = ['PS1', 'PM1', 'PP2', 'PP3', 'PP1', 'PP2', 'PP5']
		test_3c_3 = ['PP2', 'PP1', 'PS2', 'PP3', 'PP4', 'PM1']
		test_3c_4 = ['PM2', 'PP1', 'PP2', 'PP3', 'PP4', 'PS1']
		test_3c_5 = ['BS3', 'PS1', 'PM1', 'BS1', 'PP2', 'PP3', 'PP1', 'PP2' ,'BS2']


		self.assertEqual(get_pathogenicity_classification(test_1a_1), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_2), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_3), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_4), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_5), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_6), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_7), 'Pathogenic (Ia)')
		self.assertEqual(get_pathogenicity_classification(test_1a_8), 'Pathogenic (Ia)')

		self.assertEqual(get_pathogenicity_classification(test_1b_1), 'Pathogenic (Ib)')
		self.assertEqual(get_pathogenicity_classification(test_1b_2), 'Pathogenic (Ib)')
		self.assertEqual(get_pathogenicity_classification(test_1b_3), 'Pathogenic (Ib)')
		self.assertEqual(get_pathogenicity_classification(test_1b_4), 'Pathogenic (Ib)')
		self.assertEqual(get_pathogenicity_classification(test_1b_5), 'Pathogenic (Ib)')
		self.assertEqual(get_pathogenicity_classification(test_1b_6), 'Pathogenic (Ib)')

		self.assertEqual(get_pathogenicity_classification(test_1c_1), 'Pathogenic (Ic)')
		self.assertEqual(get_pathogenicity_classification(test_1c_2), 'Pathogenic (Ic)')
		self.assertEqual(get_pathogenicity_classification(test_1c_3), 'Pathogenic (Ic)')
		self.assertEqual(get_pathogenicity_classification(test_1c_4), 'Pathogenic (Ic)')
		self.assertEqual(get_pathogenicity_classification(test_1c_5), 'Pathogenic (Ic)')
		
		self.assertEqual(get_pathogenicity_classification(test_1d_1), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_2), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_3), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_4), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_5), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_6), 'Pathogenic (Id)')
		self.assertEqual(get_pathogenicity_classification(test_1d_7), 'Pathogenic (Id)')

		self.assertEqual(get_pathogenicity_classification(test_2_1), 'Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(test_2_2), 'Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(test_2_3), 'Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(test_2_4), 'Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(test_2_5), 'Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(test_2_6), 'Pathogenic (II)')
		
		self.assertEqual(get_pathogenicity_classification(test_3a_1), 'Pathogenic (IIIa)')
		self.assertEqual(get_pathogenicity_classification(test_3a_2), 'Pathogenic (IIIa)')
		self.assertEqual(get_pathogenicity_classification(test_3a_3), 'Pathogenic (IIIa)')
		self.assertEqual(get_pathogenicity_classification(test_3a_4), 'Pathogenic (IIIa)')
		self.assertEqual(get_pathogenicity_classification(test_3a_5), 'Pathogenic (IIIa)')

		self.assertEqual(get_pathogenicity_classification(test_3b_1), 'Pathogenic (IIIb)')
		self.assertEqual(get_pathogenicity_classification(test_3b_2), 'Pathogenic (IIIb)')
		self.assertEqual(get_pathogenicity_classification(test_3b_3), 'Pathogenic (IIIb)')
		self.assertEqual(get_pathogenicity_classification(test_3b_4), 'Pathogenic (IIIb)')
		self.assertEqual(get_pathogenicity_classification(test_3b_5), 'Pathogenic (IIIb)')

		self.assertEqual(get_pathogenicity_classification(test_3c_1), 'Pathogenic (IIIc)')
		self.assertEqual(get_pathogenicity_classification(test_3c_2), 'Pathogenic (IIIc)')
		self.assertEqual(get_pathogenicity_classification(test_3c_3), 'Pathogenic (IIIc)')
		self.assertEqual(get_pathogenicity_classification(test_3c_4), 'Pathogenic (IIIc)')
		self.assertEqual(get_pathogenicity_classification(test_3c_5), 'Pathogenic (IIIc)')


	def test_likely_pathogenic(self):

		testlp_1_1 = ['PVS1', 'PM1']
		testlp_1_2 = ['PVS1', 'PM5']
		testlp_1_3 = ['PM1', 'PVS1']
		testlp_1_4 = ['PM1', 'BS1', 'PVS1']
		testlp_1_5 = ['BS2', 'BS3', 'PM1', 'BS1', 'PVS1', 'BS4']

		testlp_2_1 = ['PS1', 'PM1']
		testlp_2_2 = ['PS1', 'PM5', 'PM1']
		testlp_2_3 = ['PM2', 'PS3']
		testlp_2_4 = ['PM3', 'PS3', 'PM3']
		testlp_2_5 = ['BS1', 'PM3', 'BS2', 'PS3', 'PM3', 'BA1']

		testlp_3_1 = ['PS1', 'PP1', 'PP2']
		testlp_3_2 = ['PS1', 'PP5', 'PP1', 'PP4']
		testlp_3_3 = ['PS1', 'PP5', 'PP1', 'PP4', 'PP2']
		testlp_3_4 = ['PS1', 'PP5', 'PP1', 'PP4', 'PP2', 'PP3']
		testlp_3_5 = ['PS1', 'PP5', 'PP1', 'PP4', 'PP2', 'PP3', 'BS1']
		testlp_3_6 = ['PS3', 'PP4', 'PP5']

		testlp_4_1 = ['PM1', 'PM2', 'PM3']
		testlp_4_2 = ['PM1', 'PM2', 'PM3', 'PM4']
		testlp_4_3 = ['PM1', 'PM2', 'PM3', 'PM4', 'PM5']
		testlp_4_4 = ['PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'BS1', 'BS2', 'BS3']
		testlp_4_5 = ['PM1', 'PM2', 'PM3', 'BS1', 'BS2', 'BS3']
		testlp_4_6 = ['PM4', 'PM5', 'PM6']

		testlp_5_1 = ['PM1', 'PM2', 'PP1', 'PP3']
		testlp_5_2 = ['PM1', 'PM2', 'PP1', 'PP3', 'PP5']
		testlp_5_3 = ['PM1', 'PP1', 'PP3', 'PM4', 'PP5']
		testlp_5_4 = ['PM4', 'PM6', 'PP2', 'PP5']
		testlp_5_5 = ['BS2', 'PM4', 'PM6', 'PP2', 'PP5', 'PP1', 'BS1']

		testlp_6_1 = ['PM1', 'PP1', 'PP3', 'PP2', 'PP5']
		testlp_6_2 = ['PM1', 'PP1', 'PP3', 'PP5', 'PP2', 'PP4']
		testlp_6_3 = ['PM1', 'PP1', 'PP3', 'BS1', 'PP5', 'PP2', 'PP4', 'BS2']
		testlp_6_4 = ['PM5', 'PP4', 'PP5', 'PP3', 'PP2']
		testlp_6_5 = ['PP1', 'PP3', 'PP5', 'PP2', 'PP4', 'PM6']
		
		
		self.assertEqual(get_pathogenicity_classification(testlp_1_1), 'Likely Pathogenic (I)')
		self.assertEqual(get_pathogenicity_classification(testlp_1_2), 'Likely Pathogenic (I)')
		self.assertEqual(get_pathogenicity_classification(testlp_1_3), 'Likely Pathogenic (I)')
		self.assertEqual(get_pathogenicity_classification(testlp_1_4), 'Likely Pathogenic (I)')
		self.assertEqual(get_pathogenicity_classification(testlp_1_5), 'Likely Pathogenic (I)')

		self.assertEqual(get_pathogenicity_classification(testlp_2_1), 'Likely Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(testlp_2_2), 'Likely Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(testlp_2_3), 'Likely Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(testlp_2_4), 'Likely Pathogenic (II)')
		self.assertEqual(get_pathogenicity_classification(testlp_2_5), 'Likely Pathogenic (II)')

		self.assertEqual(get_pathogenicity_classification(testlp_3_1), 'Likely Pathogenic (III)')
		self.assertEqual(get_pathogenicity_classification(testlp_3_2), 'Likely Pathogenic (III)')
		self.assertEqual(get_pathogenicity_classification(testlp_3_3), 'Likely Pathogenic (III)')
		self.assertEqual(get_pathogenicity_classification(testlp_3_4), 'Likely Pathogenic (III)')
		self.assertEqual(get_pathogenicity_classification(testlp_3_5), 'Likely Pathogenic (III)')
		self.assertEqual(get_pathogenicity_classification(testlp_3_6), 'Likely Pathogenic (III)')

		self.assertEqual(get_pathogenicity_classification(testlp_4_1), 'Likely Pathogenic (IV)')
		self.assertEqual(get_pathogenicity_classification(testlp_4_2), 'Likely Pathogenic (IV)')
		self.assertEqual(get_pathogenicity_classification(testlp_4_3), 'Likely Pathogenic (IV)')
		self.assertEqual(get_pathogenicity_classification(testlp_4_4), 'Likely Pathogenic (IV)')
		self.assertEqual(get_pathogenicity_classification(testlp_4_5), 'Likely Pathogenic (IV)')
		self.assertEqual(get_pathogenicity_classification(testlp_4_6), 'Likely Pathogenic (IV)')

		self.assertEqual(get_pathogenicity_classification(testlp_5_1), 'Likely Pathogenic (V)')
		self.assertEqual(get_pathogenicity_classification(testlp_5_2), 'Likely Pathogenic (V)')
		self.assertEqual(get_pathogenicity_classification(testlp_5_3), 'Likely Pathogenic (V)')
		self.assertEqual(get_pathogenicity_classification(testlp_5_4), 'Likely Pathogenic (V)')
		self.assertEqual(get_pathogenicity_classification(testlp_5_5), 'Likely Pathogenic (V)')

		self.assertEqual(get_pathogenicity_classification(testlp_6_1), 'Likely Pathogenic (VI)')
		self.assertEqual(get_pathogenicity_classification(testlp_6_2), 'Likely Pathogenic (VI)')
		self.assertEqual(get_pathogenicity_classification(testlp_6_3), 'Likely Pathogenic (VI)')
		self.assertEqual(get_pathogenicity_classification(testlp_6_4), 'Likely Pathogenic (VI)')
		self.assertEqual(get_pathogenicity_classification(testlp_6_5), 'Likely Pathogenic (VI)')


	def test_pathogenic_VUS(self):

		test_VUS1 = ['PVS1']
		test_VUS2 = ['PVS1', 'PP1']
		test_VUS3 = ['PS1', 'PP1']
		test_VUS4 = ['PS1']
		test_VUS5 = ['PM1', 'PM2']
		test_VUS6 = ['PM1', 'PM2', 'PP5']
		test_VUS7 = ['PM4', 'PP1', 'PP2', 'PP3']
		test_VUS8 = ['PP1', 'PP2', 'PP3', 'PP4', 'PP5']

		self.assertEqual(get_pathogenicity_classification(test_VUS1), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS2), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS3), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS4), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS5), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS6), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS7), 'VUS')
		self.assertEqual(get_pathogenicity_classification(test_VUS8), 'VUS')


	def test_benign(self):

		test_benign_1_1 = ['BA1']
		test_benign_1_2 = ['BA1', 'BP1']
		test_benign_1_3 = ['BA1', 'BP1', 'BS1']
		test_benign_1_4 = ['BA1', 'BP1', 'BS1', 'PVS1']
		test_benign_1_5 = ['PP1', 'PP2', 'BA1']
		test_benign_1_5 = ['PP1', 'PP2', 'BA1']
		test_benign_2_1 =['BS1', 'BS2']
		test_benign_2_2 =['BS1', 'BS2', 'BS3']
		test_benign_2_3 =['BS1', 'BS2', 'BP1']
		test_benign_2_4 =['BP2', 'BP3', 'BS3', 'BS4', 'BP1']
		test_benign_2_5 =['BP2', 'BP3', 'BS3', 'BS4', 'BP1', 'PP1']
		test_benign_2_6 =['BS1', 'BS2', 'PVS1']
		
		self.assertEqual(get_benign_classification(test_benign_1_1), 'Benign (I)')
		self.assertEqual(get_benign_classification(test_benign_1_2), 'Benign (I)')
		self.assertEqual(get_benign_classification(test_benign_1_3), 'Benign (I)')
		self.assertEqual(get_benign_classification(test_benign_1_4), 'Benign (I)')
		self.assertEqual(get_benign_classification(test_benign_1_5), 'Benign (I)')
		self.assertEqual(get_benign_classification(test_benign_2_1), 'Benign (II)')
		self.assertEqual(get_benign_classification(test_benign_2_2), 'Benign (II)')
		self.assertEqual(get_benign_classification(test_benign_2_3), 'Benign (II)')
		self.assertEqual(get_benign_classification(test_benign_2_4), 'Benign (II)')
		self.assertEqual(get_benign_classification(test_benign_2_5), 'Benign (II)')
		self.assertEqual(get_benign_classification(test_benign_2_6), 'Benign (II)')
	

	def test_likely_benign(self):

		testlb_1_1 =['BS2', 'BP1']
		testlb_1_2 =['BS4', 'BP7']
		testlb_1_3 =['BS3', 'BP6']

		testlb_2_1 =['BP2', 'BP1']
		testlb_2_2 =['BP2', 'BP1', 'BP3']
		testlb_2_3 =['BP3', 'BP7']
		testlb_2_4 =['BP6', 'BP2', 'BP5']
		testlb_2_5 =['BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7']

		self.assertEqual(get_benign_classification(testlb_1_1), 'Likely Benign (I)')
		self.assertEqual(get_benign_classification(testlb_1_2), 'Likely Benign (I)')
		self.assertEqual(get_benign_classification(testlb_1_3), 'Likely Benign (I)')

		self.assertEqual(get_benign_classification(testlb_2_1), 'Likely Benign (II)')
		self.assertEqual(get_benign_classification(testlb_2_2), 'Likely Benign (II)')
		self.assertEqual(get_benign_classification(testlb_2_3), 'Likely Benign (II)')
		self.assertEqual(get_benign_classification(testlb_2_4), 'Likely Benign (II)')
		self.assertEqual(get_benign_classification(testlb_2_5), 'Likely Benign (II)')


	def test_benign_VUS(self):

		test_benign_VUS1 = ['BP1']
		test_benign_VUS2 = ['BP2']
		test_benign_VUS3 = ['BP3']
		test_benign_VUS4 = ['BP4']
		test_benign_VUS5 = ['BP5']
		test_benign_VUS6 = ['BP6']
		test_benign_VUS7 = ['BP7']
		test_benign_VUS8 = ['BS1']
		test_benign_VUS9 = ['BS2']
		test_benign_VUS10 = ['BS3']
		test_benign_VUS11 = ['BS4']

		self.assertEqual(get_benign_classification(test_benign_VUS1), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS2), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS3), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS4), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS5), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS6), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS7), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS8), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS9), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS10), 'VUS')
		self.assertEqual(get_benign_classification(test_benign_VUS11), 'VUS')


	def test_final(self):

		path1 = 'Pathogenic (Ia)'
		benign1 = 'VUS'

		path2 = 'Likely Pathogenic (III)'
		benign2 = 'VUS'

		path3 = 'VUS'
		benign3 = 'Benign (I)'

		path4 = 'VUS'
		benign4 = 'Likely Benign (I)'

		path5 = 'Pathogenic (Ia)'
		benign5 = 'Benign (I)'

		path6 = 'Likely Pathogenic (I)'
		benign6 = 'Benign (II)'
		
		self.assertEqual(get_final_classification(path1, benign1), 'Pathogenic (Ia)')
		self.assertEqual(get_final_classification(path2, benign2), 'Likely Pathogenic (III)')
		self.assertEqual(get_final_classification(path3, benign3), 'Benign (I)')
		self.assertEqual(get_final_classification(path4, benign4), 'Likely Benign (I)')
		self.assertEqual(get_final_classification(path5, benign5), 'VUS - contradictory evidence provided')
		self.assertEqual(get_final_classification(path6, benign6), 'VUS - contradictory evidence provided')
		self.assertEqual(get_final_classification(path3, benign1), 'VUS - criteria not met')


	def test_valid_input(self):

		input1 =['PVS1', 'PS1', 'PS2', 'BS1']
		input2 =['PVS1', 'PS1', 'PS2', 'PS3', 'PS4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5',
				'BA1', 'BS1', 'BS2', 'BS3', 'BS4', 'BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7']

		input3 =['PVS1', 'PS1', 'PS2', 'BS1', 'Cheese']
		input4 =['PVS1', 'PS1', 'PS1', 'PS2']
		input5 =[]
		input6 = 32442

		self.assertTrue(valid_input(input1)) #valid input
		self.assertTrue(valid_input(input2)) #valid input
		self.assertFalse(valid_input(input3)) #invalid classification
		self.assertFalse(valid_input(input4)) #duplicates in list
		self.assertFalse(valid_input(input5)) #empty list
		self.assertFalse(valid_input(input6)) #not a list
	
	def test_adjust_strength(self):

		input1 = [('PVS1', 'PM'), ('PM1', 'PM'), ('PS2', 'PM')]
		input3 = [('BA1', 'BS'), ('BP1', 'BP'), ('BS1', 'BP')]
		input4 = [('BP1', 'BS'), ('BS2', 'BP'), ('BP7', 'BP')]
		input6 = [('PP1', 'PS'), ('BS2', 'BP'), ('BM4', 'PP')]
		input7 = [('PP1', 'PS'), ('BS2', 'BP'), ('BM4', 'PP'), ('PVS1', 'PM'), ('PM1', 'PP'), ('PS2', 'PM')]
		
		self.assertEqual(adjust_strength(input1), ['PMS1', 'PM1', 'PM2'])
		self.assertEqual(adjust_strength(input3), ['BS1', 'BP1', 'BP1'])
		self.assertEqual(adjust_strength(input4), ['BS1', 'BP2', 'BP7'])
		self.assertEqual(adjust_strength(input6), ['PS1', 'BP2', 'PP4'])
		self.assertEqual(adjust_strength(input7), ['PS1', 'BP2', 'PP4', 'PMS1', 'PP1', 'PM2'])


	def test_classify(self):

		input1 = ['PVS1', 'PS1', 'BP1']
		input2 = ['PVS1', 'PS1', 'PS1']
		input3 = ['BA1', 'PP1']
		input4 = ['PVS1', 'BA1', 'PS1']
		input5 = ['PP1', 'BP1']
		input6 = ['BS1', 'BP1', 'PS1', 'PM1', 'PM2', 'PM3']
		input7 = ['PVS1', 'PM6', 'BS1']
		input8 = ['BS2', 'BP1', 'BS1']
		input9 = ['PVS1']
		input10 = ['PM1', 'PM2', 'PM3', 'PM4', 'PM5']
		input11= ['BS2', 'BP1']
		input12=['PS1','PP1','PS3']
		
		self.assertEqual(classify(input1), 'Pathogenic (Ia)')
		self.assertEqual(classify(input2), 'Pathogenic (Ia)')
		self.assertEqual(classify(input3), 'Benign (I)')
		self.assertEqual(classify(input4), 'VUS - contradictory evidence provided')
		self.assertEqual(classify(input5), 'VUS - criteria not met')
		self.assertEqual(classify(input6), 'VUS - contradictory evidence provided')
		self.assertEqual(classify(input7), 'Likely Pathogenic (I)')
		self.assertEqual(classify(input8), 'Benign (II)')
		self.assertEqual(classify(input9), 'VUS - criteria not met')
		self.assertEqual(classify(input10), 'Likely Pathogenic (IV)')
		self.assertEqual(classify(input11), 'Likely Benign (I)')
		self.assertEqual(classify(input12), 'Pathogenic (II)')


if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestACMGRatings)
