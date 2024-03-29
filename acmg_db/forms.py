from django import forms
from django.forms import ModelForm
from acmg_db.models import  *
from django.urls import reverse
from crispy_forms.bootstrap import Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML
from django.contrib.auth.models import User

# Genome Version List
GENOME_BUILD=[
	('GRCh37','GRCh37'),
	('GRCh38','GRCh38'),
	]

platform_choices = [
			('SNP Array','SNP Array'),
			('Oligo Array','Oligo Array'),
			('MLPA','MLPA'),
			('NGS','NGS'),
			]
			
# File upload forms ---------------------------------------------------
class VariantFileUploadForm(forms.Form):
	"""
	Form for inputting a tsv file of variants from the variant database, and adding them to the database
	"""
	variant_file = forms.FileField()
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
	
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
		self.helper.form_action = reverse('auto_input')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('variant_file', placeholder='Select a file to upload', title=False),
			Field('panel_applied', placeholder='Enter analysis performed', title=False),
			Field('affected_with', placeholder='Enter what the patient is affected with', title=False)
		)


class ManualUploadForm(forms.Form):
	"""
	Used for inputting individual variants into the database
	"""

	variant = forms.CharField(required=False, max_length=20000)
	sample_name = forms.CharField(max_length=50)
	worklist = forms.CharField(max_length=50)
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
	genotype = forms.ChoiceField(
		choices = (
			('Het', 'Het'),
			('Hom', 'Hom'),
			('Hemi', 'Hemi'),
			('Mosaic', 'Mosaic'),
			('NA', 'NA')
		)
	)
	genome = forms.CharField(label='Which Human Reference Genome version was used?', widget=forms.Select(choices=GENOME_BUILD))

	def __init__(self, *args, **kwargs):

		self.panel_options = kwargs.pop('options')

		super(ManualUploadForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-data-form'
		self.fields['panel_applied'].choices = self.panel_options
		self.fields['panel_applied'].help_text = 'Enter the analysis performed or panel applied. Click on Panels in the top bar to add new analyses/ panels.'
		self.fields['worklist'].label = 'Worksheet'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('manual_input')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('variant', placeholder='Enter the variant in the format 17:41197732G>A', title=False),
			Field('sample_name', placeholder='Enter the sample name, e.g. 19M12345', title=False),
			Field('worklist', placeholder='Enter the worksheet name, e.g. 19-4321', title=False),
			Field('panel_applied', title=False),
			Field('affected_with', placeholder='Enter the referral reasons for the patient', title=False),
			Field('genotype', placeholder='Enter the genotype of the variant', title=False),
			Field('genome', placeholder='Select the version of the reference genome which was used for analysis', title=False),
		)

class CNVFileUploadForm(forms.Form):
	"""
	Form for inputting a CNV file of CNVs from the Cytosure Interpret Software Aberration Report, and adding them to the database
	"""
	
	CNV_file = forms.FileField()
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
	platform = forms.CharField(widget=forms.Select(choices=platform_choices))
	worksheet = forms.CharField()
	
	def __init__(self, *args, **kwargs):
		
		self.panel_options = kwargs.pop('options')

		super(CNVFileUploadForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.fields['panel_applied'].choices = self.panel_options
		self.fields['panel_applied'].help_text = 'Click on Panels in the top bar to add new panels'
		self.helper.form_id = 'file-upload-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_home')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('CNV_file', placeholder='Select a file to upload', title=False),
			Field('worksheet', placeholder='Enter worksheet', title=False),
			Field('panel_applied', placeholder='Enter analysis performed', title=False),
			Field('affected_with', placeholder='Enter what the patient is affected with', title=False),
			Field('platform', placeholder='Select platform used', title=False)
		)
		
class CNVBluefuseUploadForm(forms.Form):
	"""
	Form for inputting a CNV file of CNVs from the Bluefuse Multi Software, and adding them to the database
	"""
	
	CNV_file = forms.FileField()
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
	platform = forms.CharField(widget=forms.Select(choices=platform_choices))
	worksheet = forms.CharField()
	
	def __init__(self, *args, **kwargs):
		
		self.panel_options = kwargs.pop('options')

		super(CNVBluefuseUploadForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.fields['panel_applied'].choices = self.panel_options
		self.fields['panel_applied'].help_text = 'Click on Panels in the top bar to add new panels'
		self.helper.form_id = 'file-upload-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_bluefuse')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('CNV_file', placeholder='Select a file to upload. Must be the CGH summary file', title=False),
			Field('worksheet', placeholder='Enter worksheet', title=False),
			Field('panel_applied', placeholder='Enter analysis performed', title=False),
			Field('affected_with', placeholder='Enter what the patient is affected with', title=False),
			Field('platform', placeholder='Select platform used', title=False)
		)
		
