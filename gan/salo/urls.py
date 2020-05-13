from . import views
from django.urls import path

app_name = 'salo'
urlpatterns = [
    path('', views.salo, name='salo'),
]