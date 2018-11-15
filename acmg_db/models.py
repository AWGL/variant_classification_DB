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
	transcript = models.ForeignKey(Transcript,on_delete=models.CASCADE)
	hgvs_c = models.TextField()



class Classification(models.Model):

	"""
	Class to hold results of ACMG classification


	"""

	PATH_CHOICES = (('VS', 'VERY_STRONG'),('ST', 'STRONG'), ('MO', 'MODERATE'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	BENIGN_CHOICES = (('BA', 'STAND_ALONE'), ('ST', 'STRONG'), ('PP', 'SUPPORTING', ), ('NA', 'NA'))
	STATUS_CHOICES = (('0', 'NONE'), ('1', 'Awaiting Second Check'), ('2', 'Complete'))
	SAMPLE_TYPE_CHOICES = (('G', 'Germline'), ('S', 'Somatic'))

	variant = models.ForeignKey(Variant,on_delete=models.CASCADE)
	creation_date = models.DateTimeField(null=True, blank=True)
	second_check_date = models.DateTimeField(null=True, blank=True)
	user_creator = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='user_creator')
	user_second_checker = models.ForeignKey('auth.User', null=True, blank=True, on_delete=models.CASCADE, related_name='user_second_checker')
	status = models.CharField(max_length=1, choices =STATUS_CHOICES, default='0')
	acmg_class = models.CharField(max_length=25, null=True, blank=True)
	final_class = models.CharField(max_length=25, null=True, blank=True)
	sample = models.CharField(max_length=25, null =True, blank=True)
	sample_type = models.CharField(max_length=1, choices=SAMPLE_TYPE_CHOICES, null=True, blank=True)
	sample_comment = models.TextField(null=True, blank=True)


	PVS1 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PS1 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PS1 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PS3 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PS4 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM1 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM2 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM3 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM4 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM5 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PM6 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PP1 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PP2 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PP3 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PP4 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')
	PP5 = models.CharField(max_length=2, choices=PATH_CHOICES, default='NA')


	BA1 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BS1 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BS2 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BS3 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BS4 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP1 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP2 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP3 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP4 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP5 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP6 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')
	BP7 = models.CharField(max_length=2, choices=BENIGN_CHOICES, default='NA')



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




