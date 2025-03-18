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
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
import time
import uuid

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
            unique_filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{file.name}"
            file_path = f"images/{unique_filename}"  # File path in Supabase bucket
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
    
class StorageChangeImage(APIView):
    def patch(self, request, pk):

        storage_item = get_object_or_404(Storage, pk=pk)  # Get the storage object by pk
        file = request.FILES.get('storage_image')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        old_image_url = storage_item.storage_image
        unique_filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{file.name}"
        file_path = f"images/{unique_filename}"  # File path in Supabase bucket
        file_content = file.read()

        try:
            # Upload file to Supabase
            res = supabase.storage.from_("AQKids").upload(
                file=file_content,
                path=file_path
            )

            # Get the public URL of the uploaded file
            file_url = supabase.storage.from_("AQKids").get_public_url(
                res.__getattribute__("path")
            )
            
            if old_image_url:
                parsed_url = urlparse(old_image_url)  # Parse URL to extract file path
                old_file_path = parsed_url.path.lstrip("/")  # Remove leading slash
                supabase.storage.from_("AQKids").remove([old_file_path])

            # Update storage object
            storage_item.storage_image = file_url
            storage_item.save()

            return Response({
                "id": storage_item.id,
                "title": storage_item.title,
                "storage_image": file_url,
                "quantity": storage_item.quantity
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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