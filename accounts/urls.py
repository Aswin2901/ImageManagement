from django.contrib import admin
from django.urls import path
from accounts.views import RegisterView, CustomLoginView , image_get_view , image_post_view , Edit_view , delete_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('image_get/<int:user_id>/', image_get_view, name='image-get'),
    path('image_post/<int:user_id>/', image_post_view, name='image-upload'),
    path('images_edit/<int:pk>/', Edit_view, name='image-edit'),
    path('images_delete/<int:pk>/', delete_view, name='image-delete'),
]
