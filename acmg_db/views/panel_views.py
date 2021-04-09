from acmg_db.forms import NewPanelForm
from acmg_db.models import *

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render

@transaction.atomic
@login_required
def panels(request):
	"""
	Page to view panels and add new panels. All panels are stored in lowercase
	"""
	# get list of all panels
	panels = Panel.objects.all().order_by('panel')

	# make empty form
	form = NewPanelForm()
	context = {'panels': panels, 'form': form}

	# if form submitted
	if request.method == 'POST':
		form = NewPanelForm(request.POST)

		if form.is_valid():
			# throw error if panel already exists
			try:
				new_panel = Panel.objects.get(panel = form.cleaned_data['panel_name'].lower())
				context['warn'] = ['Panel already exists']

			# add the panel if it doesnt
			except Panel.DoesNotExist:
				new_panel = Panel.objects.create(
					panel = form.cleaned_data['panel_name'].lower(),
					added_by = request.user
				)

	return render(request, 'acmg_db/panels.html', context)
