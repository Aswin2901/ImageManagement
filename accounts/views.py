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
from rest_framework.decorators import api_view , parser_classes
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
import json

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=400)

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        print('email :' , email , password)

        # Check if the user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=400)

        # Validate the password
        if not check_password(password, user.password):
            return Response({'error': 'Invalid credentials'}, status=400)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Update the user's last login
        update_last_login(None, user)

        # Build the response
        response_data = {
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id':user.id,
                'email': user.email,
                'phone': getattr(user, 'phone', None),
                'full_name': getattr(user, 'full_name', None),
            }
        }

        return Response(response_data)
    
    
@api_view(['GET'])
def image_get_view(request , user_id):
    if request.method == 'GET':
        user = User.objects.get(id = user_id)
        images = ImageUpload.objects.filter(user=user).order_by('order')
        serializer = ImageUploadSerializer(images, many=True)
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def image_post_view(request, user_id):
    if request.method == 'POST':
        try:
            # Access files and titles from the request
            images = request.FILES.getlist('files')  # Fetch all uploaded files
            titles = request.POST.getlist('titles')  # Fetch all titles

            print('images:', images, 'titles:', titles)

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

            # Get the user instance
            user = User.objects.get(id=user_id)

            # Create ImageUpload objects
            uploaded_images = []
            for image_file, title in zip(images, titles):
                image = ImageUpload.objects.create(user=user, image=image_file, title=title)
                uploaded_images.append(image)

            # Serialize and return the uploaded images
            serializer = ImageUploadSerializer(uploaded_images, many=True)
            return JsonResponse(serializer.data, safe=False, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return JsonResponse(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
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
    
@api_view(['POST'])
def update_image_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = data.get("user_id")
            images = data.get("images", [])

            if not user_id or not images:
                return JsonResponse({"error": "Invalid data"}, status=400)

            for item in images:
                image_id = item.get("id")
                order = item.get("order")

                if image_id is not None and order is not None:
                    ImageUpload.objects.filter(id=image_id, user_id=user_id).update(order=order)

            return JsonResponse({"message": "Image order updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)