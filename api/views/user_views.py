from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import User
# from api.serializers.user_serializers import UserSerializer
from api.serializers import UserSerializer
# from django.shortcuts import get_object_or_404


class StaffUserView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserUpdateView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def patch(self, request):
        authenticated_user = request.user
        serializer = UserSerializer(authenticated_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        authenticated_user = request.user
       
        return Response({
            "username": authenticated_user.username,
            "role": authenticated_user.role,  
        })

class VerifyTokenView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)

class UserListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# user = get_object_or_404(User, pk=pk)