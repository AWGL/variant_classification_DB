from django.db import models
from auditlog.registry import auditlog
from auditlog.models import LogEntry
from auditlog.models import AuditlogHistoryField

from acmg_db.utils import acmg_classifier

import numpy as np

class Worklist(models.Model):
	"""
	Model to store which worklist the sample was on.
	For example 18-1234.

	"""
	name = models.CharField(max_length=50, primary_key=True)

	def __str__(self):
		return self.name


class Panel(models.Model):
	"""
	Which panel is applied to the sample.

	This corresponds to the analysis_performed field in the Sample model.
	"""

	panel = models.CharField(max_length=100, primary_key=True)
	added_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

	def __str__(self):
		return self.panel.capitalize()


class Sample(models.Model):
	"""
	Model to hold information specific to a sample.

	"""

	history = AuditlogHistoryField()

	name = models.CharField(max_length=255, unique=True) # worksheet_id + '-' + sample_id + '-' + analysis performed
	sample_name_only = models.CharField(max_length=150)  # sample_id only
	worklist = models.ForeignKey(Worklist, on_delete=models.CASCADE)
	affected_with = models.TextField()
	analysis_performed = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE)
	analysis_complete = models.BooleanField()
	other_changes = models.TextField()
	genome = models.TextField(default='GRCh37')

	def __str__(self):
		return self.name

class Variant(models.Model):
	"""
	Model to hold unique variants within the database.

	"""

	variant_hash = models.CharField(max_length=64, primary_key=True)
	chromosome  = models.CharField(max_length=25)
	position  = models.IntegerField()
	ref = models.TextField()
	alt = models.TextField()
	genome = models.TextField(default='GRCh37')

	def __str__(self):
		return f'{self.chromosome}:{self.position}{self.ref}>{self.alt}'


	def most_recent_classification(self):
		"""
		Return the most recent classification that is either complete or archived

		"""

		classifications = Classification.objects.filter(variant=self, status__in=['2', '3']).order_by('-second_check_date')

		if len(classifications) > 0:

			most_recent = classifications[0]

			all_classes = [classification.display_classification() for classification in classifications]

			all_classes = list(set(all_classes))

			all_classes = '|'.join(all_classes)

			count = len(classifications)

			return most_recent, all_classes, count

		return None, None, 0


class Gene(models.Model):
	"""
	Model to hold information specific to a gene.

	Also stores additional data regarding the inheritance pattern for that gene and any conditions associated with a gene.

	"""
	INHERITANCE_CHOICES = (
		('Unknown', 'Unknown'), 
		('Autosomal dominant', 'Autosomal dominant'), 
		('Autosomal recessive', 'Autosomal recessive'),
		('Digenic dominant', 'Digenic dominant'),
		('Digenic recessive', 'Digenic recessive'),
		('X linked dominant', 'X linked dominant'),
		('X linked recessive', 'X linked recessive'),
		('Imprinting centre', 'Imprinting centre'),
		('Somatic mutation', 'Somatic mutation'),
	)

	name = models.CharField(max_length=25, primary_key=True)
	inheritance_pattern = models.CharField(max_length=255, null=True, blank=True)
	conditions = models.TextField(null=True, blank=True)

	def __str__(self):
		return self.name

	def get_all_phenotypes(self):
		"""
		Get all phenotypes for a gene
		"""

		related_phenotypes = GenePhenotype.objects.filter(gene=self)

		phenotype_list = []

		for phenotype in related_phenotypes:

			phenotype_list.append(phenotype.disease_name)

		return phenotype_list

	def get_all_inheritance(self):
		"""
		Get all inheritance patterns for a gene
		"""

		related_phenotypes = GenePhenotype.objects.filter(gene=self)

		phenotype_list = []

		for phenotype in related_phenotypes:

			if phenotype.inheritance != '':

				# split up mixed ones
				if ',' in phenotype.inheritance:

					phenotype_inherit = phenotype.inheritance.split(',')

					for split_inheritance in phenotype_inherit:

					 	phenotype_list.append(split_inheritance.strip())

				else:

					phenotype_list.append(phenotype.inheritance.strip())


		return list(set(phenotype_list))


