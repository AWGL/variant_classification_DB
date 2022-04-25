from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone

from acmg_db.models import *

#--------------------------------------------------------------------------------------------------
@transaction.atomic
def signup(request):
	"""
	Allow users to sign up
	User accounts are inactive by default - an admin must activate it using the admin page.

	"""

	if request.method == 'POST':

		form = UserCreationForm(request.POST)

		if form.is_valid():

			form.save()
			
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			user.is_active = False
			user.save()

			return redirect('home')

		else:

			form = UserCreationForm()
			return render(request, 'acmg_db/signup.html', {'form': form, 'warning' : ['Could not create an account.']})

	else:

		form = UserCreationForm()
		return render(request, 'acmg_db/signup.html', {'form': form, 'warning': []})


#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def about(request):
	"""
	The about page. Displays information about the application.
	"""

	return render(request, 'acmg_db/about.html', {})

#--------------------------------------------------------------------------------------------------
@transaction.atomic
@login_required
def ajax_delete_comment(request):
	"""
	View to allow users to delete comments.

	"""

	if request.is_ajax():

		comment_pk = request.POST.get('comment_pk').strip()
		comment = get_object_or_404(UserComment, pk =comment_pk)

		classification_pk = request.POST.get('classification_pk').strip()
		classification = get_object_or_404(Classification, pk =classification_pk)

		# only the user who created the comment can delete
		if request.user == comment.user:

			# only allow if classification is not complete
			if classification.status == '0' or classification.status == '1':

				comment.delete()

				comments = UserComment.objects.filter(classification=classification, visible=True)

				html = render_to_string('acmg_db/ajax_comments.html',
										{'comments': comments, 'user': request.user})

				return HttpResponse(html)

		else:

				comments = UserComment.objects.filter(classification=classification, visible=True)

				html = render_to_string('acmg_db/ajax_comments.html',
										{'comments': comments, 'user': request.user})

				return HttpResponse(html)



	else:

			raise PermissionDenied('You do not have permission to delete this comment.')



@transaction.atomic
@login_required
def artefact_check(request, pk):
	"""
	Allow arbitrary users to perform artefact checks
	"""

	classifications = Classification.objects.filter(analysis_id=pk)

	if request.method == 'POST':

		post_params = request.POST.dict()

		del post_params['csrfmiddlewaretoken']

		for key in post_params:

			genuine_status = request.POST[key]

			classification_obj = Classification.objects.get(pk=key)

			previous_classifications = Classification.objects.filter(variant=classification_obj.variant,variant__genome=classification_obj.variant.genome, status__in=['2', '3']).exclude(pk=classification_obj.pk).order_by('-second_check_date')

			# only update if no user assigned and first check
			if classification_obj.status == '0' and classification_obj.user_first_checker is None:

				if genuine_status == 'Artefact':

					classification_obj.genuine = '4'
					classification_obj.artefact_checker = request.user
					classification_obj.artefact_check_date = timezone.now()
					classification_obj.status = '1'
					classification_obj.first_final_class = '6'
					classification_obj.user_first_checker = request.user
					classification_obj.first_check_date = timezone.now() 

					classification_obj.save()

				elif genuine_status == 'Genuine - New Classification':

					classification_obj.genuine = '1'
					classification_obj.artefact_checker = request.user
					classification_obj.artefact_check_date = timezone.now()

					# initiate classification 
					classification_obj.initiate_classification()


					classification_obj.save()


				elif genuine_status == 'Genuine - Use Previous Classification':

					# if there isnt a previous classification, throw a warning and stop
					if len(previous_classifications) == 0:

						print('No classification to use for previous')
						# if there is, update final class to whatever it was previously
					else:

						classification_obj.genuine = '2'
						classification_obj.artefact_checker = request.user
						classification_obj.artefact_check_date = timezone.now()
						classification_obj.status = '1'

						classification_obj.first_final_class = previous_full_classifications[0].second_final_class

						classification_obj.save()				
				


	return render(request, 'acmg_db/artefact_check.html', {'classifications':classifications})