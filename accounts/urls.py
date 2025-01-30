from django.contrib import admin
from . import views
from django.urls import path
from accounts.views import RegisterView, CustomLoginView , image_get_view , image_post_view , Edit_view , delete_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('image_get/', image_get_view, name='image-get'),
    path('image_post/', image_post_view, name='image-upload'),
    path('images_edit/<int:pk>/', Edit_view, name='image-edit'),
    path('images_delete/<int:pk>/', delete_view, name='image-delete'),
    path("update_order/", views.update_image_order, name="update_image_order"),
    path('user_details/', views.user_details, name='user_details'),
    path('change_password/', views.change_password, name='change_password'),
]