class GenePhenotype(models.Model):
	"""
	Model links gene with a phenotype
	"""

	gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
	disease_name = models.TextField()
	inheritance = models.TextField()
	manual = models.BooleanField()

class Transcript(models.Model):
	"""
	Model to hold a transcript e.g NM_007298.3
	Each transcript appears in a gene.

	"""

	name = models.CharField(max_length=40, primary_key=True)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=True,blank=True)

	def __str__(self):
		return f'{self.name} ({self.gene})'


class TranscriptVariant(models.Model):
	"""
	Model to link a variant with a transcript.

	A variant can potentially fall within many transcripts.

	Holds data on HGVS as well as exon data and consequence.

	"""

	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
	transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=True, blank=True)
	hgvs_c = models.TextField(null=True, blank=True)
	hgvs_p = models.TextField(null=True, blank=True)
	exon = models.CharField(max_length=10,null=True, blank=True)
	consequence = models.CharField(max_length=100, null=True, blank=True)
	vep_version = models.CharField(max_length=20)

	def __str__(self):
		return f'{self.transcript}'


	def display_hgvsc(self):
		"""
		Function to display the HGVSc

		"""
		if self.hgvs_c == None:
			return None

		else:
			try:
				return self.hgvs_c.split(':')[1]

			except:
				return self.hgvs_c 

	def display_hgvsp(self):
		"""
		Function to display the HGVSp

		"""
		if self.hgvs_p == None:
			return None

		else:
			try:
				return self.hgvs_p.split(':')[1]

			except:
				return self.hgvs_p


