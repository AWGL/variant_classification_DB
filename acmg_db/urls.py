from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as rest_views

from acmg_db import views


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

    path('download_variant_list/', views.download_variant_list, name='download_variant_list'),


    path('search/', views.search, name='search'),
    path('view_gene/<str:pk>/', views.view_gene, name='view_gene'),
    path('view_sample/<str:pk>/', views.view_sample, name='view_sample'),

    path('ajax/delete_comment/', views.ajax_delete_comment, name='ajax_delete_comment'),


    path('api-token-auth/', rest_views.obtain_auth_token),
    path('api-add-variants/', views.AddVariantsForAnalysis.as_view(), name='add-variants'),
    
    path('cnv_home/', views.cnv_home, name = 'cnv_home'),
    path('cnv_pending/', views.cnv_pending, name = 'cnv_pending'),
    path('cnv_manual/', views.cnv_manual, name = 'cnv_manual'),
    path('cnv_first_check/<int:pk>/', views.cnv_first_check, name = 'cnv_first_check'),
    path('cnv_second_check/<int:pk>/', views.cnv_second_check, name = 'cnv_second_check'),
    path('ajax/acmg_cnv_classification_first/', views.ajax_acmg_cnv_classification_first, name='ajax_acmg_cnv_classification_first'),
    path('ajax/acmg_cnv_classification_second/', views.ajax_acmg_cnv_classification_second, name='ajax_acmg_cnv_classification_second'),
    path('ajax/cnv_comments/', views.ajax_cnv_comments, name='ajax_cnv_comments'),
    path('ajax/cnv_delete_comment/', views.ajax_cnv_delete_comment, name='ajax_cnv_delete_comment'),
    path('view_cnvs/', views.view_cnvs, name='view_cnvs'),
    path('cnv_view_classification/<int:pk>/', views.cnv_view_classification, name='cnv_view_classification'),
    path('cnv_reporting/', views.cnv_reporting, name='cnv_reporting'),
    path('cnv_search',views.cnv_search, name='cnv_search'),
    path('cnv_view_sample/<str:pk>/',views.cnv_view_sample, name='cnv_view_sample'),
    path('view_cnv/<str:pk>/', views.view_cnv, name='view_cnv'),
    path('cnv_view_gene/<str:pk>/', views.cnv_view_gene, name='cnv_view_gene'),
    path('download_cnv_list/', views.download_cnv_list, name='download_cnv_list'),
    path('ajax/cnv_decipher_download/', views.ajax_cnv_decipher_download, name='ajax_cnv_decipher_download'),
    path('cnv_view_region/<str:pk>/', views.cnv_view_region, name='cnv_view_region'),
    
]
