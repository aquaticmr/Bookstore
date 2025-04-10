# bookstore/urls.py

from django.urls import path
from . import views # Import views from the current directory (the bookstore app)

urlpatterns = [
    path('', views.book_list, name='book_list'), # Show book list on root of app
    path('login/', views.login_view, name='login'),
    # Note: Logout should ideally be a POST request for security
    # We link to it via a form in the template
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:book_id>/', views.remove_from_cart, name='remove_from_cart'), # Optional remove URL
]