class Classification(models.Model):

	"""
	Class to hold results of ACMG classification.

	The overall model for storing classifications is as follows;

	1) Classification class holds a unique classification. A variant can be classified many times.
	2) Each classification is initiated and the ACMG answers (ClassificationAnswer) are created from ClassificationQuestions
	3) The ClassificationAnswer class stores what the user selected for each question.

	"""

	# Some choices for the CharFields
	PATH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'), ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	BENIGN_CHOICES = (('BA', 'STAND_ALONE'), ('ST', 'STRONG'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	STATUS_CHOICES = (('0', 'First Check'), ('1', 'Second Check'), ('2', 'Complete'), ('3', 'Archived'))
	GENUINE_ARTEFACT_CHOICES = (
		('0', 'Pending'), 
		('1', 'Genuine - New Classification'), 
		('2', 'Genuine - Use Previous Classification'),
		('3', 'Genuine - Not Analysed'),
		('4', 'Artefact'),
		('5', 'Genuine - Not Analysed Unrelated to Phenotype'),
	)
	FINAL_CLASS_CHOICES = (
		('0', 'Benign'), 
		('1', 'Likely Benign'), 
		('2', 'VUS - Criteria Not Met'),
		('3', 'Contradictory Evidence Provided'), 
		('4', 'Likely Pathogenic'), 
		('5', 'Pathogenic'),
		('6', 'Artefact'), 
		('7', 'Not analysed'),
		('8', 'Not Analysed Unrelated to Phenotype'),
	)

	history = AuditlogHistoryField()

	variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='variant_classifications')
	sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
	selected_transcript_variant = models.ForeignKey(TranscriptVariant, on_delete=models.CASCADE, null=True, blank=True)
	creation_date = models.DateTimeField()
	first_check_date = models.DateTimeField(null=True, blank=True)
	second_check_date = models.DateTimeField(null=True, blank=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_creator')
	user_first_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_first_checker')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_second_checker')
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
	genuine = models.CharField(max_length=1, choices=GENUINE_ARTEFACT_CHOICES, default='0')
	first_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES)
	second_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES)  # The actual one we want to display.
	is_trio_de_novo = models.BooleanField()
	genotype = models.IntegerField(null=True, blank=True)
	guideline_version = models.CharField(max_length=20)
	vep_version = models.CharField(max_length=20)
	analysis_id = models.IntegerField(null=True, blank=True, db_index=True)
	artefact_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='artefact_checker')
	artefact_check_date = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f'{self.id}'

	def display_status(self):
		"""
		Take the status in the database e.g. 0 and return the string \
		which corresponds to that e.g First check
		"""
		return self.STATUS_CHOICES[int(self.status)][1]

	def display_genuine(self):
		"""
		Display the genuine status attribute.
		"""
		return self.GENUINE_ARTEFACT_CHOICES[int(self.genuine)][1]

	def display_first_classification(self):
		"""
		Take the classification in the database e.g. 0 and return the string \
		which corresponds to that e.g Pathogenic

		This displays the result of the first check analysis.
		"""
		return self.FINAL_CLASS_CHOICES[int(self.first_final_class)][1]		

	def display_final_classification(self):

		"""
		Take the classification in the database e.g. 0 and return the string \
		which corresponds to that e.g Pathogenic.

		This displays the result of the second check analysis.
		"""
		if self.second_final_class == 'False':
			return 'False'
		else:
			return self.FINAL_CLASS_CHOICES[int(self.second_final_class)][1]	

	def display_classification(self):
		"""
		For instances where we only want to display the final class if the \
		classification has been completed i.e. second check has been done.
		"""
		if self.status == '2' or self.status == '3':
			return self.display_final_classification()
		else:
			return 'Pending'

	def initiate_classification(self):
		"""
		Creates the needed ClassificationAnswer objects for a new classification.
		"""
		answers = ClassificationAnswer.objects.filter(classification=self)

		#Check we're not running the function twice
		if len(answers) == 0:

			# for TSC
			if self.sample.analysis_performed.panel[0:4].lower() == 'tsc_':

				questions = ClassificationQuestion.objects.all()

			else:

				questions = ClassificationQuestion.objects.all().exclude(category = 'Familial Cancer Specific')


			questions = questions.order_by('order')

			for question in questions:

				new_answer = ClassificationAnswer.objects.create(
					classification = self,
					classification_question=question,
					selected_first = False,
					selected_second = False,
					strength_first = question.default_strength,
					strength_second = question.default_strength,
					)
				new_answer.save()

		else:
			return HttpResponseForbidden()

		return None

	def calculate_acmg_score_first(self):
		"""
		Use the acmg_classifer util to generate the ACMG classification.
		Calculates based on the first user's input.
		Output:
		integer classification to store in database, corresponding to 
		FINAL_CLASS_CHOICES above
		"""
		# pull out all classification questions and answers
		classification_answers = ClassificationAnswer.objects.filter(classification=self)

		# for TSC
		if self.sample.analysis_performed.panel[0:4].lower() == 'tsc_':

			correct_number_of_questions = ClassificationQuestion.objects.all().count()

		else:

			correct_number_of_questions = ClassificationQuestion.objects.all().exclude(category = 'Familial Cancer Specific').count()


		#Check we have all the answers
		if len(classification_answers) != correct_number_of_questions:
			return '7'

		results = []
		tags = []

		# Only get the ones where the user has selected True
		for answer in classification_answers:

			if answer.selected_first == True:

				results.append((answer.classification_question.acmg_code, answer.strength_first))
				tags.append(answer.classification_question.acmg_code)

		# If nothing applied, return VUS
		if len(results) == 0:
			return '2'

		# otherwise, if valid, classify
		if acmg_classifier.valid_input(tags) == True:
			final_class = acmg_classifier.classify(results)

			return final_class

		return '7'

	def calculate_acmg_score_second(self):
		"""
		Use the acmg_classifer util to generate the ACMG classification.
		Calculates based on the second user's input.
		Output: integer classification to store in database, corresponding to 
		FINAL_CLASS_CHOICES above
		"""
		# pull out all classification questions and answers
		classification_answers = ClassificationAnswer.objects.filter(classification=self)

		# for TSC
		if self.sample.analysis_performed.panel[0:4].lower() == 'tsc_':

			correct_number_of_questions = ClassificationQuestion.objects.all().count()

		else:

			correct_number_of_questions = ClassificationQuestion.objects.all().exclude(category = 'Familial Cancer Specific').count()


		#Check we have all the answers
		if len(classification_answers) != correct_number_of_questions:
			return '7'

		results = []
		tags = []

		# Only get the ones where the user has selected True
		for answer in classification_answers:

			if answer.selected_second == True:

				results.append((answer.classification_question.acmg_code, answer.strength_second))
				tags.append(answer.classification_question.acmg_code)

		# If nothing applied, return VUS
		if len(results) == 0:
			return '2'

		# otherwise, if valid, classify
		if acmg_classifier.valid_input(tags) == True:
			final_class = acmg_classifier.classify(results)
			return final_class

		return '7'

	def display_genotype(self):
		"""
		Display Genotype
		"""

		if self.genotype == 1:

			return 'Het'

		elif self.genotype == 2:

			return 'Hom'

		elif self.genotype == 3:

			return 'Hemi'

		elif self.genotype == 4:

			return 'Mosaic'

		else:

			return 'NA'

	def get_igv_locus(self):
		"""
		Return the variant position for IGV

		"""

		variant = self.variant

		return f'{variant.chromosome}:{variant.position-20}-{variant.position+20}'


