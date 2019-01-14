from django.db import models
from .utils import acmg_classifier
from auditlog.registry import auditlog
from auditlog.models import LogEntry
from auditlog.models import AuditlogHistoryField
from django.contrib.contenttypes.models import ContentType

"""
Some models for the Database

- Please note that the software was originally designed with the idea that a variant could be /
found in many different transcripts and the user would select one from a selection automatcally pulled from \
an annotation source. This feature was removed but the overall models still reflect this so that it can be added \
at a future date if required.

- This software is designed simply and is not fully normalised. Should still provide enough structure so that the \
data can be exported and inported into a futire variant database.



"""

class Worklist(models.Model):
	"""
	Stores which worklist the sample was on.

	"""
	name = models.CharField(max_length=50, primary_key=True)



class Sample(models.Model):

	"""
	Holds information specific to a sample

	"""

	name = models.CharField(max_length=50)
	worklist = models.ForeignKey(Worklist, on_delete=models.CASCADE)
	affected_with = models.TextField()
	analysis_performed = models.TextField()
	analysis_complete = models.BooleanField()
	other_changes = models.TextField()




class Variant(models.Model):

	"""
	Model to hold unique variants within the DB.

	"""

	key = models.CharField(max_length=200, primary_key=True)
	variant_hash = models.CharField(max_length=64, unique =True)
	chromosome  = models.CharField(max_length=25)
	position  = models.IntegerField()
	ref = models.TextField()
	alt = models.TextField()


	def get_genes(self):

		"""
		Return a list of all genes the variant is found in.

		"""

		variant_transcripts = TranscriptVariant.objects.filter(variant=self).exclude(transcript__name = 'None')

		genes = ';'.join(list(set([transcript.transcript.gene.name for transcript in variant_transcripts])))

		return genes



class Gene(models.Model):

	"""
	Class to hold a gene model.

	"""

	name = models.CharField(max_length=25, primary_key=True)


class Transcript(models.Model):

	"""
	Class to hold a transcript e.g NM_007298.3

	"""

	name = models.CharField(max_length=25, primary_key=True)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=True,blank=True)
	refseq_options = models.CharField(max_length=200, null=True, blank=True)
	refseq_selected = models.CharField(max_length=50, null=True, blank=True)


class TranscriptVariant(models.Model):
	"""
	Class to link a variant with a transcript.

	A variant can potentially fall within many transcripts.

	Holds data on HGVS as well as exon

	"""
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
	transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, null=True, blank=True)
	hgvs_c = models.TextField(null=True, blank=True)
	hgvs_p = models.TextField(null=True, blank=True)
	exon = models.CharField(max_length=10,null=True, blank=True)

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
	STATUS_CHOICES = (('0', 'Awaiting Analysis'), ('1', 'Awaiting Second Check'), ('2', 'Complete'), ('3', 'Archived'))
	FINAL_CLASS_CHOICES =(('0', 'Benign'), ('1', 'Likely Benign'), ('2', 'VUS - Criteria Not Met'),
		('3', 'VUS - Contradictory Evidence Provided'), ('4', 'Likely Pathogenic'), ('5', 'Pathogenic'),
		('6', 'Artefact'), ('7', 'NA'))

	history = AuditlogHistoryField()

	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
	sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
	#which variant transcript is associated with the classification.
	selected_transcript_variant = models.ForeignKey(TranscriptVariant, on_delete=models.CASCADE, null=True, blank=True)
	creation_date = models.DateTimeField()
	second_check_date = models.DateTimeField(null=True, blank=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_creator')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_second_checker')
	status = models.CharField(max_length=1, choices =STATUS_CHOICES, default='0')
	final_class = models.CharField(max_length=1, null=True, blank=True, choices = FINAL_CLASS_CHOICES)

	is_trio_de_novo = models.BooleanField()
	inheritance_pattern = models.CharField(max_length=15, null=True, blank=True)
	conditions = models.TextField(null=True, blank=True)


	def display_status(self):
		"""
		Take the status in the database e.g. 0 and return the string \
		which corresponds to that e.g Awaiting Analysis

		"""
		STATUS_CHOICES = (('0', 'Awaiting Analysis'), ('1', 'Awaiting Second Check'), ('2', 'Complete'), ('3', 'Archived'))

		return STATUS_CHOICES[int(self.status)][1]

	def display_final_classification(self):

		"""
		Take the classification in the database e.g. 0 and return the string \
		which corresponds to that e.g Pathogenic

		"""

		FINAL_CLASS_CHOICES =(('0', 'Benign'), ('1', 'Likely Benign'), ('2', 'VUS - Criteria Not Met'),
		('3', 'VUS - Contradictory Evidence Provided'), ('4', 'Likely Pathogenic'), ('5', 'Pathogenic'),
		('6', 'Artefact'), ('7', 'NA'))

		return FINAL_CLASS_CHOICES[int(self.final_class)][1]		


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

		Calculates based on the first user's input

		"""

		classification_answers = ClassificationAnswer.objects.filter(classification=self)

		all_questions_count = ClassificationQuestion.objects.all().count()

		#Check we have all the answers
		if len(classification_answers) != all_questions_count:

			return False

		results = []

		tags = []

		# Only get the ones where the user has selected True
		for answer in classification_answers:

			if answer.selected_first == True:

				results.append((answer.classification_question.acmg_code, answer.strength_first))

				tags.append(answer.classification_question.acmg_code)


		if acmg_classifier.valid_input(tags) == True:

			updated_acmg_codes = acmg_classifier.adjust_strength(results)

			return acmg_classifier.classify(updated_acmg_codes)

		return False

	def calculate_acmg_score_second(self):
		"""
		Use the acmg_classifer util to generate the ACMG classification.

		Calculates based on the second user's input

		"""

		classification_answers = ClassificationAnswer.objects.filter(classification=self)

		all_questions_count = ClassificationQuestion.objects.all().count()

		#Check we have all the answers
		if len(classification_answers) != all_questions_count:

			return False

		results = []

		tags = []

		# Only get the ones where the user has selected True
		for answer in classification_answers:

			if answer.selected_second == True:

				results.append((answer.classification_question.acmg_code, answer.strength_second))

				tags.append(answer.classification_question.acmg_code)


		if acmg_classifier.valid_input(tags) == True:

			updated_acmg_codes = acmg_classifier.adjust_strength(results)

			return acmg_classifier.classify(updated_acmg_codes)

		return False



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

		if self.allowed_strength_change == False:

			return default_strength

		else:

			if self.pathogenic_question == True:

				return ['PV','PS', 'PM', 'PP']

			else:

				return ['BA', 'BS', 'BP']



class ClassificationAnswer(models.Model):
	"""
	Stores the user selected answer (True, False) and the selected strength for each \
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

class UserComment(models.Model):

	"""

	A class to hold a comment by a user against a Classification object.

	"""
	classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	time = models.DateTimeField()


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

auditlog.register(Variant)
auditlog.register(Classification)
auditlog.register(ClassificationQuestion)
auditlog.register(ClassificationAnswer)
auditlog.register(UserComment)


