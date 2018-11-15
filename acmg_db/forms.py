from django import forms
from .models import  *
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.contrib.auth.models import User



class SearchForm(forms.Form):
	"""
	A search form.
	See the seach view for more information.
	"""
	search = forms.CharField(required=False, max_length=255)

	def __init__(self, *args, **kwargs):

		super(SearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-data-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'

		self.helper.form_method = 'get'
		self.helper.form_action = reverse('home')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(

					Field(
						'search',
						placeholder='Enter a variant to classify', title=False))


class NewClassificationForm(forms.Form):

	"""
	Form for doing a new classification.



	"""