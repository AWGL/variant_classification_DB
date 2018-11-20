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


class SampleInformationForm(forms.Form):


	sample_lab_number = forms.CharField(max_length=25)
	analysis_performed = forms.CharField(max_length=25)
	other_changes = forms.CharField(max_length=25)
	affected_with = forms.CharField(max_length=25)
	trio_de_novo = forms.BooleanField(required=False)
	inheritance_pattern = forms.CharField(max_length=30)
	conditions = forms.CharField(widget=forms.Textarea)
	final_classification = forms.CharField(max_length=25)
	transcript_variants = forms.ChoiceField(required=False)


	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.variant = Variant.objects.get(key = self.classification.variant.key)
		self.transcript_variants = TranscriptVariant.objects.filter(variant=self.variant).exclude(transcript__name = 'None')
		self.choices = [(transcript_variant.pk, transcript_variant.hgvs_c) for transcript_variant in self.transcript_variants] + [('None', 'None')]

		super(SampleInformationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()

		self.fields['transcript_variants'].choices = self.choices
		self.fields['sample_lab_number'].initial = self.classification.sample_lab_number
		self.fields['analysis_performed'].initial = self.classification.analysis_performed
		self.fields['other_changes'].initial = self.classification.other_changes
		self.fields['affected_with'].initial = self.classification.affected_with
		self.fields['trio_de_novo'].initial = self.classification.trio_de_novo
		self.fields['inheritance_pattern'].initial = self.classification.inheritance_pattern
		self.fields['conditions'].initial = self.classification.conditions
		self.fields['final_classification'].initial = self.classification.final_class

		try:
			self.fields['transcript_variants'].initial = self.classification.selected_transcript_variant.pk
		except:
			pass

		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit for 2nd Check', css_class='btn-success acmg_submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
						Div('transcript_variants'),
						Field('sample_lab_number'),
						Div('analysis_performed'),
						Div('other_changes'),
						Div('affected_with'),
						Div('trio_de_novo'),
						Div('inheritance_pattern'),
						Div('conditions'),
						Div('final_classification'),
						
						 )






		









