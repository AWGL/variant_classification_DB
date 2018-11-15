from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('classification/<int:pk>/', views.new_classification, name='new_classification'),
]