class ClassificationQuestion(models.Model):
	"""
	Model to hold the possible questions that a user may be asked.

	That is hold all the ACMG questions e.g. PVS1

	"""

	STRENGTH_CHOICES = (('PV', 'PATH_VERY_STRONG'),
						('PS', 'PATH_STRONG'),
	 					('PM', 'PATH_MODERATE'),
						('PP', 'PATH_SUPPORTING', ),
	 					('BA', 'BENIGN_STAND_ALONE'),
						('BS', 'BENIGN_STRONG'),
						('BP', 'BENIGN_SUPPORTING'))


	CATEGORY_CHOICES = (('Variant type and gene-variant profile', 'A'), 
						('Frequency data', 'B'),
						('Review of literature and databases', 'C'),
						('Functional studies', 'D'),
						('Computer predictions', 'E'),
						('De novo variants', 'F'),
						('Phenotype and family history information', 'G'),
						('Multiple variants identified in a patient', 'H'),
						('Familial Cancer Specific', 'I'))
		
	acmg_code = models.CharField(max_length=5)
	order = models.IntegerField()
	text = models.TextField()
	default_strength = models.CharField(max_length=2, choices=STRENGTH_CHOICES)
	allowed_strength_change = models.BooleanField() #Can the user change the strength?
	pathogenic_question = models.BooleanField()
	category = models.TextField(choices= CATEGORY_CHOICES)

	def __str__ (self):
		return self.acmg_code

	def strength_options(self):
		"""
		Returns the strength options for a question.

		Used to create a choice field in the relevant forms.

		"""
		# list of codes that can be applied at pathogenic very strong and benign standalone
		allowed_pvs = ['PVS1', 'PS2', 'PM3', 'PM6']
		allowed_ba = ['BA1']

		if self.allowed_strength_change == False:

			return default_strength

		elif self.pathogenic_question == True and self.acmg_code not in allowed_pvs:

			return ['PS', 'PM', 'PP']

		elif self.pathogenic_question == True and self.acmg_code in allowed_pvs:

			return ['PV','PS', 'PM', 'PP']

		elif self.pathogenic_question == False and self.acmg_code in allowed_ba:

			return ['BA', 'BS', 'BP']

		else:

			return ['BS', 'BP']


class ClassificationAnswer(models.Model):
	"""
	Model to store the user's selected answer (True, False) and the selected strength for each \
	ClassificationQuestion in a Classification.

	"""

	STRENGTH_CHOICES = (('PV', 'PATH_VERY_STRONG'),('PS', 'PATH_STRONG'),
	 ('PM', 'PATH_MODERATE'), ('PP', 'PATH_SUPPORTING', ),
	 ('BA', 'BENIGN_STAND_ALONE'), ('BS', 'BENIGN_STRONG'), ('BP', 'BENIGN_SUPPORTING'))

	history = AuditlogHistoryField()

	classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
	classification_question = models.ForeignKey(ClassificationQuestion, on_delete=models.CASCADE)
	selected_first = models.BooleanField()
	strength_first = models.CharField(max_length=2, choices=STRENGTH_CHOICES)
	selected_second = models.BooleanField()
	strength_second = models.CharField(max_length=2, choices=STRENGTH_CHOICES)
	comment = models.TextField()

	def __str__(self):
		return f'{self.id}'


