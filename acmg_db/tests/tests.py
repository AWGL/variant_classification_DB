from django.test import TestCase
from acmg_db.models import *

class TestViewsSimple(TestCase):
	"""
	Simple tests to check we get right response code from a view

	"""

	fixtures = ['190123_test_data_basic.json']

	def setUp(self):

		self.client.login(username='admin', password= 'hello123')

	def test_view_home(self):

		response = self.client.get('/')
		self.assertEqual(response.status_code,200)

	def test_view_manual_input(self):

		response = self.client.get('/manual_input/')
		self.assertEqual(response.status_code,200)

	def test_view_first_check(self):

		response = self.client.get('/first_check/24/')
		self.assertEqual(response.status_code,200)

	def test_pending_classifications(self):

		response = self.client.get('/pending_classifications')
		self.assertEqual(response.status_code,200)

	def test_view_view_classification(self):

		response = self.client.get('/view_classification/24/')
		self.assertEqual(response.status_code,200)

	def test_view_second_check(self):

		response = self.client.get('/second_check/24/')
		# Not allowed to access this page as classification 24 is not ready for second check
		self.assertEqual(response.status_code,403)

	def test_view_signup(self):

		response = self.client.get('/signup/')
		self.assertEqual(response.status_code,200)

	def test_view_about(self):

		response = self.client.get('/about/')
		self.assertEqual(response.status_code,200)

	def test_view_variants(self):

		response = self.client.get('/variants/')
		self.assertEqual(response.status_code,200)


class TestViewsComplex(TestCase):

	"""
	More complex tests

	"""

	fixtures = ['190123_test_data_complex.json']

	def setUp(self):

		self.client.login(username='admin', password= 'hello123')

	def test_cannot_access_first_analysis(self):
		"""
		Test that a user can't access the first check if the variant status is second check
		"""

		response = self.client.get('/first_check/24/')
		self.assertEqual(response.status_code,403)

	def test_other_user_cannot_access_second_analysis(self):
		"""
		Test that another non assigned user (testuser) cannot access the second check
		"""
		self.client.login(username='admin', password='hello123')
		response = self.client.get('/second_check/24/')
		self.client.login(username='testuser', password='hello123!')
		response = self.client.get('/second_check/24/')
		self.assertEqual(response.status_code,403)

	def test_other_user_cannot_access_first_analysis(self):
		"""
		Test that another non assigned user (testuser) cannot access the first check
		"""

		self.client.login(username='testuser', password='hello123!')
		response = self.client.get('/first_check/24/')
		self.assertEqual(response.status_code,403)

	def test_view_specific_variant(self):
		"""
		Test the view specific variant (view_variant) page.
		"""
		response = self.client.get('/variant/15bf6934fcff979041fdb24c61acdc10b4ab3a967705334e817cb475087f5e5b/')
		self.assertEqual(response.status_code,200)


