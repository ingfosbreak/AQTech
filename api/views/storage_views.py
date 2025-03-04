from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import Storage
from api.serializers import StorageSerializer
# from api.serializers.storage_serializers import StorageSerializer
from api.services import supabase
from django.conf import settings

class StorageListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request):
        storages = Storage.objects.all()
        serializer = StorageSerializer(storages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):

        file = request.FILES.get('storage_image', None)
        
        # Handle file upload if a file is present
        if file:
            file_path = f"images/{file.name}"  # File path in Supabase bucket
            file_content = file.read()
            try:
                # Upload to Supabase
                res = supabase.storage.from_("AQKids").upload(
                    file=file_content,
                    path=file_path
                )

                # Get public URL of uploaded file
                file_url = supabase.storage.from_("AQKids").get_public_url(
                    res.__getattribute__("path")
                )

                request.data['storage_image'] = file_url  # Save URL in request data

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

        serializer = StorageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StorageDetailView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({"error": "Storage not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StorageSerializer(storage)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({"error": "Storage not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = StorageSerializer(storage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            storage = Storage.objects.get(pk=pk)
        except Storage.DoesNotExist:
            return Response({"error": "Storage not found"}, status=status.HTTP_404_NOT_FOUND)

        storage.delete()
        return Response({"message": "Storage deleted successfully"}, status=status.HTTP_204_NO_CONTENT)