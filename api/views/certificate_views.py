from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from api.permissions import IsAdmin
from api.models import Certificate, User, Course
from api.services import supabase
from django.conf import settings
from django.shortcuts import get_object_or_404
from urllib.parse import urlparse
import time
import uuid
from django.http import JsonResponse

class CerificateListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdmin]

    def post(self, request):

        file = request.FILES.get('certificate_image')

        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        unique_filename = f"{int(time.time())}_{uuid.uuid4().hex[:8]}_{file.name}"
        file_path = f"certificates/{unique_filename}"  # File path in Supabase bucket
        file_content = file.read()

        user = get_object_or_404(User, id=request.data.get("user"))  # Retrieves the User instance

        # You may also want to fetch the course or other related objects
        course = get_object_or_404(Course, id=request.data.get("course"))

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

            certificate = Certificate(
                user=user,  # Assuming user is provided in the request data
                course=course,  # Assuming course is provided in the request data
                certificate_url=file_url,
                status="issued"  # Default status to "issued"
            )
            certificate.save()

            return JsonResponse({
                "id": certificate.id,
                "user": certificate.user.id,
                "course": certificate.course.id,
                "certificate_url": certificate.certificate_url,
                "status": certificate.status
            }, safe=False, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllCertificate(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        authenticated_user = request.user

        if not authenticated_user:
            return Response({"error": "No user"}, status=status.HTTP_401_UNAUTHORIZED)
        
        certificates = Certificate.objects.filter(user=authenticated_user)
        
        # Prepare the response data manually
        certificate_data = []
        for certificate in certificates:
            certificate_data.append({
                'id': certificate.id,
                'course': certificate.course.courseName,  # Adjust if needed to retrieve course info
                'status': certificate.status,  # Added status field here
                'certificate_url': certificate.certificate_url,
            })
        
        # Return the response as JSON with status code 200
        return JsonResponse(certificate_data, safe=False, status=status.HTTP_200_OK)  # Explicitly setting status to 200
