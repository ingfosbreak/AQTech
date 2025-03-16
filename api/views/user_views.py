from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated
from api.models import User
# from api.serializers.user_serializers import UserSerializer
from api.serializers import UserSerializer
from api.serializers.user_serializers import ProfileSerializer
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

class UserDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.prefetch_related("students").get(id=user_id)  # Optimize query
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data)
# user = get_object_or_404(User, pk=pk)