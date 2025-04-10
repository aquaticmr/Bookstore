# bookstore_project/urls.py

from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bookstore.urls')), # Include bookstore app's URLs here
    # NO 'from . import views' needed in *this* file
]