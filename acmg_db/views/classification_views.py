from ..forms import ArchiveClassificationForm, ResetClassificationForm, AssignSecondCheckToMeForm
from ..models import *

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

	"""

	classifications = Classification.objects.filter(status__in=['0', '1']).order_by('-creation_date')

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


	else:

		# Otherwise just get the information for display
		classification_answers = (ClassificationAnswer.objects.filter(classification=classification)
			.order_by('classification_question__order'))

		comments = UserComment.objects.filter(classification=classification, visible=True)

		archive_form = ArchiveClassificationForm(classification_pk = classification.pk)
		reset_form = ResetClassificationForm(classification_pk = classification.pk)
		assign_form = AssignSecondCheckToMeForm(classification_pk = classification.pk)

		return render(request, 'acmg_db/view_classification.html', {'classification': classification,
									 'classification_answers': classification_answers,
									 'comments': comments,
									 'archive_form': archive_form,
									 'reset_form': reset_form,
									 'assign_form': assign_form})
