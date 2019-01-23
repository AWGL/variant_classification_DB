from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('manual_input/', views.manual_input, name='manual_input'),
    path('classification/<int:pk>/', views.new_classification, name='new_classification'),
    path('view_classification/<int:pk>/', views.view_classification, name='view_classification'),
    path('second_check/<int:pk>/', views.second_check, name='second_check'),
    path('ajax/acmg_classification_first/', views.ajax_acmg_classification_first, name='ajax_acmg_classification_first'),
    path('ajax/acmg_classification_second/', views.ajax_acmg_classification_second, name='ajax_acmg_classification_second'),
    path('ajax/comments/', views.ajax_comments, name='ajax_comments'),
    path('view_previous_classifications', views.view_previous_classifications, name='view_previous_classifications'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='acmg_db/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='acmg_db/logout.html'), name='logout'),
    path('about/', views.about, name='about'),
    path('variants/', views.view_variants, name='view_variants'),
    path('variant//<str:pk>/', views.view_variant, name='view_variant'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)