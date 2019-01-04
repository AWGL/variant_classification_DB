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
	'''
	variant = forms.CharField(required=False, max_length=255)
	gene = forms.CharField(max_length=100)
	transcript = forms.CharField(max_length=100)
	hgvs_c = forms.CharField(max_length=100)
	hgvs_p = forms.CharField(max_length=100)
	exon = forms.CharField(max_length=10)
	sample_name = forms.CharField(max_length=500)
	worklist = forms.CharField(max_length=100)
	affected_with = forms.CharField(max_length=500)
	analysis_performed = forms.CharField(max_length=500)
	other_changes = forms.CharField(max_length=500)


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

					Field('variant', placeholder='Enter a variant to classify', title=False),
					Field('gene', placeholder='Enter a gene name', title=False),
					Field('transcript', placeholder='Enter a transcript name', title=False),
					Field('hgvs_c', placeholder='Enter the HGVSc for the variant', title=False),
					Field('hgvs_p', placeholder='Enter the HGVSp for the variant', title=False),
					Field('exon', placeholder='Enter the exon number for the variant', title=False),
					Field('sample_name', placeholder='Enter the sample name', title=False),
					Field('worklist', placeholder='Enter the worklist name', title=False),
					Field('affected_with', placeholder='Enter What the sample is affected with', title=False),
					Field('analysis_performed', placeholder='Enter the analysis performed', title=False),
					Field('other_changes', placeholder='Enter any other changes', title=False),

					)


class ClassificationInformationForm(forms.Form):
	"""
	Form for storing Sample Information.

	Note that this form originally had data from multiple models in hence the \
	unneeded complexity - could just be a model form really.

	Keep it this way in case we add automatic transcript-gene annotation back in.

	"""
	FINAL_CLASS_CHOICES =(('0', 'Benign'), ('1', 'Likely Benign'), ('2', 'VUS - Criteria Not Met'),
		('3', 'VUS - Contradictory Evidence Provided'), ('4', 'Likely Pathogenic'), ('5', 'Pathogenic'),
		('6', 'Artefact'), ('7', 'NA'))

	
	inheritance_pattern = forms.CharField(max_length=30)
	conditions = forms.CharField(widget=forms.Textarea)
	is_trio_de_novo = forms.BooleanField(required=False)
	final_classification = forms.ChoiceField(choices=FINAL_CLASS_CHOICES)


	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(ClassificationInformationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.fields['inheritance_pattern'].initial = self.classification.inheritance_pattern
		self.fields['conditions'].initial = self.classification.conditions
		self.fields['final_classification'].initial = self.classification.final_class
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success acmg_submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
						
						Div('inheritance_pattern'),
						Div('conditions'),
						Div('is_trio_de_novo'),
						Div('final_classification'),
						
						 )



class ClassificationInformationSecondCheckForm(forms.Form):
	"""
	Form for storing Sample Information.

	Note that this form originally had data from multiple models in hence the \
	unneeded complexity - could just be a model form really.

	Keep it this way in case we add automatic transcript-gene annotation back in.

	"""
	FINAL_CLASS_CHOICES =(('0', 'Benign'), ('1', 'Likely Benign'), ('2', 'VUS - Criteria Not Met'),
		('3', 'VUS - Contradictory Evidence Provided'), ('4', 'Likely Pathogenic'), ('5', 'Pathogenic'),
		('6', 'Artefact'), ('7', 'NA'))

	
	inheritance_pattern = forms.CharField(max_length=30)
	conditions = forms.CharField(widget=forms.Textarea)
	is_trio_de_novo = forms.BooleanField(required=False)
	final_classification = forms.ChoiceField(choices=FINAL_CLASS_CHOICES)



	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(ClassificationInformationSecondCheckForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.fields['inheritance_pattern'].initial = self.classification.inheritance_pattern
		self.fields['conditions'].initial = self.classification.conditions
		self.fields['final_classification'].initial = self.classification.final_class
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success acmg_submit'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
						
						Div('inheritance_pattern'),
						Div('conditions'),
						Div('is_trio_de_novo'),
						Div('final_classification'),
						
						 )


		









