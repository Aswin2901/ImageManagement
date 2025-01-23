from rest_framework import serializers
from .models import User , ImageUpload

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Password confirmation check
        password = validated_data['password']
        confirm_password = validated_data['password']  # Assuming `confirm_password` is part of the same input
        
        if password != confirm_password:
            raise serializers.ValidationError({'non_field_errors': 'Passwords do not match'})
        
        user = User(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id', 'image', 'title', 'created_at', 'updated_at']