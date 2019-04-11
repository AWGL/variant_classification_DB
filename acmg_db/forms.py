from django import forms
from .models import  *
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML
from django.contrib.auth.models import User


# File upload forms ---------------------------------------------------
class VariantFileUploadForm(forms.Form):
	"""
	Form for inputting a tsv file of variants from the variant database, and adding them to the database
	"""
	variant_file = forms.FileField()
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(max_length=100)

	def __init__(self, *args, **kwargs):
		
		self.panel_options = kwargs.pop('options')

		super(VariantFileUploadForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.fields['panel_applied'].choices = self.panel_options
		self.fields['panel_applied'].help_text = 'Click on Panels in the top bar to add new panels'
		self.helper.form_id = 'file-upload-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('home')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('variant_file', placeholder='Select a file to upload', title=False),
			Field('panel_applied', placeholder='Enter analysis performed', title=False),
			Field('affected_with', placeholder='Enter what the patient is affected with', title=False),
		)


class ManualUploadForm(forms.Form):
	"""
	Used for inputting individual variants into the database
	"""

	variant = forms.CharField(required=False, max_length=255)
	gene = forms.CharField(max_length=25)
	transcript = forms.CharField(max_length=25)
	hgvs_c = forms.CharField(max_length=100)
	hgvs_p = forms.CharField(max_length=100)
	exon = forms.CharField(max_length=10)
	sample_name = forms.CharField(max_length=50)
	worklist = forms.CharField(max_length=50)
	affected_with = forms.CharField(max_length=100)
	analysis_performed = forms.ChoiceField()
	other_changes = forms.CharField(max_length=500)
	consequence = forms.CharField(max_length=100)


	def __init__(self, *args, **kwargs):

		self.panel_options = kwargs.pop('options')

		super(ManualUploadForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-data-form'
		self.fields['analysis_performed'].choices = self.panel_options
		self.fields['analysis_performed'].help_text = 'Click on Panels in the top bar to add new panels'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('manual_input')
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
			Field('consequence', placeholder='The consequence of the variant', title=False)
		)


# New classification - first check forms ---------------------------------------------------------------
class SampleInfoForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check
	"""

	affected_with = forms.CharField(widget=forms.Textarea)
	other_changes = forms.CharField(widget=forms.Textarea, required=False)
	analysis_performed = forms.ChoiceField(required=True)


	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.sample = self.classification.sample
		self.options = kwargs.pop('options')

		super(SampleInfoForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['affected_with'].initial = self.sample.affected_with
		self.fields['affected_with'].widget.attrs['rows'] = 2
		self.fields['other_changes'].initial = self.sample.other_changes
		self.fields['other_changes'].widget.attrs['rows'] = 2
		self.fields['analysis_performed'].choices = self.options
		self.fields['analysis_performed'].initial = self.sample.analysis_performed.pk
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('analysis_performed'),
			Field('affected_with'),
			Field('other_changes'),
		)


class VariantInfoForm(forms.Form):
	"""
	Form for storing variant Information.

	"""
	inheritance_choices = Gene.INHERITANCE_CHOICES

	select_transcript = forms.ChoiceField()
	inheritance_pattern = forms.MultipleChoiceField(choices=inheritance_choices)
	conditions = forms.CharField(widget=forms.Textarea)
	is_trio_de_novo = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		super(VariantInfoForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['select_transcript'].choices = self.options
		self.fields['select_transcript'].initial = self.classification.selected_transcript_variant.pk
		self.fields['inheritance_pattern'].initial = self.classification.selected_transcript_variant.transcript.gene.inheritance_pattern
		self.fields['inheritance_pattern'].widget.attrs['size'] = 6
		self.fields['inheritance_pattern'].help_text = 'Hold shift ctrl to select multiple.'
		self.fields['conditions'].initial = self.classification.selected_transcript_variant.transcript.gene.conditions
		self.fields['conditions'].widget.attrs['rows'] = 2
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML('<h5>Edit transcript</h5>'),
			Field('select_transcript'),
			HTML('<hr><h5>Edit gene info</h5>'),
			Field('inheritance_pattern'),
			Field('conditions'),
			HTML('<hr><h5>Is the variant de novo?</h5>'),
			Field('is_trio_de_novo'),
		)


class GenuineArtefactForm(forms.Form):
	"""
	Form to select whether a variant is genuine or an artefact, and whether to start a new classification or use a previous one.
	"""
	genuine_artefact_choices = Classification.GENUINE_ARTEFACT_CHOICES
	genuine = forms.ChoiceField(choices=genuine_artefact_choices)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(GenuineArtefactForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.form_id = 'genuine-artefact-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.fields['genuine'].initial = self.classification.genuine
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('genuine', id='genuine_field'),
		)


class FinaliseClassificationForm(forms.Form):
	"""
	Form for submitting the first check page.
	"""
	final_class_choices = Classification.FINAL_CLASS_CHOICES + (('8', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(FinaliseClassificationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '8'
		self.fields['final_classification'].label = 'Final classification'
		self.fields['final_classification'].help_text = 'If you would like to overwrite the ACMG classification, add the reason to the Evidence tab and select the classification from this drop-down'
		self.fields['confirm'].label = 'Confirm that the classification is complete'
		self.helper.form_id = 'finalise-classification-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('new_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit for second check', css_class='btn-danger'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('final_classification'),
			Field('confirm'),
		)


# Second check forms ---------------------------------------------------------------
class SampleInfoFormSecondCheck(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the second check
	Identical to first check form except from the form action
	"""

	affected_with = forms.CharField(widget=forms.Textarea)
	other_changes = forms.CharField(widget=forms.Textarea, required=False)
	analysis_performed = forms.ChoiceField(required=True)


	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.sample = self.classification.sample
		self.options = kwargs.pop('options')

		super(SampleInfoFormSecondCheck, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['affected_with'].initial = self.sample.affected_with
		self.fields['affected_with'].widget.attrs['rows'] = 2
		self.fields['other_changes'].initial = self.sample.other_changes
		self.fields['other_changes'].widget.attrs['rows'] = 2
		self.fields['analysis_performed'].choices = self.options
		self.fields['analysis_performed'].initial = self.sample.analysis_performed.pk
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('analysis_performed'),
			Field('affected_with'),
			Field('other_changes'),
		)


