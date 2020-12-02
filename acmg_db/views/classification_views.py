from acmg_db.forms import ArchiveClassificationForm, ResetClassificationForm, AssignSecondCheckToMeForm, SendBackToFirstCheckForm
from acmg_db.models import *

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def pending_classifications(request):
	"""
	Page to view classifications that havent yet been completed

	Use select_related to perform SQL join for all data we need, so that we only hit the database 
	once - https://docs.djangoproject.com/en/3.0/ref/models/querysets/#select-related
	"""

	classifications = Classification.objects.filter(
			status__in=['0', '1']
		).select_related(
			'sample__analysis_performed', 'sample__worklist', 
			'selected_transcript_variant__transcript',
			'selected_transcript_variant__transcript__gene',
			'variant', 'user_first_checker', 'user_second_checker'
		).order_by(
			'-creation_date'
		)

	return render(request, 'acmg_db/pending_classifications.html', {'classifications': classifications})


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def view_classification(request, pk):
	"""
	View a read only version of a classification of a variant

	"""

	classification = get_object_or_404(Classification, pk=pk)

	# Allow users to archive the classification
	if request.method == 'POST':

		if 'submit-archive' in request.POST:

			if classification.status == '2':

				form = ArchiveClassificationForm(request.POST, classification_pk = classification.pk)

				if form.is_valid():

					# Update status to archived
					cleaned_data = form.cleaned_data
					classification.status = '3'
					classification.save()
					return redirect('home')

			else:

				raise PermissionDenied('You do not have permission to archive the classification.')

		# Allow users to reset a classification
		elif 'submit-reset' in request.POST:

			# Only allow user to reset if status is first or second analysis
			if classification.status == '0' or classification.status == '1':

				form = ResetClassificationForm(request.POST, classification_pk = classification.pk)

				if form.is_valid():

					classification = get_object_or_404(Classification, pk=form.classification_pk)

					classification.first_check_date = None
					classification.second_check_date = None
					classification.user_first_checker = None
					classification.user_second_checker = None
					classification.status = '0'
					classification.genuine = '0'
					classification.first_final_class = '7'
					classification.second_final_class = '7'
					classification.save()

					comments = UserComment.objects.filter(classification=classification)
					comments.delete()

					answers = ClassificationAnswer.objects.filter(classification=classification)
					answers.delete()

					return redirect('home')

			else:

				raise PermissionDenied('You do not have permission to reset the classification.')

		# Allow users to assign the second check to themselves
		elif 'submit-assign' in request.POST:

			# Only allow user to reset if status is first or second analysis
			if classification.status == '1' and classification.user_second_checker != request.user:

				form = AssignSecondCheckToMeForm(request.POST, classification_pk = classification.pk)

				if form.is_valid():

					classification = get_object_or_404(Classification, pk=form.classification_pk)

					classification.user_second_checker = request.user
					classification.save()

					return redirect('home')

			else:

				raise PermissionDenied('You do not have permission to assign the second check to yourself.')	


		# Allow users to assign the second check to themselves
		elif 'submit-sendback' in request.POST:

			# Only allow user to reset if status is second check and the user is None, the first checker or 2nd checker
			if classification.status == '1' and (classification.user_second_checker == request.user or classification.user_first_checker == request.user):

				form = SendBackToFirstCheckForm(request.POST, classification_pk = classification.pk)

				if form.is_valid():

					classification = get_object_or_404(Classification, pk=form.classification_pk)

					# delete any second check answers
					classification_answers = ClassificationAnswer.objects.filter(classification=classification)

					for c_answer in classification_answers:

						c_answer.selected_second = False
						c_answer.strength_second = c_answer.classification_question.default_strength
						c_answer.save()

					# delete any second check comments
					classification_comments = UserComment.objects.filter(classification =classification, user= classification.user_second_checker)
					classification_comments.delete()

					# reset other attributes
					classification.first_check_date = None
					classification.second_check_date = None
					classification.user_second_checker = None
					classification.status = '0'
					classification.second_final_class = '7'
					classification.save()

					return redirect('home')

			else:

				raise PermissionDenied('You do not have permission to assign the second check to yourself.')	


	else:

		# Otherwise just get the information for display
		classification_answers = (ClassificationAnswer.objects.filter(classification=classification)
			.order_by('classification_question__order'))

		# make dictionaries for summary of codes applied
		full_strength_dict = {
			'PV':{'PVS1': 'not applied'}, 
			'PS':{'PS1': 'not applied', 'PS2': 'not applied', 'PS3': 'not applied', 'PS4': 'not applied'}, 
			'PM':{'PM1': 'not applied', 'PM2': 'not applied', 'PM3': 'not applied',
			      'PM4': 'not applied', 'PM5': 'not applied', 'PM6': 'not applied'}, 
			'PP':{'PP1': 'not applied', 'PP2': 'not applied', 'PP3': 'not applied', 'PP4': 'not applied'}, 
			'BP':{'BP1': 'not applied', 'BP2': 'not applied', 'BP3': 'not applied', 
				  'BP4': 'not applied', 'BP5': 'not applied', 'BP7': 'not applied'}, 
			'BS':{'BS1': 'not applied', 'BS2': 'not applied', 'BS3': 'not applied', 'BS4': 'not applied', }, 
			'BA':{'BA1': 'not applied'}
			}
		altered_strength_dict = {'PV':[], 'PS':[], 'PM':[], 'PP':[], 'BP':[], 'BS':[], 'BA':[]}
		strength_count_dict = {'PV':0, 'PS':0, 'PM':0, 'PP':0, 'BP':0, 'BS':0, 'BA':0}

		# loop through answers and edit dictionaries to show classification - currently based on second check
		for a in classification_answers:
			if classification.status == '0':
				if a.selected_first:
					# if code is applied, parse required fields
					code = a.classification_question.acmg_code
					default = a.classification_question.default_strength
					set_strength = a.strength_first

					# if strength isnt changed
					if set_strength == default:
						# special handling for PS4_M/P becuase they are seperate rules in the database
						if code == 'PS4_M':
							full_strength_dict['PS']['PS4'] = 'altered'
							altered_strength_dict['PM'].append('PS4_M')
						elif code == 'PS4_P':
							full_strength_dict['PS']['PS4'] = 'altered'
							altered_strength_dict['PP'].append('PS4_P')
						else:
							full_strength_dict[default][code] = 'applied'
						strength_count_dict[set_strength] += 1
					else:
						# if strength is changed make new code ID
						if set_strength == 'BA':
							new_code = f'{code}_{set_strength}'
						elif set_strength == 'PV':
							new_code = f'{code}_VS'
						else:
							new_code = f'{code}_{set_strength[1]}'
						full_strength_dict[default][code] = 'altered'
						altered_strength_dict[set_strength].append(new_code)
						strength_count_dict[set_strength] += 1
			else:
				if a.selected_second:
					# if code is applied, parse required fields
					code = a.classification_question.acmg_code
					default = a.classification_question.default_strength
					set_strength = a.strength_second

					# if strength isnt changed
					if set_strength == default:
						# special handling for PS4_M/P becuase they are seperate rules in the database
						if code == 'PS4_M':
							full_strength_dict['PS']['PS4'] = 'altered'
							altered_strength_dict['PM'].append('PS4_M')
						elif code == 'PS4_P':
							full_strength_dict['PS']['PS4'] = 'altered'
							altered_strength_dict['PP'].append('PS4_P')
						else:
							full_strength_dict[default][code] = 'applied'
						strength_count_dict[set_strength] += 1
					else:
						# if strength is changed make new code ID
						if set_strength == 'BA':
							new_code = f'{code}_{set_strength}'
						elif set_strength == 'PV':
							new_code = f'{code}_VS'
						else:
							new_code = f'{code}_{set_strength[1]}'
						full_strength_dict[default][code] = 'altered'
						altered_strength_dict[set_strength].append(new_code)
						strength_count_dict[set_strength] += 1


		comments = UserComment.objects.filter(classification=classification, visible=True)
		classification_history = classification.history.all()
		sample_history = classification.sample.history.all()
		history = (classification_history | sample_history).order_by('-timestamp')

		archive_form = ArchiveClassificationForm(classification_pk = classification.pk)
		reset_form = ResetClassificationForm(classification_pk = classification.pk)
		assign_form = AssignSecondCheckToMeForm(classification_pk = classification.pk)
		sendback_form = SendBackToFirstCheckForm(classification_pk = classification.pk)

		return render(request, 'acmg_db/view_classification.html', 
			{	
				'classification': classification,
				'classification_answers': classification_answers,
				'classes_full_strength': full_strength_dict,
				'classes_altered_strength': altered_strength_dict,
				'classes_count': strength_count_dict,
				'comments': comments,
				'archive_form': archive_form,
				'reset_form': reset_form,
				'assign_form': assign_form,
				'sendback_form': sendback_form,
				'history': history
			}
		)