class TestSubmitACMGData(TestCase):
	"""
	Test the ajax submission of ACMG data works

	"""

	fixtures = ['190123_test_data_acmg.json']

	def setUp(self):

		self.client.login(username='admin', password= 'hello123')

	def test_pathogenic_first_check(self):
		"""
		Test a range of ajax submissions that should result in pathogenic results

		"""
		classification_obj = Classification.objects.get(pk=26)
		self.assertEqual(classification_obj.calculate_acmg_score_first(), '2')

		response = self.client.get('/first_check/26/')
		self.assertEqual(response.status_code,200)

		# Create POST data for ajax submission and check class is updated
		data = {'classifications': [('{" 131":["PVS1","PV","True",""]," 132":["PM4","PM","True",""]," 133":["PP2","PP","False",""]," 134":["BP1","BP","False",""]," 135":["BP3","BP","False",""]," 136":["PS4","PS","False",""]," 137":["PM2","PM","False",""]," 138":["BA1","BA","False",""]," 139":["BS1","BS","False",""]," 140":["BS2","BS","False",""]," 141":["PS1","PS","False",""]," 142":["PM1","PM","False",""]," 143":["PM5","PM","False",""]," 144":["PS3","PS","False",""]," 145":["BS3","BS","False",""]," 146":["PP3","PP","False",""]," 147":["BP4","BP","False",""]," 148":["BP7","BP","False",""]," 149":["PS2","PS","False",""]," 150":["PM6","PM","False",""]," 151":["PP1","PP","False",""]," 152":["PP4","PP","False",""]," 153":["BS4","BS","False",""]," 154":["PM3","PM","False",""]," 155":["BP2","BP","False",""]," 156":["BP5","BP","False",""]}')], 'classification_pk': ['26']}
		response = self.client.post('/ajax/acmg_classification_first/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

		self.assertEqual(response.status_code,200)
		self.assertEqual(classification_obj.calculate_acmg_score_first(), '5')


	def test_faithful_transmisson_first_check(self):
		"""
		Test whether the submitted data gets there correctly

		"""
		classification_obj = Classification.objects.get(pk=26)
		self.assertEqual(classification_obj.calculate_acmg_score_first(), '2')

		response = self.client.get('/first_check/26/')
		self.assertEqual(response.status_code,200)

		# Create POST data for ajax submission and check class is updated
		# Set every category to True and comment to incrementing numbers
		# Change a couple of the strengths too
		data = {'classifications': [('{" 131":["PVS1","PV","True","1"]," 132":["PM4","PP","True","2"]," 133":["PP2","PP","True","3"]," 134":["BP1","BS","True","4"]," 135":["BP3","BP","True","5"]," 136":["PS4","PS","True","6"]," 137":["PM2","PM","True","7"]," 138":["BA1","BA","True","8"]," 139":["BS1","BS","True","9"]," 140":["BS2","BS","True","10"]," 141":["PS1","PS","True","11"]," 142":["PM1","PM","True","12"]," 143":["PM5","PM","True","13"]," 144":["PS3","PS","True","14"]," 145":["BS3","BS","True","15"]," 146":["PP3","PP","True","16"]," 147":["BP4","BP","True","17"]," 148":["BP7","BP","True","18"]," 149":["PS2","PS","True","19"]," 150":["PM6","PM","True","20"]," 151":["PP1","PP","True","21"]," 152":["PP4","PP","True","22"]," 153":["BS4","BS","True","23"]," 154":["PM3","PM","True","24"]," 155":["BP2","BP","True","25"]," 156":["BP5","BP","True","26"]}')], 'classification_pk': ['26']}
		response = self.client.post('/ajax/acmg_classification_first/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

		answers = ClassificationAnswer.objects.filter(classification= classification_obj).order_by('pk')

		# Check every category is True and comment is correct
		for i, answer in enumerate(answers):

			self.assertEqual(answer.selected_first, True)
			self.assertEqual(answer.comment, str(i+1))

		# Check strengths that have been changed from default have been changed
		answer_obj = ClassificationAnswer.objects.get(pk=132)

		self.assertEqual(answer_obj.strength_first, 'PP')

		answer_obj = ClassificationAnswer.objects.get(pk=134)

		self.assertEqual(answer_obj.strength_first, 'BS')


	def test_pathogenic_second_check(self):
		"""
		Test a range of ajax submissions that should result in pathogenic results

		"""
		classification_obj = Classification.objects.get(pk=24)
		self.assertEqual(classification_obj.calculate_acmg_score_second(), '2')

		response = self.client.get('/second_check/24/')
		self.assertEqual(response.status_code,200)

		# Create POST data for ajax submission and check class is updated
		data = {'classifications': ['{" 79":["PVS1","PV","True",""]," 80":["PM4","PM","True",""]," 81":["PP2","PP","False",""]," 82":["BP1","BP","False",""]," 83":["BP3","BP","False",""]," 84":["PS4","PS","False",""]," 85":["PM2","PM","False",""]," 86":["BA1","BA","False",""]," 87":["BS1","BS","False",""]," 88":["BS2","BS","False",""]," 89":["PS1","PS","False",""]," 90":["PM1","PM","False",""]," 91":["PM5","PM","False",""]," 92":["PS3","PS","False",""]," 93":["BS3","BS","False",""]," 94":["PP3","PP","False",""]," 95":["BP4","BP","False",""]," 96":["BP7","BP","False",""]," 97":["PS2","PS","False",""]," 98":["PM6","PM","False",""]," 99":["PP1","PP","False",""]," 100":["PP4","PP","False",""]," 101":["BS4","BS","False",""]," 102":["PM3","PM","False",""]," 103":["BP2","BP","False",""]," 104":["BP5","BP","False",""]}'], 'classification_pk': ['24']}
		response = self.client.post('/ajax/acmg_classification_second/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

		self.assertEqual(response.status_code,200)
		self.assertEqual(classification_obj.calculate_acmg_score_second(), '5')


	def test_faithful_transmisson_second_check(self):
		"""
		Test whether the submitted data gets there correctly

		"""
		classification_obj = Classification.objects.get(pk=24)
		self.assertEqual(classification_obj.calculate_acmg_score_second(), '2')

		response = self.client.get('/second_check/24/')
		self.assertEqual(response.status_code,200)

		# Create POST data for ajax submission and check class is updated
		# Set every category to True and comment to incrementing numbers
		# Change a couple of the strengths too
		data = {'classifications': ['{" 79":["PVS1","PV","True","1"]," 80":["PM4","PS","True","2"]," 81":["PP2","PP","True","3"]," 82":["BP1","BS","True","4"]," 83":["BP3","BP","True","5"]," 84":["PS4","PS","True","6"]," 85":["PM2","PM","True","7"]," 86":["BA1","BA","True","8"]," 87":["BS1","BS","True","9"]," 88":["BS2","BS","True","10"]," 89":["PS1","PS","True","11"]," 90":["PM1","PM","True","12"]," 91":["PM5","PM","True","13"]," 92":["PS3","PS","True","14"]," 93":["BS3","BS","True","15"]," 94":["PP3","PP","True","16"]," 95":["BP4","BP","True","17"]," 96":["BP7","BP","True","18"]," 97":["PS2","PS","True","19"]," 98":["PM6","PM","True","20"]," 99":["PP1","PP","True","21"]," 100":["PP4","PP","True","22"]," 101":["BS4","BS","True","23"]," 102":["PM3","PM","True","24"]," 103":["BP2","BP","True","25"]," 104":["BP5","BP","True","26"]}'], 'classification_pk': ['24']}
		response = self.client.post('/ajax/acmg_classification_second/', data, **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})

		answers = ClassificationAnswer.objects.filter(classification= classification_obj).order_by('pk')

		# Check every category is True and comment is correct
		for i, answer in enumerate(answers):

			self.assertEqual(answer.selected_second, True)
			self.assertEqual(answer.comment, str(i+1))

		# Check strengths that have been changed from default have been changed
		answer_obj = ClassificationAnswer.objects.get(pk=80)

		self.assertEqual(answer_obj.strength_second, 'PS')

		answer_obj = ClassificationAnswer.objects.get(pk=82)

		self.assertEqual(answer_obj.strength_second, 'BS')

















