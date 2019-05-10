from ..models import *

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import render, redirect

# GLOBAL VARIABLES
# list of all panels to populate dropdown lists
PANEL_OPTIONS = [(str(panel.pk), panel) for panel in Panel.objects.all().order_by('panel')]


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