class UserComment(models.Model):
	"""
	Model to hold a comment by a user against a Classification object.

	"""

	classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	time = models.DateTimeField()
	visible = models.BooleanField(default=True)

	def __str__(self):
		if len(self.text) > 50:
			return f'{self.text[:50]}...'
		else:
			return f'{self.text}'


	def get_evidence(self):
		"""
		Return the evidence associated with a comment.

		"""
		evidence = Evidence.objects.filter(comment=self)

		if len(evidence) == 0:

			return None

		return evidence


class Evidence(models.Model):
	"""
	Model to hold files that relate to evidence e.g. pdfs, screenshots.
	Must be associated with a comment.
	"""

	file = models.FileField(upload_to='uploads/', null=True, blank=True)
	comment = models.ForeignKey(UserComment, on_delete=models.CASCADE)
	
class CNVSample(models.Model):
	"""
	Model to hold CNV Sample information upon upload
	"""
	history = AuditlogHistoryField()
	
	sample_name = models.CharField(max_length=150, default='')  # sample_id only
	worklist = models.ForeignKey(Worklist, on_delete=models.CASCADE)
	affected_with = models.TextField()
	analysis_performed = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE)
	analysis_complete = models.BooleanField()
	platform = models.TextField()
	cyto = models.TextField(null=True)
	
class CNVVariant(models.Model):
	"""
	Model to hold CNV variant information
	"""
	full = models.TextField() #full CNV variant in format CHR:START-STOP
	chromosome = models.TextField()
	start = models.IntegerField()
	stop = models.IntegerField()
	length = models.IntegerField()
	genome = models.TextField(default='GRCh37')
	cyto_loc = models.TextField()
	max_start = models.IntegerField()
	max_stop = models.IntegerField()

