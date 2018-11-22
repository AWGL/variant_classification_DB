from django import forms
from .models import  *
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div
from django.contrib.auth.models import User


class SecondCheckForm(forms.Form):
	"""
	Form for user to accept or reject classification of variant.

	"""

	accept = forms.ChoiceField()

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')

		super(SecondCheckForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.fields['accept'].choices = [('1', 'Accept'), ('2', 'Reject')]
		self.helper.form_id = 'accept-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check', kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(

					Field('accept'))


class SearchForm(forms.Form):
	'''
	A search form.
	See the seach view for more information.
	'''
	search = forms.CharField(required=False, max_length=255)
	gene = forms.CharField(max_length=25)
	transcript = forms.CharField(max_length=25)
	hgvs_c = forms.CharField(max_length=50)
	hgvs_p = forms.CharField(max_length=50)
	exon = forms.CharField(max_length=10)


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

					Field('search',placeholder='Enter a variant to classify', title=False),
					Field('gene', placeholder='Enter a gene name', title=False),
					Field('transcript',placeholder='Enter a transcript name', title=False),
					Field('hgvs_c',placeholder='Enter the HGVSc for the variant', title=False),
					Field('hgvs_p',placeholder='Enter the HGVSc for the variant', title=False),
					Field('exon',placeholder='Enter the exon number for the variant', title=False)

					)


class SampleInformationForm(forms.Form):
	"""
	Form for storing Sample Information.

	Note that this form originally had data from multiple models in hence the \
	unneeded complexity - could just be a model form really.

	Keep it this way in case we add automatic transcript-gene annotation back in.

	"""

	sample_lab_number = forms.CharField(max_length=25)
	analysis_performed = forms.CharField(max_length=50)
	other_changes = forms.CharField(max_length=50)
	affected_with = forms.CharField(max_length=50)
	trio_de_novo = forms.BooleanField(required=False)
	inheritance_pattern = forms.CharField(max_length=30)
	conditions = forms.CharField(widget=forms.Textarea)
	final_classification = forms.CharField(max_length=50)
	transcript_variants = forms.ChoiceField(required=False)


	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(SampleInformationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['sample_lab_number'].initial = self.classification.sample_lab_number
		self.fields['analysis_performed'].initial = self.classification.analysis_performed
		self.fields['other_changes'].initial = self.classification.other_changes
		self.fields['affected_with'].initial = self.classification.affected_with
		self.fields['trio_de_novo'].initial = self.classification.trio_de_novo
		self.fields['inheritance_pattern'].initial = self.classification.inheritance_pattern
		self.fields['conditions'].initial = self.classification.conditions
		self.fields['final_classification'].initial = self.classification.final_class
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit for 2nd Check', css_class='btn-success acmg_submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
						Field('sample_lab_number'),
						Div('analysis_performed'),
						Div('other_changes'),
						Div('affected_with'),
						Div('trio_de_novo'),
						Div('inheritance_pattern'),
						Div('conditions'),
						Div('final_classification'),
						
						 )






		









