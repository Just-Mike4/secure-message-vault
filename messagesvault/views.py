from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import MessageVault
from .serializers import (
    MessageCreateSerializer, 
    MessageListSerializer,
    MessageUnlockSerializer
)
from django.contrib.auth.hashers import check_password
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from django.utils import timezone

class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageListSerializer

    def get_queryset(self):
        return MessageVault.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        message = get_object_or_404(MessageVault, pk=pk, created_by=request.user)
        serializer = MessageUnlockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check message status
        if message.self_destruct and message.has_been_viewed:
            return Response(
                {"detail": "Message has been destroyed"},
                status=status.HTTP_410_GONE
            )

        if message.unlock_after and message.unlock_after > timezone.now():
            return Response({
                "detail": f"Available after {message.unlock_after}"
            }, status=status.HTTP_423_LOCKED)

        # Handle decryption
        try:
            passphrase = serializer.validated_data.get('passphrase', '')
            if message.passphrase_hash:
                if not check_password(passphrase, message.passphrase_hash):
                    raise ValueError("Invalid passphrase")
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=message.salt,
                    iterations=480000,
                )
                key = base64.urlsafe_b64encode(
                    kdf.derive(passphrase.encode()))
            else:
                master_key = Fernet(base64.urlsafe_b64encode(
                    os.environ['MASTER_KEY'].encode()))
                key = master_key.decrypt(message.encrypted_key)

            fernet = Fernet(key)
            content = fernet.decrypt(message.encrypted_content).decode()

            if message.self_destruct:
                message.delete()
            else:
                message.has_been_viewed = True
                message.save()

            return Response({
                'title': message.title,
                'content': content
            })

        except (InvalidToken, ValueError) as e:
            return Response(
                {"detail": "Decryption failed - invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )