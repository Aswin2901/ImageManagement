from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer , ImageUploadSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from .models import User , ImageUpload
from rest_framework import status
from rest_framework.decorators import api_view , parser_classes , permission_classes
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
import json
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt


User = get_user_model()

# 🔹 Register View (with JWT tokens)
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": getattr(user, 'full_name', None),
                    "phone": getattr(user, 'phone', None),
                }
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔹 Login View (JWT-based authentication)
class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password
        if not check_password(password, user.password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update last login time
        update_last_login(None, user)

        return Response({
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': getattr(user, 'full_name', None),
                'phone': getattr(user, 'phone', None),
            }
        }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def image_get_view(request):
    try:
        user = request.user  
        images = ImageUpload.objects.filter(user=user).order_by('order')
        serializer = ImageUploadSerializer(images, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure user is authenticated
def image_post_view(request):
    if request.method == 'POST':
        try:
            # Get the logged-in user from the token
            user = request.user

            # Access files and titles from the request
            images = request.FILES.getlist('files')  
            titles = request.POST.getlist('titles')  

            if not images or not titles:
                return JsonResponse(
                    {"error": "Images and titles are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(images) != len(titles):
                return JsonResponse(
                    {"error": "Number of images and titles must match."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create ImageUpload objects
            uploaded_images = []
            for image_file, title in zip(images, titles):
                image = ImageUpload.objects.create(user=user, image=image_file, title=title)
                uploaded_images.append(image)

            # Serialize and return the uploaded images
            serializer = ImageUploadSerializer(uploaded_images, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)

        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return JsonResponse({"error": "Invalid request method."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def Edit_view(request, pk):
    try:
        image = ImageUpload.objects.get(pk=pk)
    except ImageUpload.DoesNotExist:
        return Response({"error": "Image not found."}, status=404)

    serializer = ImageUploadSerializer(image, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
def delete_view(request, pk):
    print('into')
    try:
        # Retrieve the image by its primary key
        image = ImageUpload.objects.get(pk=pk)
        print('image : ' , image)

        # Delete the image
        image.delete()
        return Response({"message": "Image deleted successfully."}, status=200)

    except ImageUpload.DoesNotExist:
        return Response({"error": "Image not found."}, status=404)

    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=500)
    
@csrf_exempt
@api_view(['POST'])
def update_image_order(request):
    try:
        data = json.loads(request.body)
        user_id = request.user.id
        images = data.get("images", [])

        if not user_id or not images:
            return JsonResponse({"error": "Invalid data"}, status=400)

        image_instances = []
        for item in images:
            image_id = item.get("id")
            order = item.get("order")

            if image_id is not None and order is not None:
                image_instances.append(ImageUpload(id=image_id, user_id=user_id, order=order))

        if image_instances:
            with transaction.atomic():  # Ensures all updates are done in a single transaction
                ImageUpload.objects.bulk_update(image_instances, ['order'])

        return JsonResponse({"message": "Image order updated successfully"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def user_details(request):
    user = request.user
    return Response({
        'name': user.full_name,
        'email': user.email,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def change_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')

    # Check if old password is correct
    if not check_password(old_password, user.password):
        return JsonResponse({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate new password (You can add more password validation here)
    if len(new_password) < 8:
        return JsonResponse({'error': 'New password must be at least 8 characters'}, status=status.HTTP_400_BAD_REQUEST)

    # Update password
    user.password = make_password(new_password)
    user.save()

    return JsonResponse({'message': 'Password updated successfully'})