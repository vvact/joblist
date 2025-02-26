from rest_framework import serializers
from django.contrib.auth import get_user_model

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse




User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name"]
 #Registration       
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "password", "confirm_password"]

    def validate(self, data):
        """Ensure password and confirm_password match"""
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")  # Remove confirm_password before saving
        user = User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            password=validated_data["password"]
        )
        return user
    
#login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    
    def validate(self, data):
        """Authenticate user"""
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        
        tokens = RefreshToken.for_user(user)  # Generate tokens
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "access_token": str(tokens.access_token),
            "refresh_token": str(tokens)
        }
    
#Logout
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, data):
        """Blacklist the refresh token"""
        try:
            refresh = RefreshToken(data["refresh_token"])
            refresh.blacklist()  # Blacklist the token
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token.")
        return data
    


    #Reset Password
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("User with this email does not exist.")

        # Generate password reset token
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = f"http://127.0.0.1:8000/api/users/reset-password-confirm/{user.id}/{token}/"

        # Send password reset email
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_url}",
            "noreply@example.com",
            [email],
            fail_silently=False,
        )

        return {"message": "Password reset link sent to your email."}


#Reset Password Confirmation
class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def save(self, user):
        user.set_password(self.validated_data["password"])
        user.save()