class CNV(models.Model):	
	"""
	Model to hold CNV classification information 
	"""	
	STATUS_CHOICES = (('0', 'First Check'), ('1', 'Second Check'), ('2', 'Complete'), ('3', 'Archived'))
	FINAL_CLASS_CHOICES = (
		('0', 'Benign'), 
		('1', 'Likely Benign'), 
		('2', 'VUS - Criteria Not Met'),
		('3', 'Likely Pathogenic'), 
		('4', 'Pathogenic'),
		('5', 'Not analysed'),
		('6', 'Artefact')
	)
	GENUINE_ARTEFACT_CHOICES = (
		('0', 'Pending'), 
		('1', 'Genuine - New Classification'), 
		('2', 'Genuine - Use Previous Classification'),
		('3', 'Genuine - Not Analysed'),
		('4', 'Artefact')
	)
	
	history = AuditlogHistoryField()
	
	sample = models.ForeignKey(CNVSample, on_delete=models.CASCADE)
	cnv = models.ForeignKey(CNVVariant, on_delete=models.CASCADE, related_name='cnv_classification')
	gain_loss = models.TextField()
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
	user_first_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='cnv_first_checker')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='cnv_second_checker')
	first_final_score = models.DecimalField(decimal_places=2, max_digits=10, default='0')
	second_final_score = models.DecimalField(decimal_places=2, max_digits=10, default='0')
	first_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES, default = '5')
	second_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES, default = '5')  # The actual one we want to display.
	inheritance = models.TextField(null=True)
	copy = models.TextField(null=True)
	genotype = models.TextField(null=True)
	genuine = models.CharField(max_length=1, choices=GENUINE_ARTEFACT_CHOICES, default='0')
	method = models.TextField() #this allows us to change the ACMG guidelines being used whilst retaining the information on actual gain/loss
	first_check_date = models.DateTimeField(null=True, blank=True)
	second_check_date = models.DateTimeField(null=True, blank=True)
	creation_date = models.DateTimeField(null=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='cnv_user_creator')
		
	def __str__(self):
		return f'{self.id}'

	def display(self):

		chrom = self.cnv.chromosome
		start = self.cnv.start
		end = self.cnv.stop
		gain_loss = self.gain_loss

		if gain_loss == 'Loss':

			gain_loss = 'del'
		
		elif gain_loss == 'Loh':
		
			gain_loss = "LOH"

		elif gain_loss == 'Gain':

			gain_loss = 'dup'

		else:

			raise Exception('Unknown CNV type')

		return f'{chrom}:{start}-{end}{gain_loss}'
	
	def genes_as_list(self):
		return CNVGene.objects.filter(cnv=self)

	def genes_as_str(self):
		genes =  CNVGene.objects.filter(cnv=self)

		genes = [gene.gene.name for gene in genes]

		return ','.join(genes)
	
	def count_genes(self):

		count = CNVGene.objects.filter(cnv=self)

		if count is None:

			return 0

		return len(CNVGene.objects.filter(cnv=self))
		
	def display_status(self):
		"""
		Take the status in the database e.g. 0 and return the string \
		which corresponds to that e.g First check
		"""
		return self.STATUS_CHOICES[int(self.status)][1]

	def display_genuine(self):
		"""
		Display the genuine status attribute.
		"""
		return self.GENUINE_ARTEFACT_CHOICES[int(self.genuine)][1]
	
	def display_first_classification(self):
		"""
		Take the classification in the database e.g. 0 and return the string \
		which corresponds to that e.g Pathogenic

		This displays the result of the first check analysis.
		"""
		return self.FINAL_CLASS_CHOICES[int(self.first_final_class)][1]		

	def display_final_classification(self):

		"""
		Take the classification in the database e.g. 0 and return the string \
		which corresponds to that e.g Pathogenic.

		This displays the result of the second check analysis.
		"""
		if  self.second_final_class == 'False':
			return 'False'
		else:
			return self.FINAL_CLASS_CHOICES[int(self.second_final_class)][1]	

	def display_classification(self):
		"""
		For instances where we only want to display the final class if the \
		classification has been completed i.e. second check has been done.
		"""
		if self.status == '2' or self.status == '3':
			return self.display_final_classification()
		else:
			return 'Pending'
			
	def initiate_classification(self):
		"""
		Creates the needed CNVClassificationAnswer objects for a new CNV classification.
		"""
		if self.method == 'Gain':

			answers = CNVGainClassificationAnswer.objects.filter(cnv=self)

			#Check we're not running the function twice
			if len(answers) == 0:

				questions = CNVGainClassificationQuestion.objects.all()

				for question in questions:

					new_answer = CNVGainClassificationAnswer.objects.create(
						cnv = self,
						cnv_classification_question=question,
						score = 0,
						comment = ''
					)
					new_answer.save()

			else:

				return HttpResponseForbidden()

			return None

		elif self.method == 'Loss':
			answers = CNVLossClassificationAnswer.objects.filter(cnv=self)

			#Check we're not running the function twice
			if len(answers) == 0:

				questions = CNVLossClassificationQuestion.objects.all()

				for question in questions:

					new_answer = CNVLossClassificationAnswer.objects.create(
						cnv = self,
						cnv_classification_question=question,
						score = 0,
						comment = ''
						)

					new_answer.save()
			else:

				return HttpResponseForbidden()
	
			return None
	
	def calculate_acmg_score_first(self):
		"""
		Use the acmg_classifer util to generate the ACMG classification.
		Calculates based on the first user's input.
		Output:
		integer classification to store in database, corresponding to 
		FINAL_CLASS_CHOICES above
		"""
		
		if self.method == 'Gain':
			# pull out all classification questions and answers
			classification_answers = CNVGainClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVGainClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score

			return final_score
		
		elif self.method == 'Loss':
			
			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score

			return final_score
	
	def calculate_acmg_score_second(self):
		"""
		Use the acmg_classifer util to generate the ACMG classification.
		Calculates based on the second user's input.
		Output:
		integer classification to store in database, corresponding to 
		FINAL_CLASS_CHOICES above
		"""
		
		if self.method == 'Gain':
			# pull out all classification questions and answers
			classification_answers = CNVGainClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVGainClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score_second

			return final_score
		
		elif self.method == 'Loss':

			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score_second

			return final_score
			
		elif self.gain_loss == 'Loh':
			
			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score_second

			return final_score

	def get_answers_for_download(self):

		if self.method == 'Gain':
			# pull out all classification questions and answers
			classification_answers = CNVGainClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVGainClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			return classification_answers
		
		elif self.method == 'Loss':

			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			return classification_answers

		elif self.gain_loss == 'Loh':
			
			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) == all_questions_count:
				pass
			elif len(classification_answers) == (all_questions_count - 1):
				pass
			else:
				return 'NA'

			return classification_answers
	
	
			
