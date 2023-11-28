# csv_upload_project/urls.py

from django.contrib import admin
from django.urls import path, include
from csv_upload import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('csv-upload/', include('csv_upload.urls')),
    path('select-hotel/', views.select_hotel, name='select_hotel'),
    path('select-location/', views.select_location, name='select_location'),
    path('hotel-detail/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('lcr_analysis/', views.lcr_analysis, name='lcr_analysis'),
    
]

