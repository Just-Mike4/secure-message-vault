from .serializers import RegisterSerializer, LoginSerializer,PasswordResetConfirmSerializer,PasswordResetSerializer
from rest_framework import viewsets, permissions, status,generics
from rest_framework.response import Response

class RegistrationView(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('post')
    
    def create(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Registeration successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginView(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('post')

    def create(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.create(serializer.validated_data)
            return Response(token, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset link sent"}, status=status.HTTP_200_OK)

class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uid, token, *args, **kwargs):
        data = {
            'uid': uid,
            'token': token,
            'new_password': request.data.get('new_password')
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset"}, status=status.HTTP_200_OK)