class CNVGene(models.Model):
	""" 
	Model to hold all of the CNV genes 
	"""
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE)
	cnv = models.ForeignKey(CNV, on_delete=models.CASCADE)

class CNVLossClassificationQuestion(models.Model):
	"""
	Model to hold the possible questions that a user may be asked for CNV Classification.

	That is hold all the ACMG questions e.g. PVS1

	"""

	CATEGORY_CHOICES = (('Section 1: Initial assessment of genomics content', '1'), 
						('Section 2: Overlap with established/predicted haploinsufficiency (HI) or established benign genes/genomic regions (Skip to Section 3 if your copy-number loss DOES NOT overlap these types of genes/regions)', '2'),
						('Section 3: Evaluation of Gene Number', '3'),
						('Section 4: Detailed evaluation of genomic content using cases from published literature, public databases, and/or internal lab data', '4'),
						('Section 5: Evaluation of inheritance pattern/family history for patient being studied', '5'),
						('Section 6: Other criteria from SNV variant interpretation guidelines','6'),
						)
	
	TYPE_CHOICES = (('Pathogenic Supporting','PS'),('Benign Supporting','BS'),('Zero','0'),('1B','1B'),('Other','Other'))
		
	evidence_type = models.CharField(max_length=500)
	evidence = models.TextField()
	suggested = models.TextField()
	max_score = models.FloatField(null=True)
	category = models.TextField(choices= CATEGORY_CHOICES)
	qu_type = models.TextField(choices=TYPE_CHOICES)
	order = models.IntegerField(blank=True, null=True)
	
	def score_range_pos(self):
		
		#code block for having every number between 0 and 1 in increments of 0.05 up to the max score
		#max_val = self.max_score + 0.01
		#array = np.arange(0,max_val,0.05)
		
		#new_list = []
		
		#for i in array:
		
		#	new_list.append(str(round(i, 2)))
		
		#code block for having only 0, 0.15, 0.3, 0.45, 0.9 and 1 as options, up to the max score
		array = [0.00,0.15,0.30,0.45,0.90,1.00]
		new_list = []
		
		for i in array:
			if i <= self.max_score:
				new_list.append(round(i,2))
		
		return new_list
	
	def score_range_neg(self):
		
		#code block for having every number between 0 and 1 in increments of 0.05 up to the max score
		#max_val = self.max_score - 0.01
		#array = np.arange(0,max_val,-0.05)
		
		#new_list = []
		
		#for i in array:
		
		#	new_list.append(str(round(i, 2)))
		
		
		#code block for having only 0, -0.15, -0.3, -0.45, -0.9 and -1 as options, up to the max score
		array = [0.00,-0.15,-0.30,-0.45,-0.90,-1.00]
		new_list = []
		
		for i in array:
			if i >= self.max_score:
				new_list.append(round(i,2))
		return new_list

		
