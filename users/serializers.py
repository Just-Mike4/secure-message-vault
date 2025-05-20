from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import AccessToken
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email= serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    username = serializers.CharField(required=True)


    class Meta:
        model = User
        fields = ["username","email", "password"]

    def create(self, validated_data):
        user = User.objects.create(
            username= validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.filter(email=email).first()
    
        if user :
            user = authenticate(request=self.context.get('request'), username=user.username, password=password)
        else:
            raise serializers.ValidationError('Invalid login credentials')
    
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        access = AccessToken.for_user(user)
        return {
            'access': str(access),
             'user': {
                'name': f"{user.username.title()}", 
                'email': user.email,
            }
        }


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        request = self.context.get('request')
        user = User.objects.get(email=self.validated_data['email'])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = str(AccessToken.for_user(user))
        reset_link = request.build_absolute_uri(
            reverse('password-reset-confirm', kwargs={'uid': uid, 'token': token})
        )

        send_mail(
            'Password Reset Request',
            f"""
            Dear {user.username},
        
            We received a request to reset your password for your account associated with this email address. If you did not request this, please ignore this email. No changes have been made to your account.
        
            To reset your password, please click the link below or copy and paste it into your browser:
        
            http://127.0.0.1:8000/password_reset/{uid}/{token}
        
            This link will expire in 1 hour.
        
            If you have any questions, feel free to contact our support team.
        
            Best regards,
            The Simple Message Vault Team
            """,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, attrs): 
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID")
        
        token = attrs['token']
        try:
            AccessToken(token)
        except Exception:
            raise serializers.ValidationError("Invalid token")
        
        return attrs

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uid']))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()