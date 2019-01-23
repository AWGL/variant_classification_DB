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

	def test_view_new_classification(self):

		response = self.client.get('/classification/24/')
		self.assertEqual(response.status_code,200)

	def test_view_previous_classifications(self):

		response = self.client.get('/view_previous_classifications')
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

		pass

class TestSubmitACMGData(TestCase):
	"""
	Test the ajax submission of ACMG data works

	"""

	pass


class TestFinalSubmission(TestCase):
	"""
	Test the final checkers result gets to the database correctly.

	"""
	
	pass





















