from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('', views.pending_classifications, name='home'), # change this to change home page

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='acmg_db/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='acmg_db/logout.html'), name='logout'),
    path('about/', views.about, name='about'),

    path('auto_input/', views.auto_input, name='auto_input'),
    path('manual_input/', views.manual_input, name='manual_input'),

    path('first_check/<int:pk>/', views.first_check, name='first_check'),
    path('ajax/acmg_classification_first/', views.ajax_acmg_classification_first, name='ajax_acmg_classification_first'),

    path('second_check/<int:pk>/', views.second_check, name='second_check'),
    path('ajax/acmg_classification_second/', views.ajax_acmg_classification_second, name='ajax_acmg_classification_second'),
    path('ajax/comments/', views.ajax_comments, name='ajax_comments'),

    path('pending_classifications', views.pending_classifications, name='pending_classifications'),   # list of all classifications
    path('view_classification/<int:pk>/', views.view_classification, name='view_classification'),                       # individual classifications
    path('reporting', views.reporting, name='reporting'),

    path('variants/', views.view_variants, name='view_variants'),           # all unique variants
    path('variant/<str:pk>/', views.view_variant, name='view_variant'),     # each instance of a variant

    path('panels/', views.panels, name='panels'),

    path('search/', views.search, name='search'),
    path('view_gene/<str:pk>/', views.view_gene, name='view_gene'),
    path('view_sample/<str:pk>/', views.view_sample, name='view_sample'),

    path('ajax/delete_comment/', views.ajax_delete_comment, name='ajax_delete_comment'),

]