class CNVManualUpload(forms.Form):
	"""
	Used for inputting individual CNVs into the database
	"""

	CNV = forms.CharField(max_length=20000)
	sample_name = forms.CharField(max_length=50)
	worklist = forms.CharField(max_length=50)
	panel_applied = forms.ChoiceField()
	affected_with = forms.CharField(widget=forms.Textarea(attrs={'rows':4}))
	gain_loss = forms.ChoiceField(
		choices = (
			('Gain', 'Gain'),
			('Loss', 'Loss')
		)
	)
	genome = forms.CharField(label='Which Human Reference Genome version was used?', widget=forms.Select(choices=GENOME_BUILD))
	platform = forms.CharField(widget=forms.Select(choices=platform_choices))
	cyto = forms.CharField()
	cyto_loc = forms.CharField()

	def __init__(self, *args, **kwargs):

		self.panel_options = kwargs.pop('options')

		super(CNVManualUpload, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-data-form'
		self.fields['panel_applied'].choices = self.panel_options
		self.fields['panel_applied'].help_text = 'Enter the analysis performed or panel applied. Click on Panels in the top bar to add new analyses/ panels.'
		self.fields['CNV'].label = 'CNV'
		self.fields['worklist'].label = 'Worksheet'
		self.fields['cyto'].label = 'Cyto ID'
		self.fields['cyto_loc'].label = 'Cytogenetic Location'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_manual')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('CNV', placeholder='Enter the CNV in the format Chr:Start-Stop, e.g. 8:8494182-8753293', title=False),
			Field('cyto_loc', placeholder='Enter the cytogenetic location e.g. 8p23.1', title=False),
			Field('sample_name', placeholder='Enter the Molecular Number, e.g. 19M12345', title=False),
			Field('cyto', placeholder='Enter the Cyto ID', title=False),
			Field('worklist', placeholder='Enter the worksheet', title=False),
			Field('panel_applied', title=False),
			Field('affected_with', placeholder='Enter the referral reasons for the patient', title=False),
			Field('gain_loss', placeholder='Enter whether the CNV is a gain or loss', title=False),
			Field('genome', placeholder='Select the version of the reference genome which was used for analysis', title=False),
			Field('platform', placeholder='Select platform used', title=False)
		)

# New classification - first check forms ---------------------------------------------------------------
class SampleInfoForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check
	"""

	affected_with = forms.CharField(widget=forms.Textarea)
	other_changes = forms.CharField(widget=forms.Textarea, required=False)

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
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('first_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('affected_with'),
			Field('other_changes'),
		)

class CNVSampleInfoForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check
	"""
	
	cyto_ID = forms.CharField(widget=forms.Textarea, required=False)
	affected_with = forms.CharField(widget=forms.Textarea, required=False)
	platform = forms.CharField(widget=forms.Select(choices=platform_choices))

	def __init__(self, *args, **kwargs):

		super(CNVSampleInfoForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['cyto_ID'].widget.attrs['rows'] = 1
		self.fields['affected_with'].widget.attrs['rows'] = 2
		self.helper.form_id = 'cnvsample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('cyto_ID'),
			Field('affected_with'),
			Field('platform')
		)

class TranscriptForm(forms.Form):
	"""
	Form for changing the transcript assocaited with a variant
	"""
	select_transcript = forms.ChoiceField()

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		super(TranscriptForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['select_transcript'].choices = self.options
		self.fields['select_transcript'].initial = self.classification.selected_transcript_variant.pk
		self.helper.form_id = 'transcript-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('first_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML('<h5>Edit transcript</h5>'),
			Field('select_transcript'),
		)


