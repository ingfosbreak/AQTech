import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreatePaymentIntentView(APIView):
    def post(self, request):
        try:
            data = request.data
            amount = data.get("amount")  # Amount in cents
            currency = data.get("currency", "thb")  # Default to THB
            date = datetime.strptime(data.get("date"), "%Y-%m-%dT%H:%M:%S.%fZ").date()
            metadata = {
                "student_id": data.get("student_id"),  # Store student ID
                "course_id": data.get("course_id"),  # Store purchased course
                "date": date,
            }

            # Create PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_configuration="pmc_1R1AzmDCJUREqBVa83HoBBaA",
                metadata=metadata,
            )

            return Response({"client_secret": intent.client_secret}, status=status.HTTP_200_OK)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookAPIView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        print(sig_header)
        print(endpoint_secret)
        # print("Headers:", request.META)
        # print("Payload:", payload)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            print(e)
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            print(e)
            return HttpResponse(status=400)
        
        if event["type"] == "payment_intent.succeeded":
            session = event["data"]["object"]
            metadata = session.get("metadata", {})  # Get metadata from Stripe session              
            print("Payment was successful.")
            print("Metadata:", metadata)

        return Response(status=status.HTTP_200_OK)