class VariantInfoFormSecondCheck(forms.Form):
	"""
	Form for storing variant Information.

	"""
	inheritance_choices = Gene.INHERITANCE_CHOICES

	select_transcript = forms.ChoiceField()
	inheritance_pattern = forms.MultipleChoiceField(choices=inheritance_choices)
	conditions = forms.CharField(widget=forms.Textarea)
	is_trio_de_novo = forms.BooleanField(required=False)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		super(VariantInfoFormSecondCheck, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['select_transcript'].choices = self.options
		self.fields['select_transcript'].initial = self.classification.selected_transcript_variant.pk
		self.fields['inheritance_pattern'].initial = self.classification.selected_transcript_variant.transcript.gene.inheritance_pattern
		self.fields['inheritance_pattern'].widget.attrs['size'] = 6
		self.fields['inheritance_pattern'].help_text = 'Hold shift ctrl to select multiple.'
		self.fields['conditions'].initial = self.classification.selected_transcript_variant.transcript.gene.conditions
		self.fields['conditions'].widget.attrs['rows'] = 2
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML('<h5>Edit transcript</h5>'),
			Field('select_transcript'),
			HTML('<hr><h5>Edit gene info</h5>'),
			Field('inheritance_pattern'),
			Field('conditions'),
			HTML('<hr><h5>Is the variant de novo?</h5>'),
			Field('is_trio_de_novo'),
		)


class FinaliseClassificationSecondCheckForm(forms.Form):
	"""
	Form for submitting the second check page.
	"""
	final_class_choices = Classification.FINAL_CLASS_CHOICES + (('8', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(FinaliseClassificationSecondCheckForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '8'
		self.fields['final_classification'].label = 'Final classification'
		self.fields['final_classification'].help_text = 'If you would like to overwrite the ACMG classification, add the reason to the Evidence tab and select the classification from this drop-down'
		self.fields['confirm'].label = 'Confirm that the classification is complete'
		self.helper.form_id = 'finalise-classification-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Finalise', css_class='btn-danger'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('final_classification'),
			Field('confirm'),
		)


# Archive/ reset/ reassign forms ---------------------------------------------------
class ArchiveClassificationForm(forms.Form):
	"""
	Form to archive a classification.
	"""
	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(ArchiveClassificationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('view_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit-archive', 'Archive Classification', css_class='btn-danger'))


class ResetClassificationForm(forms.Form):
	"""
	Form to reset a classification
	"""
	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(ResetClassificationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('view_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit-reset', 'Reset Classification', css_class='btn-danger'))


class AssignSecondCheckToMeForm(forms.Form):
	"""
	Allow users to assign a second check to themselves in the History tab
	"""
	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(AssignSecondCheckToMeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('view_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit-assign', 'Assign Second Check to Me', css_class='btn-danger'))


# panel forms -----------------------------------------------------------
class NewPanelForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check
	"""
	panel_name = forms.CharField()

	def __init__(self, *args, **kwargs):
		super(NewPanelForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.form_id = 'new-panel-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('panels')
		self.helper.add_input(Submit('submit', 'Add', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('panel_name'),
		)

