import unittest
from acmg_db.utils.acmg_classifier import *


class TestACMGRatings(unittest.TestCase):

	def test_pathogenic(self):

		test_path_1a_1 = [('PVS1', 'PV'), ('PS1', 'PS')]
		test_path_1a_2 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS')]
		test_path_1a_3 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS'), ('PS1', 'PS')]
		test_path_1a_4 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS'), ('PS2', 'PS'), ('PS1', 'PS')]

		test_path_1b_1 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM6', 'PM')]
		test_path_1b_2 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM6', 'PM'), ('PM3', 'PM')]
		test_path_1b_3 = [('PVS1', 'PV'), ('PM5', 'PM'), ('PM4', 'PM'), ('PM2', 'PM'), ('PM3', 'PM')]
		test_path_1b_4 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM')]
		test_path_1b_5 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM')]
		
		test_path_1c_1 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PP1', 'PP')]
		
		test_path_1d_1 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP')]
		test_path_1d_2 = [('PVS1', 'PV'), ('PP2', 'PP'), ('PP4', 'PP'), ('PP3', 'PP')]
		test_path_1d_3 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_path_1d_4 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		test_path_2_1 = [('PS1', 'PS'), ('PS2', 'PS')]
		test_path_2_2 = [('PS1', 'PS'), ('PS2', 'PS'), ('PS3', 'PS')]
		test_path_2_3 = [('PS1', 'PS'), ('PS2', 'PS'), ('PS3', 'PS'), ('PS4', 'PS')]
					
		test_path_3a_1 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM')]
		test_path_3a_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM')]
		test_path_3a_3 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM')]
		test_path_3a_4 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM')]

		test_path_3b_1 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP')]
		test_path_3b_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP')]
		test_path_3b_3 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_path_3b_4 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		test_path_3c_1 = [('PS2', 'PS'), ('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_path_3c_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		self.assertEqual(classify(test_path_1a_1), '5')
		self.assertEqual(classify(test_path_1a_2), '5')
		self.assertEqual(classify(test_path_1a_3), '5')
		self.assertEqual(classify(test_path_1a_4), '5')

		self.assertEqual(classify(test_path_1b_1), '5')
		self.assertEqual(classify(test_path_1b_2), '5')
		self.assertEqual(classify(test_path_1b_3), '5')
		self.assertEqual(classify(test_path_1b_4), '5')
		self.assertEqual(classify(test_path_1b_5), '5')

		self.assertEqual(classify(test_path_1c_1), '5')
		
		self.assertEqual(classify(test_path_1d_1), '5')
		self.assertEqual(classify(test_path_1d_2), '5')
		self.assertEqual(classify(test_path_1d_3), '5')
		self.assertEqual(classify(test_path_1d_4), '5')

		self.assertEqual(classify(test_path_2_1), '5')
		self.assertEqual(classify(test_path_2_2), '5')
		self.assertEqual(classify(test_path_2_3), '5')
		
		self.assertEqual(classify(test_path_3a_1), '5')
		self.assertEqual(classify(test_path_3a_2), '5')
		self.assertEqual(classify(test_path_3a_3), '5')
		self.assertEqual(classify(test_path_3a_4), '5')

		self.assertEqual(classify(test_path_3b_1), '5')
		self.assertEqual(classify(test_path_3b_2), '5')
		self.assertEqual(classify(test_path_3b_3), '5')
		self.assertEqual(classify(test_path_3b_4), '5')

		self.assertEqual(classify(test_path_3c_1), '5')
		self.assertEqual(classify(test_path_3c_2), '5')


	def test_likely_pathogenic(self):

		test_lp_1_1 = [('PVS1', 'PV'), ('PM1', 'PM')]

		test_lp_2_1 = [('PS1', 'PS'), ('PM1', 'PM')]
		test_lp_2_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM5', 'PM')]

		test_lp_3_1 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP')]
		test_lp_3_2 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP')]
		test_lp_3_3 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_lp_3_4 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		test_lp_4_1 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM')]
		test_lp_4_2 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM')]
		test_lp_4_3 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM')]
		test_lp_4_4 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM')]

		test_lp_5_1 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP')]
		test_lp_5_2 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_lp_5_3 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		test_lp_6_1 = [('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP')]
		test_lp_6_2 = [('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]
		
		self.assertEqual(classify(test_lp_1_1), '4')

		self.assertEqual(classify(test_lp_2_1), '4')
		self.assertEqual(classify(test_lp_2_2), '4')

		self.assertEqual(classify(test_lp_3_1), '4')
		self.assertEqual(classify(test_lp_3_2), '4')
		self.assertEqual(classify(test_lp_3_3), '4')
		self.assertEqual(classify(test_lp_3_4), '4')

		self.assertEqual(classify(test_lp_4_1), '4')
		self.assertEqual(classify(test_lp_4_2), '4')
		self.assertEqual(classify(test_lp_4_3), '4')
		self.assertEqual(classify(test_lp_4_4), '4')

		self.assertEqual(classify(test_lp_5_1), '4')
		self.assertEqual(classify(test_lp_5_2), '4')
		self.assertEqual(classify(test_lp_5_3), '4')

		self.assertEqual(classify(test_lp_6_1), '4')
		self.assertEqual(classify(test_lp_6_2), '4')


	def test_benign(self):

		test_benign_1_1 = [('BA1', 'BA')]
		test_benign_1_2 = [('BA1', 'BA'), ('BS1', 'BS')]
		test_benign_1_3 = [('BA1', 'BA'), ('BP1', 'BP')]
		test_benign_1_4 = [('BA1', 'BA'), ('BS1', 'BS'), ('BP1', 'BP')]
		test_benign_1_5 = [('BS1', 'BA')]
		test_benign_2_1 = [('BS1', 'BS'), ('BS2', 'BS')]
		test_benign_2_2 = [('BS1', 'BS'), ('BS2', 'BS'), ('BS3', 'BS')]
		test_benign_2_3 = [('BS1', 'BS'), ('BS2', 'BS'), ('BS3', 'BS'), ('BS4', 'BS')]
		test_benign_2_4 = [('BS1', 'BS'), ('BS2', 'BS'), ('BP1', 'BP')]
		test_benign_2_5 = [('BS3', 'BS'), ('BS4', 'BS'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP1', 'BP')]
		
		self.assertEqual(classify(test_benign_1_1), '0')
		self.assertEqual(classify(test_benign_1_2), '0')
		self.assertEqual(classify(test_benign_1_3), '0')
		self.assertEqual(classify(test_benign_1_4), '0')
		self.assertEqual(classify(test_benign_1_5), '0')
		self.assertEqual(classify(test_benign_2_1), '0')
		self.assertEqual(classify(test_benign_2_2), '0')
		self.assertEqual(classify(test_benign_2_3), '0')
		self.assertEqual(classify(test_benign_2_4), '0')
		self.assertEqual(classify(test_benign_2_5), '0')


	def test_likely_benign(self):

		test_lb_1_1 = [('BS1', 'BS'), ('BP1', 'BP')]
		test_lb_1_2 = [('BS1', 'BS'), ('BP1', 'BP'), ('BP2', 'BP')]
		test_lb_1_3 = [('BS2', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP')]
		test_lb_1_4 = [('BS3', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP5', 'BP'), ('BP6', 'BP')]
		test_lb_1_5 = [('BS4', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP')]
		test_lb_1_6 = [('BS1', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP')]
		test_lb_1_7 = [('BS2', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP')]

		test_lb_2_1 = [('BP1', 'BP'), ('BP2', 'BP')]
		test_lb_2_2 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP')]
		test_lb_2_3 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP5', 'BP'), ('BP6', 'BP')]
		test_lb_2_4 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP')]
		test_lb_2_5 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP')]
		test_lb_2_6 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP')]

		self.assertEqual(classify(test_lb_1_1), '1')
		self.assertEqual(classify(test_lb_1_2), '1')
		self.assertEqual(classify(test_lb_1_3), '1')
		self.assertEqual(classify(test_lb_1_4), '1')
		self.assertEqual(classify(test_lb_1_5), '1')
		self.assertEqual(classify(test_lb_1_6), '1')
		self.assertEqual(classify(test_lb_1_7), '1')

		self.assertEqual(classify(test_lb_2_1), '1')
		self.assertEqual(classify(test_lb_2_2), '1')
		self.assertEqual(classify(test_lb_2_3), '1')
		self.assertEqual(classify(test_lb_2_4), '1')
		self.assertEqual(classify(test_lb_2_5), '1')
		self.assertEqual(classify(test_lb_2_6), '1')


	def test_insufficient_evidence_VUS(self):

		test_path_VUS1 = [('PVS1', 'PV')]
		test_path_VUS2 = [('PVS1', 'PV'), ('PP1', 'PP')]
		test_path_VUS3 = [('PS1', 'PS')]
		test_path_VUS4 = [('PS1', 'PS'), ('PP1', 'PP')]
		test_path_VUS5 = [('PM1', 'PM'), ('PM2', 'PM')]
		test_path_VUS6 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP5', 'PP')]
		test_path_VUS7 = [('PM4', 'PP'), ('PP1', 'PP')]
		test_path_VUS8 = [('PM4', 'PP'), ('PP1', 'PP'), ('PP2', 'PP')]
		test_path_VUS9 = [('PM4', 'PP'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP')]
		test_path_VUS10 = [('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP')]

		test_benign_VUS1 = [('BP1', 'BP')]
		test_benign_VUS2 = [('BP2', 'BP')]
		test_benign_VUS3 = [('BP3', 'BP')]
		test_benign_VUS4 = [('BP4', 'BP')]
		test_benign_VUS5 = [('BP5', 'BP')]
		test_benign_VUS6 = [('BP6', 'BP')]
		test_benign_VUS7 = [('BP7', 'BP')]
		test_benign_VUS8 = [('BS1', 'BS')]
		test_benign_VUS9 = [('BS2', 'BS')]
		test_benign_VUS10 = [('BS3', 'BS')]
		test_benign_VUS11 = [('BS4', 'BS')]

		self.assertEqual(classify(test_path_VUS1), '2')
		self.assertEqual(classify(test_path_VUS2), '2')
		self.assertEqual(classify(test_path_VUS3), '2')
		self.assertEqual(classify(test_path_VUS4), '2')
		self.assertEqual(classify(test_path_VUS5), '2')
		self.assertEqual(classify(test_path_VUS6), '2')
		self.assertEqual(classify(test_path_VUS7), '2')
		self.assertEqual(classify(test_path_VUS8), '2')
		self.assertEqual(classify(test_path_VUS9), '2')
		self.assertEqual(classify(test_path_VUS10), '2')

		self.assertEqual(classify(test_benign_VUS1), '2')
		self.assertEqual(classify(test_benign_VUS2), '2')
		self.assertEqual(classify(test_benign_VUS3), '2')
		self.assertEqual(classify(test_benign_VUS4), '2')
		self.assertEqual(classify(test_benign_VUS5), '2')
		self.assertEqual(classify(test_benign_VUS6), '2')
		self.assertEqual(classify(test_benign_VUS7), '2')
		self.assertEqual(classify(test_benign_VUS8), '2')
		self.assertEqual(classify(test_benign_VUS9), '2')
		self.assertEqual(classify(test_benign_VUS10), '2')
		self.assertEqual(classify(test_benign_VUS11), '2')
	

	def test_conflicting_evidence_VUS(self):

		test_conflicting_path_1a_1 = [('PVS1', 'PV'), ('PS1', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_1a_2 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_1a_3 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS'), ('PS1', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_1a_4 = [('PVS1', 'PV'), ('PS3', 'PS'), ('PS4', 'PS'), ('PS2', 'PS'), ('PS1', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_1b_1 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM6', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_1b_2 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM6', 'PM'), ('PM3', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_1b_3 = [('PVS1', 'PV'), ('PM5', 'PM'), ('PM4', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_1b_4 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_1b_5 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_1c_1 = [('PVS1', 'PV'), ('PM1', 'PM'), ('PP1', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_1d_1 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_1d_2 = [('PVS1', 'PV'), ('PP2', 'PP'), ('PP4', 'PP'), ('PP3', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_1d_3 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_1d_4 = [('PVS1', 'PV'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_2_1 = [('PS1', 'PS'), ('PS2', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_2_2 = [('PS1', 'PS'), ('PS2', 'PS'), ('PS3', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_2_3 = [('PS1', 'PS'), ('PS2', 'PS'), ('PS3', 'PS'), ('PS4', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_3a_1 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_3a_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_3a_3 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_3a_4 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_3b_1 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_3b_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_3b_3 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_3b_4 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_3c_1 = [('PS2', 'PS'), ('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_3c_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]

		test_conflicting_lp_1_1 = [('PVS1', 'PV'), ('PM1', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_2_1 = [('PS1', 'PS'), ('PM1', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_2_2 = [('PS1', 'PS'), ('PM1', 'PM'), ('PM5', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_3_1 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_3_2 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_3_3 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_3_4 = [('PS1', 'PS'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_4_1 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_4_2 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_4_3 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_4_4 = [('PM1', 'PM'), ('PM2', 'PM'), ('PM3', 'PM'), ('PM4', 'PM'), ('PM5', 'PM'), ('PM6', 'PM'), ('BP1', 'BP')]
		test_conflicting_lp_5_1 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_5_2 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_5_3 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP1', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_6_1 = [('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('BP1', 'BP')]
		test_conflicting_lp_6_2 = [('PM1', 'PM'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]

		test_conflicting_path_VUS1 = [('PVS1', 'PV'), ('BP1', 'BP')]
		test_conflicting_path_VUS2 = [('PVS1', 'PV'), ('PP1', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS3 = [('PS1', 'PS'), ('BP1', 'BP')]
		test_conflicting_path_VUS4 = [('PS1', 'PS'), ('PP1', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS5 = [('PM1', 'PM'), ('PM2', 'PM'), ('BP1', 'BP')]
		test_conflicting_path_VUS6 = [('PM1', 'PM'), ('PM2', 'PM'), ('PP5', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS7 = [('PM4', 'PP'), ('PP1', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS8 = [('PM4', 'PP'), ('PP1', 'PP'), ('PP2', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS9 = [('PM4', 'PP'), ('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('BP1', 'BP')]
		test_conflicting_path_VUS10 = [('PP1', 'PP'), ('PP2', 'PP'), ('PP3', 'PP'), ('PP4', 'PP'), ('PP5', 'PP'), ('BP1', 'BP')]

		test_conflicting_benign_VUS1 = [('BP1', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS2 = [('BP2', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS3 = [('BP3', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS4 = [('BP4', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS5 = [('BP5', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS6 = [('BP6', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS7 = [('BP7', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_VUS8 = [('BS1', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_VUS9 = [('BS2', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_VUS10 = [('BS3', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_VUS11 = [('BS4', 'BS'), ('PP1', 'PP')]

		test_conflicting_lb_1_1 = [('BS1', 'BS'), ('BP1', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_2 = [('BS1', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_3 = [('BS2', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_4 = [('BS3', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_5 = [('BS4', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_6 = [('BS1', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_1_7 = [('BS2', 'BS'), ('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_1 = [('BP1', 'BP'), ('BP2', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_2 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_3 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_4 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_5 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP'), ('PP1', 'PP')]
		test_conflicting_lb_2_6 = [('BP1', 'BP'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP4', 'BP'), ('BP5', 'BP'), ('BP6', 'BP'), ('BP7', 'BP'), ('PP1', 'PP')]

		test_conflicting_benign_1_1 = [('BA1', 'BA'), ('PP1', 'PP')]
		test_conflicting_benign_1_2 = [('BA1', 'BA'), ('BS1', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_1_3 = [('BA1', 'BA'), ('BP1', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_1_4 = [('BA1', 'BA'), ('BS1', 'BS'), ('BP1', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_1_5 = [('BS1', 'BA'), ('PP1', 'PP')]
		test_conflicting_benign_2_1 = [('BS1', 'BS'), ('BS2', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_2_2 = [('BS1', 'BS'), ('BS2', 'BS'), ('BS3', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_2_3 = [('BS1', 'BS'), ('BS2', 'BS'), ('BS3', 'BS'), ('BS4', 'BS'), ('PP1', 'PP')]
		test_conflicting_benign_2_4 = [('BS1', 'BS'), ('BS2', 'BS'), ('BP1', 'BP'), ('PP1', 'PP')]
		test_conflicting_benign_2_5 = [('BS3', 'BS'), ('BS4', 'BS'), ('BP2', 'BP'), ('BP3', 'BP'), ('BP1', 'BP'), ('PP1', 'PP')]

		self.assertEqual(classify(test_conflicting_path_1a_1), '3')
		self.assertEqual(classify(test_conflicting_path_1a_2), '3')
		self.assertEqual(classify(test_conflicting_path_1a_3), '3')
		self.assertEqual(classify(test_conflicting_path_1a_4), '3')
		self.assertEqual(classify(test_conflicting_path_1b_1), '3')
		self.assertEqual(classify(test_conflicting_path_1b_2), '3')
		self.assertEqual(classify(test_conflicting_path_1b_3), '3')
		self.assertEqual(classify(test_conflicting_path_1b_4), '3')
		self.assertEqual(classify(test_conflicting_path_1b_5), '3')
		self.assertEqual(classify(test_conflicting_path_1c_1), '3')
		self.assertEqual(classify(test_conflicting_path_1d_1), '3')
		self.assertEqual(classify(test_conflicting_path_1d_2), '3')
		self.assertEqual(classify(test_conflicting_path_1d_3), '3')
		self.assertEqual(classify(test_conflicting_path_1d_4), '3')
		self.assertEqual(classify(test_conflicting_path_2_1), '3')
		self.assertEqual(classify(test_conflicting_path_2_2), '3')
		self.assertEqual(classify(test_conflicting_path_2_3), '3')
		self.assertEqual(classify(test_conflicting_path_3a_1), '3')
		self.assertEqual(classify(test_conflicting_path_3a_2), '3')
		self.assertEqual(classify(test_conflicting_path_3a_3), '3')
		self.assertEqual(classify(test_conflicting_path_3a_4), '3')
		self.assertEqual(classify(test_conflicting_path_3b_1), '3')
		self.assertEqual(classify(test_conflicting_path_3b_2), '3')
		self.assertEqual(classify(test_conflicting_path_3b_3), '3')
		self.assertEqual(classify(test_conflicting_path_3b_4), '3')
		self.assertEqual(classify(test_conflicting_path_3c_1), '3')
		self.assertEqual(classify(test_conflicting_path_3c_2), '3')

		self.assertEqual(classify(test_conflicting_lp_1_1), '3')
		self.assertEqual(classify(test_conflicting_lp_2_1), '3')
		self.assertEqual(classify(test_conflicting_lp_2_2), '3')
		self.assertEqual(classify(test_conflicting_lp_3_1), '3')
		self.assertEqual(classify(test_conflicting_lp_3_2), '3')
		self.assertEqual(classify(test_conflicting_lp_3_3), '3')
		self.assertEqual(classify(test_conflicting_lp_3_4), '3')
		self.assertEqual(classify(test_conflicting_lp_4_1), '3')
		self.assertEqual(classify(test_conflicting_lp_4_2), '3')
		self.assertEqual(classify(test_conflicting_lp_4_3), '3')
		self.assertEqual(classify(test_conflicting_lp_4_4), '3')
		self.assertEqual(classify(test_conflicting_lp_5_1), '3')
		self.assertEqual(classify(test_conflicting_lp_5_2), '3')
		self.assertEqual(classify(test_conflicting_lp_5_3), '3')
		self.assertEqual(classify(test_conflicting_lp_6_1), '3')
		self.assertEqual(classify(test_conflicting_lp_6_2), '3')

		self.assertEqual(classify(test_conflicting_path_VUS1), '3')
		self.assertEqual(classify(test_conflicting_path_VUS2), '3')
		self.assertEqual(classify(test_conflicting_path_VUS3), '3')
		self.assertEqual(classify(test_conflicting_path_VUS4), '3')
		self.assertEqual(classify(test_conflicting_path_VUS5), '3')
		self.assertEqual(classify(test_conflicting_path_VUS6), '3')
		self.assertEqual(classify(test_conflicting_path_VUS7), '3')
		self.assertEqual(classify(test_conflicting_path_VUS8), '3')
		self.assertEqual(classify(test_conflicting_path_VUS9), '3')
		self.assertEqual(classify(test_conflicting_path_VUS10), '3')

		self.assertEqual(classify(test_conflicting_benign_VUS1), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS2), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS3), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS4), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS5), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS6), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS7), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS8), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS9), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS10), '3')
		self.assertEqual(classify(test_conflicting_benign_VUS11), '3')

		self.assertEqual(classify(test_conflicting_lb_1_1), '3')
		self.assertEqual(classify(test_conflicting_lb_1_2), '3')
		self.assertEqual(classify(test_conflicting_lb_1_3), '3')
		self.assertEqual(classify(test_conflicting_lb_1_4), '3')
		self.assertEqual(classify(test_conflicting_lb_1_5), '3')
		self.assertEqual(classify(test_conflicting_lb_1_6), '3')
		self.assertEqual(classify(test_conflicting_lb_1_7), '3')
		self.assertEqual(classify(test_conflicting_lb_2_1), '3')
		self.assertEqual(classify(test_conflicting_lb_2_2), '3')
		self.assertEqual(classify(test_conflicting_lb_2_3), '3')
		self.assertEqual(classify(test_conflicting_lb_2_4), '3')
		self.assertEqual(classify(test_conflicting_lb_2_5), '3')
		self.assertEqual(classify(test_conflicting_lb_2_6), '3')

		self.assertEqual(classify(test_conflicting_benign_1_1), '3')
		self.assertEqual(classify(test_conflicting_benign_1_2), '3')
		self.assertEqual(classify(test_conflicting_benign_1_3), '3')
		self.assertEqual(classify(test_conflicting_benign_1_4), '3')
		self.assertEqual(classify(test_conflicting_benign_1_5), '3')
		self.assertEqual(classify(test_conflicting_benign_2_1), '3')
		self.assertEqual(classify(test_conflicting_benign_2_2), '3')
		self.assertEqual(classify(test_conflicting_benign_2_3), '3')
		self.assertEqual(classify(test_conflicting_benign_2_4), '3')
		self.assertEqual(classify(test_conflicting_benign_2_5), '3')


	def test_valid_input(self):

		input1 = ['PVS1', 'PS1', 'PS2', 'BS1']
		input2 = ['PVS1', 'PS1', 'PS2', 'PS3', 'PS4', 'PM1', 'PM2', 'PM3', 'PM4', 'PM5', 'PM6', 'PP1', 'PP2', 'PP3', 'PP4', 'PP5',
				  'BA1', 'BS1', 'BS2', 'BS3', 'BS4', 'BP1', 'BP2', 'BP3', 'BP4', 'BP5', 'BP6', 'BP7']
		input3 = ['PVS1', 'PS1', 'PS2', 'BS1', 'Cheese']
		input4 = ['PVS1', 'PS1', 'PS1', 'PS2']
		input5 = []
		input6 = 32442

		self.assertTrue(valid_input(input1)) #valid input
		self.assertTrue(valid_input(input2)) #valid input
		self.assertFalse(valid_input(input3)) #invalid classification
		self.assertFalse(valid_input(input4)) #duplicates in list
		self.assertFalse(valid_input(input5)) #empty list
		self.assertFalse(valid_input(input6)) #not a list


if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestACMGRatings)
