from django.test import  TestCase
from acmg_db.models import *

class TestViews(TestCase):

	fixtures = ['181121_data_for_tests.json']

	def setUp(self):

		self.client.login(username='admin', password= 'hello123')

	def test_view_home(self):

		response = self.client.get('/')

		self.assertEqual(response.status_code,200)

	def test_view_new_classification(self):

		response = self.client.get('/classification/142/')

		self.assertEqual(response.status_code,200)

	def test_view_previous_classifications(self):

		response = self.client.get('/view_previous_classifications')

		self.assertEqual(response.status_code,200)

	def test_view_view_classification(self):

		response = self.client.get('/view_classification/141/')

		self.assertEqual(response.status_code,200)
