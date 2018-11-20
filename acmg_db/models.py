from django.db import models
from .utils import acmg_classifier


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
	Class to hold a transcript e.g NM0001.2

	"""

	name = models.CharField(max_length=25, primary_key=True)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=True,blank=True)


class TranscriptVariant(models.Model):
	"""
	Class to link a variant with a transcript

	"""
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
	transcript = models.ForeignKey(Transcript,on_delete=models.CASCADE, null=True, blank=True)
	hgvs_c = models.TextField(null=True, blank=True)
	hgvs_p = models.TextField(null=True, blank=True)
	exon = models.CharField(max_length=10,null=True, blank=True)

class Classification(models.Model):

	"""
	Class to hold results of ACMG classification


	"""

	PATH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'), ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	BENIGN_CHOICES = (('BA', 'STAND_ALONE'), ('ST', 'STRONG'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	STATUS_CHOICES = (('0', 'Awaiting Analysis'), ('1', 'Awaiting Second Check'), ('2', 'Complete'), ('3', 'OLD'))

	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
	selected_transcript_variant = models.ForeignKey(TranscriptVariant, on_delete=models.CASCADE, null=True, blank=True)
	creation_date = models.DateTimeField()
	second_check_date = models.DateTimeField(null=True, blank=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_creator')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_second_checker')
	status = models.CharField(max_length=1, choices =STATUS_CHOICES, default='0')
	final_class = models.CharField(max_length=25, null=True, blank=True)

	sample_lab_number = models.CharField(max_length=25, null =True, blank=True)
	analysis_performed = models.CharField(max_length=25, null =True, blank=True)
	other_changes = models.CharField(max_length=25, null =True, blank=True)
	affected_with = models.CharField(max_length=25, null =True, blank=True)
	trio_de_novo = models.BooleanField(null =True, blank=True)
	inheritance_pattern = models.CharField(max_length=30, null=True, blank=True)
	conditions = models.TextField(null=True, blank=True)


	def display_status(self):
		"""
		Take the status in the database e.g. 0 and return the string \
		which corresponds to that e.g.g Awaiting Analysis

		"""
		STATUS_CHOICES = (('0', 'Awaiting Analysis'), ('1', 'Awaiting Second Check'), ('2', 'Complete'), ('3', 'OLD'))

		return STATUS_CHOICES[int(self.status)][1]


	def display_classification(self):
		"""
		For instances where we only want to display the final class if the \
		classification has been completed i.e. second check has been done.

		"""

		if self.status == '2':

			return self.final_class

		else:

			return 'Not Displayed'



	def initiate_classification(self):
		"""
		When a user creates a new classicication for a variant then we \
		need to create the ClassificationAnswer objects.

		This function does that.


		"""


		answers = ClassificationAnswer.objects.filter(classification=self)

		if len(answers) == 0:

			questions = ClassificationQuestion.objects.all()

			questions = questions.order_by('order')

			for question in questions:

				new_answer = ClassificationAnswer.objects.create(
					classification = self,
					classification_question=question,
					selected = False,
					strength = question.default_strength
					)

				new_answer.save()

		return None


	def calculate_acmg_score(self):

		classification_answers = ClassificationAnswer.objects.filter(classification=self)

		all_questions_count = ClassificationQuestion.objects.all().count()

		if len(classification_answers) != all_questions_count:

			return False

		results = []

		tags = []

		for answer in classification_answers:

			if answer.selected == True:

				results.append((answer.classification_question.acmg_code, answer.strength))

				tags.append(answer.classification_question.acmg_code)


		if acmg_classifier.valid_input(tags) == True:

			updated_acmg_codes = acmg_classifier.adjust_strength(results)

			return acmg_classifier.classify(updated_acmg_codes)

		return False






class ClassificationQuestion(models.Model):

	STRENGTH_CHOICES = (('PV', 'PATH_VERY_STRONG'),('PS', 'PATH_STRONG'),
	 ('PM', 'PATH_MODERATE'), ('PP', 'PATH_SUPPORTING', ),
	 ('BA', 'BENIGN_STAND_ALONE'), ('BS', 'BENIGN_STRONG'), ('BP', 'BENIGN_SUPPORTING'))


	acmg_code = models.CharField(max_length=5)
	order = models.IntegerField()
	text = models.TextField()
	default_strength = models.CharField(max_length=2, choices=STRENGTH_CHOICES)
	allowed_strength_change = models.BooleanField()
	pathogenic_question = models.BooleanField()

	def __str__ (self):
		return self.acmg_code


	def strength_options(self):

		if self.allowed_strength_change == False:

			return default_strength

		else:

			if self.pathogenic_question == True:

				return ['PV','PS', 'PM', 'PP']

			else:

				return ['BA', 'BS', 'BP']



class ClassificationAnswer(models.Model):

	STRENGTH_CHOICES = (('PV', 'PATH_VERY_STRONG'),('PS', 'PATH_STRONG'),
	 ('PM', 'PATH_MODERATE'), ('PP', 'PATH_SUPPORTING', ),
	 ('BA', 'BENIGN_STAND_ALONE'), ('BS', 'BENIGN_STRONG'), ('BP', 'BENIGN_SUPPORTING'))

	classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
	classification_question = models.ForeignKey(ClassificationQuestion, on_delete=models.CASCADE)
	selected = models.BooleanField()
	strength = models.CharField(max_length=2, choices=STRENGTH_CHOICES)

class UserComment(models.Model):

	"""

	A class to hold a comment by a user against a classification.

	"""
	classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
	user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
	text = models.TextField()
	time = models.DateTimeField()


	def get_evidence(self):

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




