from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='home'),
    path('classification/<int:pk>/', views.new_classification, name='new_classification'),
    path('ajax/acmg_classification/', views.ajax_acmg_classification, name='ajax_acmg_classification'),
    path('ajax/comments/', views.ajax_comments, name='ajax_comments'),
    path('login/', auth_views.LoginView.as_view(template_name="acmg_db/login.html"), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="acmg_db/logout.html"), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)