class CNVGainClassificationQuestion(models.Model):
	"""
	Model to hold the possible questions that a user may be asked for CNV Classification.

	That is hold all the ACMG questions e.g. PVS1

	"""

	CATEGORY_CHOICES = (('Section 1: Initial assessment of genomics content', '1'), 
						('Section 2: Overlap with established triplosensitive (TS), haploinsufficiency (HI) or benign genes/genomic regions (Skip to Section 3 if your copy-number gain DOES NOT overlap these types of genes/regions)', '2'),
						('Section 3: Evaluation of Gene Number', '3'),
						('Section 4: Detailed evaluation of genomic content using cases from published literature, public databases, and/or internal lab data', '4'),
						('Section 5: Evaluation of inheritance pattern/family history for patient being studied', '5'),
						('Section 6: Other criteria from SNV variant interpretation guidelines','6'),
						)
	
	TYPE_CHOICES = (('Pathogenic Supporting','PS'),('Benign Supporting','BS'),('Zero','0'),('1B','1B'),('Other','Other'))
	
	evidence_type = models.CharField(max_length=500)
	evidence = models.TextField()
	suggested = models.TextField()
	max_score = models.FloatField(null=True)
	category = models.TextField(choices= CATEGORY_CHOICES)
	qu_type = models.TextField(choices=TYPE_CHOICES)
	order = models.IntegerField(blank=True, null=True)
	
	#Function to produce range of values for the scoring
	def score_range_pos(self):
		
		#code block for having every number between 0 and 1 in increments of 0.05 up to the max score
		#max_val = self.max_score + 0.01
		#array = np.arange(0,max_val,0.05)
		
		#new_list = []
		
		#for i in array:
		
		#	new_list.append(str(round(i, 2)))
			
		#code block for having only 0, 0.15, 0.3, 0.45, 0.9 and 1 as options, up to the max score
		array = [0.00,0.15,0.30,0.45,0.90,1.00]
		new_list = []
		
		for i in array:
			if i <= self.max_score:
				new_list.append(round(i,2))
		
		return new_list
		
	def score_range_neg(self):
	 	
	 	#code block for having every number between 0 and 1 in increments of 0.05 up to the max score
		#max_val = self.max_score - 0.01
		#array = np.arange(0,max_val,-0.05)
		
		#new_list = []
		
		#for i in array:
		
		#	new_list.append(str(round(i, 2)))
		
		#code block for having only 0, 0.15, 0.3, 0.45, 0.9 and 1 as options, up to the max score
		array = [0.00,-0.15,-0.30,-0.45,-0.90,-1.00]
		new_list = []
		
		for i in array:
			if i >= self.max_score:
				new_list.append(round(i,2))
		
		return new_list
	
class CNVGainClassificationAnswer(models.Model):
	"""
	Model to store the user's selected answer (True, False) and the selected strength for each \
	ClassificationQuestion in a Classification.

	"""
	history = AuditlogHistoryField()
	
	cnv = models.ForeignKey(CNV, on_delete=models.CASCADE)
	cnv_classification_question = models.ForeignKey(CNVGainClassificationQuestion, on_delete=models.CASCADE)
	score = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
	comment = models.TextField(null=True)
	score_second = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
	comment_second = models.TextField(null=True)

	def __str__(self):
		return f'{self.id}'
		
class CNVLossClassificationAnswer(models.Model):
	"""
	Model to store the user's selected answer (True, False) and the selected strength for each \
	ClassificationQuestion in a Classification.

	"""
	history = AuditlogHistoryField()
	
	cnv = models.ForeignKey(CNV, on_delete=models.CASCADE)
	cnv_classification_question = models.ForeignKey(CNVLossClassificationQuestion, on_delete=models.CASCADE)
	score = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
	comment = models.TextField(null=True)
	score_second = models.DecimalField(max_digits=10, decimal_places=2, default='0.00')
	comment_second = models.TextField(null=True)

	def __str__(self):
		return f'{self.id}'

class CNVUserComment(models.Model):
	"""
	Model to hold a comment by a user against a CNV Classification object.

	"""

	classification = models.ForeignKey(CNV, on_delete=models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	time = models.DateTimeField()
	visible = models.BooleanField(default=True)

	def __str__(self):
		if len(self.text) > 50:
			return f'{self.text[:50]}...'
		else:
			return f'{self.text}'


	def get_evidence(self):
		"""
		Return the evidence associated with a comment.

		"""
		evidence = CNVEvidence.objects.filter(comment=self)

		if len(evidence) == 0:

			return None

		return evidence
		
class CNVEvidence(models.Model):
	"""
	Model to hold files that relate to CNV evidence e.g. pdfs, screenshots.
	Must be associated with a comment.
	"""

	file = models.FileField(upload_to='uploads/', null=True, blank=True)
	comment = models.ForeignKey(CNVUserComment, on_delete=models.CASCADE)

# register audit logs
auditlog.register(Worklist)
auditlog.register(Panel)
auditlog.register(Sample)
auditlog.register(Variant)
auditlog.register(Gene)
auditlog.register(Transcript)
auditlog.register(TranscriptVariant)
auditlog.register(Classification)
auditlog.register(ClassificationQuestion)
auditlog.register(ClassificationAnswer)
auditlog.register(UserComment)
auditlog.register(Evidence)
auditlog.register(CNVSample)
auditlog.register(CNV)
