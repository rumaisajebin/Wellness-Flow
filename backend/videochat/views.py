# # views.py

from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets
from twilio.jwt.access_token import AccessToken # type: ignore
from twilio.jwt.access_token.grants import VideoGrant # type: ignore
from twilio.rest import Client # type: ignore
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.http import JsonResponse
from appoinment.models import Booking, DoctorSchedule
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework import status
from .utils import send_email

class VideoTokenViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='generate_token')
    def generate_token(self, request):
        # Fetch Twilio credentials from settings
        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_api_key_sid = settings.TWILIO_API_KEY
        twilio_api_key_secret = settings.TWILIO_API_SECRET

        # Use the authenticated user's username as identity
        identity = request.user.username

        # Strip extra spaces from the booking ID
        booking_id = request.query_params.get('booking_id', '').strip()
        if not booking_id:
            return Response({"detail": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise NotFound("Booking not found or you are not authorized.")

        # Check if the booking is paid and confirmed
        if booking.status != 'confirmed' or not booking.paid:
            raise PermissionDenied("The booking must be paid and confirmed before joining the call.")

        # Create an Access Token
        token = AccessToken(
            twilio_account_sid, twilio_api_key_sid, twilio_api_key_secret, identity=identity
        )

        # Grant access to Twilio Video
        video_grant = VideoGrant(room=f"Room{booking_id}")
        token.add_grant(video_grant)

        # Serialize the token as a JWT
        jwt_token = token.to_jwt()

        # Generate the video room link
        video_room_link = self._generate_video_link(booking_id, jwt_token)
        print(f"Generated video room link: {video_room_link}")  # Debug statement
        print(f"Generated token: {jwt_token}")
        # Share the token as a link with the patient
        self._send_token_email(booking, video_room_link)

        return Response({"token": jwt_token})

    def _generate_video_link(self, booking_id, token):
        """
        Generate a URL link for the video call room with the token.
        """
        # Assuming the frontend handles video calls at this URL
        base_url = "http://localhost:5173/videocall"
        
        # No need to decode the token as it's already a string
        video_link = f"{base_url}?room_id=Room-{booking_id}&token={token}"
        return video_link


    def _send_token_email(self, booking, video_link):
        """
        Helper function to send the video link email to the patient.
        """
        # Prepare email details
        subject = "Join Your Video Call"
        message = (
            f"Hello {booking.patient.username},\n\n"
            f"Please use the following link to join your video call with your doctor: {video_link}\n\n"
            f"Best regards,\nYour Clinic"
        )
        html_message = (
            f"<p>Hello {booking.patient.username},</p>"
            f"<p>Please use the following link to join your video call with your doctor:</p>"
            f"<p><a href='{video_link}' target='_blank'>Join Video Call</a></p>"
            f"<p>Best regards,<br>Your Clinic</p>"
        )

      

        # Send the email with the video link
        send_email(booking.patient.email, subject, message, html_message)

    @action(detail=False, methods=['post'], url_path='share_token')
    def share_token(self, request):
        booking_id = request.data.get('booking_id')
        if not booking_id:
            return Response({"detail": "Booking ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            raise NotFound("Booking not found or you are not authorized.")

        if booking.doctor != request.user:
            raise PermissionDenied("You are not authorized to share the token.")

        # Directly call the generate_token method to create a token
        token_response = self.generate_token(request)  # Call the token generation method
        if token_response.status_code != status.HTTP_200_OK:
            return token_response

        token = token_response.data['token']  # Extract the token from the response

        # Generate the video room link
        video_room_link = self._generate_video_link(booking_id, token)

        # Call the helper method to share the link via email
        self._send_token_email(booking, video_room_link)

        return Response({"detail": "Token shared with patient successfully."})
