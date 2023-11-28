# csv_upload/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('select-columns/', views.select_columns, name='select_columns'),
    
]
