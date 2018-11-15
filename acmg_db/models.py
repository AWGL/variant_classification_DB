from django.db import models

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



class Classification(models.Model):

	"""
	Class to hold results of ACMG classification


	"""

	PATH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'), ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	BENIGN_CHOICES = (('BA', 'STAND_ALONE'), ('ST', 'STRONG'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	STATUS_CHOICES = (('0', 'NONE'), ('1', 'Awaiting Second Check'), ('2', 'Complete'))
	SAMPLE_TYPE_CHOICES = (('G', 'Germline'), ('S', 'Somatic'))

	variant = models.ForeignKey(Variant,on_delete=models.CASCADE)
	creation_date = models.DateTimeField()
	second_check_date = models.DateTimeField(null=True, blank=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_creator')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_second_checker')
	status = models.CharField(max_length=1, choices =STATUS_CHOICES, default='0')
	acmg_class = models.CharField(max_length=25, null=True, blank=True)
	final_class = models.CharField(max_length=25, null=True, blank=True)
	sample = models.CharField(max_length=25, null =True, blank=True)
	sample_type = models.CharField(max_length=1, choices=SAMPLE_TYPE_CHOICES, null=True, blank=True)
	sample_comment = models.TextField(null=True, blank=True)



	def initiate_classification(self):


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



class ClassificationQuestion(models.Model):

	STRENGTH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'),
	 ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ),
	 ('BA', 'STAND_ALONE'))


	acmg_code = models.CharField(max_length=5)
	order = models.IntegerField()
	text = models.TextField()
	default_strength = models.CharField(max_length=2, choices=STRENGTH_CHOICES)
	allowed_strength_change = models.BooleanField()
	pathogenic_question = models.BooleanField()


	def strength_options(self):

		if self.allowed_strength_change == False:

			return default_strength

		else:

			if self.pathogenic_question == True:

				return ['ST', 'MO', 'PP']

			else:

				return ['ST' 'PP']



class ClassificationAnswer(models.Model):

	STRENGTH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'),
	 ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ),
	 ('BA', 'STAND_ALONE'))

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


class Evidence(models.Model):
	"""
	Model to hold files that relate to evidence e.g. pdfs, screenshots.
	Must be associated with a comment.
	"""
	file = models.FileField(upload_to='uploads/%y/%m/', null=True, blank=True)
	comment = models.ForeignKey(UserComment, on_delete=models.CASCADE)




