# serializers.py
from rest_framework import serializers
from .models import MessageVault
from django.utils import timezone
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.contrib.auth.hashers import make_password

class MessageCreateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(write_only=True)
    passphrase = serializers.CharField(
        write_only=True, 
        required=False, 
        allow_blank=True
    )
    unlock_after= serializers.DateTimeField(
        required=True,
        format="%Y-%m-%d %H:%M:%S", 
    )
    
    class Meta:
        model = MessageVault
        fields = [
            'title', 'content', 'passphrase', 
            'unlock_after', 'self_destruct'
        ]

    def validate_unlock_after(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "Unlock time must be in the future."
            )
        return value

    def create(self, validated_data):
        content = validated_data.pop('content')
        passphrase = validated_data.pop('passphrase', None)
        user = self.context['request'].user
        
        # Generate encryption components
        salt = os.urandom(16)
        encrypted_content, passphrase_hash, encrypted_key = \
            self._encrypt_content(content, passphrase, salt)

        return MessageVault.objects.create(
            encrypted_content=encrypted_content,
            passphrase_hash=passphrase_hash,
            salt=salt,
            encrypted_key=encrypted_key,
            created_by=user,
            **validated_data
        )

    def _encrypt_content(self, content, passphrase, salt):
        if passphrase:
            # Passphrase-based encryption
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = base64.urlsafe_b64encode(
                kdf.derive(passphrase.encode())
            )
            fernet = Fernet(key)
            encrypted_content = fernet.encrypt(content.encode())
            return encrypted_content, make_password(passphrase), None
        else:
            # System-key encryption
            key = Fernet.generate_key()
            fernet = Fernet(key)
            encrypted_content = fernet.encrypt(content.encode())
            master_key = Fernet(base64.urlsafe_b64encode(
                os.environ['MASTER_KEY'].encode()))
            encrypted_key = master_key.encrypt(key)
            return encrypted_content, '', encrypted_key

class MessageListSerializer(serializers.ModelSerializer):
    message_url = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = MessageVault
        fields = ['id', 'title', 'message_url', 'created_at']

    def get_message_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/messages/{obj.id}/unlock/")
        return f"/api/messages/{obj.id}/unlock/"

class MessageUnlockSerializer(serializers.Serializer):
    passphrase = serializers.CharField(
        required=False, 
        allow_blank=True,
        write_only=True
    )
    content = serializers.CharField(read_only=True)
    title = serializers.CharField(read_only=True)