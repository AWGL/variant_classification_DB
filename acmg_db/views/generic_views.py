from ..models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse


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