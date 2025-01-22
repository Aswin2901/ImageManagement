from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password
from .models import User

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
            print('user :',user)
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
                'email': user.email,
                'phone': getattr(user, 'phone', None),
                'full_name': getattr(user, 'full_name', None),
            }
        }

        return Response(response_data)