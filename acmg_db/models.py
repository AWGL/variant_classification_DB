from django.db import models
from auditlog.registry import auditlog
from auditlog.models import LogEntry
from auditlog.models import AuditlogHistoryField

from acmg_db.utils import acmg_classifier

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

	name = models.CharField(max_length=255, unique=True, default='') # worksheet_id + '-' + sample_id + '-' + analysis performed
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

	variant_hash = models.CharField(max_length=64, primary_key =True)
	chromosome  = models.CharField(max_length=25, default='')
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

		if len(classifications) >0:

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


	def all_inheritance_patterns(self):
		'''
		Join all inheritance patterns together into a string for viewing in the app.
		Making the initial list is over complicated because the list is represented as a string in the database,
		so it needs to be converte back into a list before joining
		'''
		inheritance_list = []
		for i in str(self.inheritance_pattern).split(', '):
			i = i.replace('[', '').replace(']', '').replace("'", "")
			inheritance_list.append(i)

		inheritance_string = ', '.join(inheritance_list)
		return inheritance_string


	def get_inheritance_choices_as_list(self):

		inheritance_list = []
		for i in str(self.inheritance_pattern).split(', '):
			i = i.replace('[', '').replace(']', '').replace("'", "")
			inheritance_list.append(i)

		return inheritance_list


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
		('4', 'Artefact')
	)
	FINAL_CLASS_CHOICES = (
		('0', 'Benign'), 
		('1', 'Likely Benign'), 
		('2', 'VUS - Criteria Not Met'),
		('3', 'Contradictory Evidence Provided'), 
		('4', 'Likely Pathogenic'), 
		('5', 'Pathogenic'),
		('6', 'Artefact'), 
		('7', 'Not analysed')
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
	analysis_id = models.IntegerField(null=True, blank=True)
	genome = models.TextField(default='GRCh37')

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
		Creates the needed ClassificationAnswer objects for a new classification.
		"""
		answers = ClassificationAnswer.objects.filter(classification=self)

		#Check we're not running the function twice
		if len(answers) == 0:
			questions = ClassificationQuestion.objects.all()
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
		all_questions_count = ClassificationQuestion.objects.all().count()

		#Check we have all the answers
		if len(classification_answers) != all_questions_count:
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
		all_questions_count = ClassificationQuestion.objects.all().count()

		#Check we have all the answers
		if len(classification_answers) != all_questions_count:
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
						('Multiple variants identified in a patient', 'H'))
		
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
	sample_name = models.CharField(max_length=150, default='')  # sample_id only
	worklist = models.ForeignKey(Worklist, on_delete=models.CASCADE)
	affected_with = models.TextField()
	analysis_performed = models.ForeignKey(Panel, null=True, blank=True, on_delete=models.CASCADE)
	analysis_complete = models.BooleanField()
	genome = models.TextField(default='GRCh37')
	platform = models.TextField()
	cyto = models.TextField(null=True)
	
class CNV(models.Model):	
	"""
	Model to hold CNV variant information 
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
	cnv = models.TextField()
	gain_loss = models.TextField()
	status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0')
	user_first_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='cnv_first_checker')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='cnv_second_checker')
	first_final_score = models.DecimalField(decimal_places=2, max_digits=10, default='0')
	second_final_score = models.DecimalField(decimal_places=2, max_digits=10, default='0')
	first_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES, default = 'Not analysed')
	second_final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES, default = 'Not analysed')  # The actual one we want to display.
	inheritance = models.TextField(null=True)
	copy = models.TextField(null=True)
	genotype = models.TextField(null=True)
	genuine = models.CharField(max_length=1, choices=GENUINE_ARTEFACT_CHOICES, default='0')
		
	def __str__(self):
		return f'{self.id}'
	
	def genes_as_list(self):
		return CNVGene.objects.filter(cnv=self)
	
	def count_genes(self):
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
		if self.gain_loss == 'Gain':
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
		elif self.gain_loss == 'Loss':
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
		
		if self.gain_loss == 'Gain':
			# pull out all classification questions and answers
			classification_answers = CNVGainClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVGainClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) != all_questions_count:
				return '7'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score

			return final_score
		
		elif self.gain_loss == 'Loss':
			
			# pull out all classification questions and answers
			classification_answers = CNVLossClassificationAnswer.objects.filter(cnv=self)
			all_questions_count = CNVLossClassificationQuestion.objects.all().count()

			#Check we have all the answers
			if len(classification_answers) != all_questions_count:
				return '7'

			final_score = 0

			#Add up total score
			for answer in classification_answers:
				final_score+=answer.score

			return final_score
			