class VariantInfoForm(forms.Form):
	"""
	Form for storing variant Information.

	"""
	inheritance_choices = Gene.INHERITANCE_CHOICES

	inheritance_pattern = forms.ChoiceField(choices=inheritance_choices, required=False)
	conditions = forms.CharField(widget=forms.Textarea, required=False)
	is_trio_de_novo = forms.BooleanField(required=False)
	genotype = forms.ChoiceField(
		choices = (
			('Het', 'Het'),
			('Hom', 'Hom'),
			('Hemi', 'Hemi'),
			('Mosaic', 'Mosaic'),
			('NA', 'NA')
		)
	)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		if self.classification.genotype == 1:
			genotype_init = 'Het'

		elif self.classification.genotype == 2:
			genotype_init = 'Hom'

		elif self.classification.genotype == 3:
			genotype_init = 'Hemi'

		elif self.classification.genotype == 4:
			genotype_init = 'Mosaic'

		else:
			genotype_init = 'NA'

		super(VariantInfoForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['inheritance_pattern'].widget.attrs['size'] = 9
		self.fields['conditions'].widget.attrs['rows'] = 2
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.fields['genotype'].initial = genotype_init
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('first_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML(f'<hr><div class="row"><div class="col-md-2"><h5>Add gene info</h5></div><div class="col-md-8"><h5>Gene name - {self.classification.selected_transcript_variant.transcript.gene}</h5></div></div>'),
			Field('inheritance_pattern'),
			Field('conditions'),
			HTML('<h5>Edit variant info</h5>'),
			Field('genotype'),
			HTML('Is the variant de novo?'),
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
		self.helper.form_action = reverse('first_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('genuine', id='genuine_field'),
		)

class CNVGenuineArtefactForm(forms.Form):
	"""
	Form to select whether a variant is genuine or an artefact, and whether to start a new classification or use a previous one.
	"""
	genuine_artefact_choices = CNV.GENUINE_ARTEFACT_CHOICES
	genuine = forms.ChoiceField(choices=genuine_artefact_choices)

	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(CNVGenuineArtefactForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.form_id = 'genuine-artefact-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.fields['genuine'].initial = self.cnv.genuine
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_first_check',kwargs={'pk':self.cnv_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('genuine', id='genuine_field'),
		)
		
class CNVPreviousClassificationsForm(forms.Form):
	"""
	Form to list all previous classifications as a drop down, allowing you to select which one you'd like to use for classification
	"""
	class_choices = CNV.FINAL_CLASS_CHOICES
	previous_classification = forms.ChoiceField(choices=class_choices)
	
	def __init__(self, *args, **kwargs):
	
		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)
		
		super(CNVPreviousClassificationsForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.helper.form_id = 'genuine-artefact-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_first_check',kwargs={'pk':self.cnv_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('previous_classification', id='previous_classifiction'),
		)
	


class FinaliseClassificationForm(forms.Form):
	"""
	Form for submitting the first check page.
	"""
	final_class_choices = Classification.FINAL_CLASS_CHOICES + (('9', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(FinaliseClassificationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '9'
		self.fields['final_classification'].label = 'Final classification'
		self.fields['final_classification'].help_text = 'If you would like to overwrite the ACMG classification, add the reason to the Evidence tab and select the classification from this drop-down'
		self.fields['confirm'].label = 'Confirm that the classification is complete'
		self.helper.form_id = 'finalise-classification-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('first_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Submit for second check', css_class='btn-danger'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('final_classification'),
			Field('confirm'),
		)

class CNVDetailsForm(forms.Form):
	"""
	Form for specifying CNV further details
	"""
	inheritance_options = [
				('Trio De Novo','Trio De Novo'),
				('Maternal','Maternal'),
				('Paternal','Paternal'),
				('Mosaic','Mosaic'),
				('Unknown','Unknown')
				]
	copy_options = [
			('Nullisomic','Nullisomic'),
			('Deletion','Deletion'),
			('Duplication','Duplication'),
			('Triplication','Triplication'),
			('Amplification (>Trip)', 'Amplification (>Trip)')
			]
	geno_options = [
			('Heterozygous','Heterozygous'),
			('Homozygous','Homozygous'),
			('Hemizygous','Hemizygous')
			]
	inheritance = forms.MultipleChoiceField(choices=inheritance_options, widget=forms.CheckboxSelectMultiple())
	copy_number = forms.CharField(widget=forms.Select(choices=copy_options))
	genotype = forms.CharField(widget=forms.Select(choices=geno_options))
	
	def __init__(self, *args, **kwargs):

		super(CNVDetailsForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('inheritance', placeholder='Select inheritance pattern', title=False),
			Field('copy_number', placeholder='Select CNV copy number', title=False),
			Field('genotype', placeholder='Select CNV genotype', title=False),
		)
		
class CNVMethodForm(forms.Form):
	"""
	Form for changing ACMG Guidelines to use
	"""
	method = forms.CharField(required=False, widget=forms.Select(choices=(
								('Gain','Gain'),
								('Loss','Loss')
							)))
	
	def __init__(self, *args, **kwargs):

		super(CNVMethodForm, self).__init__(*args, **kwargs)
		self.fields['method'].label = 'ACMG Classification Guidelines'
		self.helper = FormHelper()
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('method', placeholder='Select ACMG Guidelines to use', title=False),
		)

class CNVFinaliseClassificationForm(forms.Form):
	"""
	Form for submitting the first check page.
	"""
	final_class_choices = CNV.FINAL_CLASS_CHOICES + (('8', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(CNVFinaliseClassificationForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '8'
		self.fields['final_classification'].label = 'Final classification'
		self.fields['final_classification'].help_text = 'If you would like to overwrite the ACMG classification, add the reason to the Evidence tab and select the classification from this drop-down'
		self.fields['confirm'].label = 'Confirm that the classification is complete'
		self.helper.form_id = 'finalise-classification-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_first_check',kwargs={'pk':self.cnv_pk})
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
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('affected_with'),
			Field('other_changes'),
		)


class TranscriptFormSecondCheck(forms.Form):
	"""
	Form for changing the transcript assocaited with a variant
	"""
	select_transcript = forms.ChoiceField()

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		super(TranscriptFormSecondCheck, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['select_transcript'].choices = self.options
		self.fields['select_transcript'].initial = self.classification.selected_transcript_variant.pk
		self.helper.form_id = 'transcript-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML('<h5>Edit transcript</h5>'),
			Field('select_transcript'),
		)


class VariantInfoFormSecondCheck(forms.Form):
	"""
	Form for storing variant Information.

	"""
	inheritance_choices = Gene.INHERITANCE_CHOICES

	inheritance_pattern = forms.ChoiceField(choices=inheritance_choices)
	conditions = forms.CharField(widget=forms.Textarea)
	is_trio_de_novo = forms.BooleanField(required=False)
	genotype = forms.ChoiceField(
		choices = (
			('Het', 'Het'),
			('Hom', 'Hom'),
			('Hemi', 'Hemi'),
			('Mosaic', 'Mosaic'),
			('NA', 'NA')
		)
	)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)
		self.options = kwargs.pop('options')

		if self.classification.genotype == 1:
			genotype_init = 'Het'

		elif self.classification.genotype == 2:
			genotype_init = 'Hom'

		elif self.classification.genotype == 3:
			genotype_init = 'Hemi'

		elif self.classification.genotype == 4:
			genotype_init = 'Mosaic'

		else:
			genotype_init = 'NA'

		super(VariantInfoFormSecondCheck, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['inheritance_pattern'].widget.attrs['size'] = 9
		self.fields['conditions'].widget.attrs['rows'] = 2
		self.fields['is_trio_de_novo'].initial = self.classification.is_trio_de_novo
		self.fields['genotype'].initial = genotype_init
		self.helper.form_id = 'sample-information-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('second_check',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit', 'Update', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			HTML(f'<hr><div class="row"><div class="col-md-2"><h5>Add gene info</h5></div><div class="col-md-8"><h5>Gene name - {self.classification.selected_transcript_variant.transcript.gene}</h5></div></div>'),
			Field('inheritance_pattern'),
			Field('conditions'),
			HTML('<h5>Edit variant info</h5>'),
			Field('genotype'),
			HTML('Is the variant de novo?'),
			Field('is_trio_de_novo'),
		)


class FinaliseClassificationSecondCheckForm(forms.Form):
	"""
	Form for submitting the second check page.
	"""
	final_class_choices = Classification.FINAL_CLASS_CHOICES + (('9', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(FinaliseClassificationSecondCheckForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '9'
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

class FinaliseCNVClassificationSecondCheckForm(forms.Form):
	"""
	Form for submitting the second check page.
	"""
	final_class_choices = CNV.FINAL_CLASS_CHOICES + (('8', 'Use classification (don\'t override)'),)
	final_classification = forms.ChoiceField(choices=final_class_choices)
	confirm = forms.BooleanField(required=True)

	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(FinaliseCNVClassificationSecondCheckForm, self).__init__(*args, **kwargs)

		self.helper = FormHelper()
		self.fields['final_classification'].initial = '8'
		self.fields['final_classification'].label = 'Final classification'
		self.fields['final_classification'].help_text = 'If you would like to overwrite the ACMG classification, add the reason to the Evidence tab and select the classification from this drop-down'
		self.fields['confirm'].label = 'Confirm that the classification is complete'
		self.helper.form_id = 'finalise-classification-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_second_check',kwargs={'pk':self.cnv_pk})
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

class ArchiveCNVClassificationForm(forms.Form):
	"""
	Form to archive a cnv classification.
	"""
	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(ArchiveCNVClassificationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_view_classification',kwargs={'pk':self.cnv_pk})
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
		
class CNVResetClassificationForm(forms.Form):
	"""
	Form to reset a CNV classification
	"""
	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(CNVResetClassificationForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_view_classification',kwargs={'pk':self.cnv_pk})
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
		
class CNVAssignSecondCheckToMeForm(forms.Form):
	"""
	Allow users to assign a CNV second check to themselves in the History tab
	"""
	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(CNVAssignSecondCheckToMeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_view_classification',kwargs={'pk':self.cnv_pk})
		self.helper.add_input(Submit('submit-assign', 'Assign Second Check to Me', css_class='btn-danger'))


class SendBackToFirstCheckForm(forms.Form):
	"""
	Allow users to send back a classification to first check.
	"""
	def __init__(self, *args, **kwargs):

		self.classification_pk = kwargs.pop('classification_pk')
		self.classification = Classification.objects.get(pk = self.classification_pk)

		super(SendBackToFirstCheckForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('view_classification',kwargs={'pk':self.classification_pk})
		self.helper.add_input(Submit('submit-sendback', 'Send Back To First Check', css_class='btn-danger'))
		
class CNVSendBackToFirstCheckForm(forms.Form):
	"""
	Allow users to send back a CNV classification to first check.
	"""
	def __init__(self, *args, **kwargs):

		self.cnv_pk = kwargs.pop('cnv_pk')
		self.cnv = CNV.objects.get(pk = self.cnv_pk)

		super(CNVSendBackToFirstCheckForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_view_classification',kwargs={'pk':self.cnv_pk})
		self.helper.add_input(Submit('submit-sendback', 'Send Back To First Check', css_class='btn-danger'))


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


# reporting forms -----------------------------------------------------------
class ReportingSearchForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check
	"""
	sample = forms.CharField()
	worksheet = forms.CharField()
	panel_name = forms.ChoiceField()

	def __init__(self, *args, **kwargs):

		self.panel_options = kwargs.pop('options')

		super(ReportingSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'reporting-search-form'
		self.fields['panel_name'].choices = self.panel_options
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('reporting')
		self.helper.add_input(Submit('submit', 'Search', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('sample'),
			Field('worksheet'),
			Field('panel_name'),
		)
		
class ReportingCNVSearchForm(forms.Form):
	"""
	A form to collect data specific to a sample/patient for the first check - from CNV - only difference to above is reverse action
	"""
	sample = forms.CharField()
	worksheet = forms.CharField()
	panel_name = forms.ChoiceField()

	def __init__(self, *args, **kwargs):

		self.panel_options = kwargs.pop('options')

		super(ReportingCNVSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'reporting-search-form'
		self.fields['panel_name'].choices = self.panel_options
		self.fields['sample'].label = 'Molecular Number'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_reporting')
		self.helper.add_input(Submit('submit', 'Search', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('sample'),
			Field('worksheet'),
			Field('panel_name'),
		)


# search forms -----------------------------------------------------------
class SearchForm(forms.Form):
	"""
	Form for collecting user query for searching genes, variants, samples
	"""

	search_input = forms.CharField()
	build = forms.ChoiceField(choices=(('GRCh37', 'GRCh37'), ('GRCh38', 'GRCh38')))

	def __init__(self, *args, **kwargs):
		
		super(SearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('search')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('search_input', placeholder='Search for a variant, gene or sample.', title=False),
			Field('build', title=False),
		)

class CNVSearchForm(forms.Form):
	"""
	Form for collecting user query for searching CNVs, genes, samples
	"""

	search_input = forms.CharField()

	def __init__(self, *args, **kwargs):
		
		super(CNVSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('cnv_search')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('search_input', placeholder='Search for a CNV, gene or molecular number.', title=False),
		)
		
class CNVAdvancedSearchForm(forms.Form):
	"""
	Form for collecting user query for searching CNVs, genes, samples
	"""

	chromosome = forms.CharField()
	start = forms.CharField()
	stop = forms.CharField()

	def __init__(self, *args, **kwargs):
		
		super(CNVAdvancedSearchForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'search-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('chromosome', placeholder='Chromosome', title=False),
			Field('start',placeholder='Start location',title=False),
			Field('stop',placeholder='Stop location',title=False),
		)



# Download Variant List Form -----------------------------------------------------------

class DownloadVariantListForm(forms.Form):
	"""
	Form for downloading variant lists.
	"""

	CLASSIFICATION_CHOICES = (('Benign', 'Benign'),
	 ('Likely Benign', 'Likely Benign'),
	 ('Artefact', 'Artefact'),
	 ('VUS - Criteria Not Met', 'VUS - Criteria Not Met'),
	 ('Contradictory Evidence Provided','Contradictory Evidence Provided' ),
	 ('Likely Pathogenic','Likely Pathogenic' ),
	 ('Pathogenic', 'Pathogenic'), )


	black_list = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'size':'7'}), choices=CLASSIFICATION_CHOICES, required=False)
	white_list = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'size':'7'}), choices=CLASSIFICATION_CHOICES, required=False)
	build = forms.ChoiceField(choices=(('GRCh37', 'GRCh37'), ('GRCh38', 'GRCh38')))

	def __init__(self, *args, **kwargs):
		
		super(DownloadVariantListForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'download-variant-list-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('download_variant_list')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('black_list', placeholder='Variant classifications to blacklist', title=False),
			Field('white_list', placeholder='Variant classifications to whitelist.', title=False),
			Field('build', title=False),
		)
		
class DownloadCNVListForm(forms.Form):
	"""
	Form for downloading variant lists.
	"""

	CLASSIFICATION_CHOICES = (('Benign', 'Benign'),
	 ('Likely Benign', 'Likely Benign'),
	 ('Artefact', 'Artefact'),
	 ('VUS - Criteria Not Met', 'VUS - Criteria Not Met'),
	 ('Contradictory Evidence Provided','Contradictory Evidence Provided' ),
	 ('Likely Pathogenic','Likely Pathogenic' ),
	 ('Pathogenic', 'Pathogenic'), )


	black_list = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'size':'7'}), choices=CLASSIFICATION_CHOICES, required=False)
	white_list = forms.MultipleChoiceField(widget=forms.SelectMultiple(attrs={'size':'7'}), choices=CLASSIFICATION_CHOICES, required=False)


	def __init__(self, *args, **kwargs):
		
		super(DownloadCNVListForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'download-variant-list-form'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('download_cnv_list')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('black_list', placeholder='CNV classifications to blacklist', title=False),
			Field('white_list', placeholder='CNV classifications to whitelist.', title=False),
		)

class SelectAnalysisArtefacts(forms.Form):
	"""
	Form for downloading variant lists.
	"""

	analysis_id = forms.IntegerField()


	def __init__(self, *args, **kwargs):
		
		super(SelectAnalysisArtefacts, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_id = 'artefact_check'
		self.helper.label_class = 'col-lg-2'
		self.helper.field_class = 'col-lg-8'
		self.helper.form_method = 'post'
		self.helper.form_action = reverse('artefact_check_select')
		self.helper.add_input(Submit('submit', 'Submit', css_class='btn-success'))
		self.helper.form_class = 'form-horizontal'
		self.helper.layout = Layout(
			Field('analysis_id', placeholder='Which VariantBank Analysis to check', title=False),
		)
















# Create the form class.
class PhenotypeForm(ModelForm):

	def __init__(self, *args, **kwargs):
		super(PhenotypeForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.layout.append(Submit('Save', 'Save'))
		self.helper.form_method = 'post'


	class Meta:
		model = GenePhenotype
		fields = ['disease_name', 'inheritance']
