from django.contrib import admin
from django.urls import path
from accounts.views import RegisterView, CustomLoginView , ImageEditDeleteView , image_get_view , image_post_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('image_get/<int:user_id>/', image_get_view, name='image-get'),
    path('image_post/<int:user_id>/', image_post_view, name='image-upload'),
    path('images/<int:pk>/', ImageEditDeleteView.as_view(), name='image-edit-delete'),
]