class CNVGene(models.Model):
	""" 
	Model to hold all of the CNV genes 
	"""
	gene = models.TextField()
	cnv = models.ForeignKey(CNV, on_delete=models.CASCADE)

class CNVLossClassificationQuestion(models.Model):
	"""
	Model to hold the possible questions that a user may be asked for CNV Classification.

	That is hold all the ACMG questions e.g. PVS1

	"""

	CATEGORY_CHOICES = (('Section 1: Initial assessment of genomics content', '1'), 
						('Section 2: Overlap with established/predicted haploinsufficiency (HI) or established benign genes/genomic regions (Skip to Section 3 if your copy-number loss DOES NOT overlap these types of genes/regions)', '2'),
						('Section 3: Evaluation of Gene Number', '3'),
						('Section 4: Detailed evaluation of genomic content using cases from published literature, public databases, and/or internal lab data (Skip to section 5 if either your CNV overlapped with an established HI gene/region in section 2, OR there have been no reports associating either the CNV or any genes within the CNV with human phenotypes caused by loss of function [LOF] or copy-number loss)', '4'),
						('Section 5: Evaluation of inheritance pattern/family history for patient being studied', '5'),
						)
		
	evidence_type = models.CharField(max_length=500)
	evidence = models.TextField()
	suggested = models.TextField()
	max_score = models.DecimalField(decimal_places=2, max_digits=10)
	category = models.TextField(choices= CATEGORY_CHOICES)

		
class CNVGainClassificationQuestion(models.Model):
	"""
	Model to hold the possible questions that a user may be asked for CNV Classification.

	That is hold all the ACMG questions e.g. PVS1

	"""

	CATEGORY_CHOICES = (('Section 1: Initial assessment of genomics content', '1'), 
						('Section 2: Overlap with established triplosensitive (TS), haploinsufficiency (HI) or benign genes/genomic regions (Skip to Section 3 if your copy-number gain DOES NOT overlap these types of genes/regions', '2'),
						('Section 3: Evaluation of Gene Number', '3'),
						('Section 4: Detailed evaluation of genomic content using cases from published literature, public databases, and/or internal lab data (Skip to section 5 if there have been no reports associating either the copy-number gain or any of the genes therein with human phenotypes caused by triplosensitivity', '4'),
						('Section 5: Evaluation of inheritance pattern/family history for patient being studied', '5'),
						)
		
	evidence_type = models.CharField(max_length=500)
	evidence = models.TextField()
	suggested = models.TextField()
	max_score = models.DecimalField(decimal_places=2, max_digits=10)
	category = models.TextField(choices= CATEGORY_CHOICES)
	
class CNVGainClassificationAnswer(models.Model):
	"""
	Model to store the user's selected answer (True, False) and the selected strength for each \
	ClassificationQuestion in a Classification.

	"""
	history = AuditlogHistoryField()
	
	cnv = models.ForeignKey(CNV, on_delete=models.CASCADE)
	cnv_classification_question = models.ForeignKey(CNVGainClassificationQuestion, on_delete=models.CASCADE)
	score = models.DecimalField(max_digits=10, decimal_places=2)
	comment = models.TextField()

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
	score = models.DecimalField(max_digits=10, decimal_places=2)
	comment = models.TextField()

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
auditlog.register(CNVGainClassificationQuestion)
auditlog.register(CNVLossClassificationQuestion)
auditlog.register(CNVGainClassificationAnswer)
auditlog.register(CNVLossClassificationAnswer)
