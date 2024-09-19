# views.py
import stripe
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking, Transaction
from account.models import DoctorProfile, CustomUser

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentView(viewsets.ViewSet):

    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        booking_id = request.data.get('booking_id')
        payment_method = request.data.get('payment_method', 'stripe')  # Get payment method
        booking = Booking.objects.get(id=booking_id)
        patient = request.user

        if booking.patient != patient:
            return Response({'error': 'You can only pay for your own booking.'}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(booking, 'transaction'):
            return Response({'error': 'A transaction already exists for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

        doctor = booking.doctor
        doctor_profile = DoctorProfile.objects.get(user=doctor)
        
        try:
            if payment_method == 'stripe':
                # Create Stripe Checkout Session
                frontend_base_url = "http://localhost:5173"
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': f"Consultation with {doctor.username}",
                            },
                            'unit_amount': int(doctor_profile.fee * 100),  # Convert fee to cents
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f'http://localhost:5173/patient/payment-success?session_id={{CHECKOUT_SESSION_ID}}&booking_id={booking.id}',
                    cancel_url='http://localhost:5173/patient/payment-cancel',
                    metadata={
                        'booking_id': booking.id,
                    }
                )

                # Create a pending transaction linked to this booking
                transaction = Transaction.objects.create(
                    patient=patient,
                    doctor=doctor,
                    booking=booking,
                    amount=doctor_profile.fee,
                    status='pending',
                    stripe_charge_id=None
                )
                print(f"Transaction created with ID: {transaction.id}, status: {transaction.status}")
                return Response({'sessionId': session.id}, status=status.HTTP_200_OK)
            
            elif payment_method == 'wallet':
                if patient.wallet_balance >= doctor_profile.fee:
                    # Deduct from wallet
                    patient.wallet_balance -= doctor_profile.fee
                    patient.save()

                    # Create a successful transaction record
                    transaction = Transaction.objects.create(
                        patient=patient,
                        doctor=doctor,
                        booking=booking,
                        amount=doctor_profile.fee,
                        status='success',
                        stripe_charge_id=None  # No Stripe charge ID for wallet payments
                    )

                    booking.paid = True
                    booking.status = 'confirmed'
                    booking.save()

                    # Update doctor's wallet
                    doctor_profile = booking.doctor
                    doctor_profile.wallet_balance += transaction.amount
                    doctor_profile.save()
                    # doctor_profile.wallet_balance += doctor_profile.fee
                    # doctor_profile.save()

                    return Response({'message': 'Payment successful using wallet'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'error': 'Invalid payment method'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def payment_success(self, request):
        session_id = request.query_params.get('session_id')
        booking_id = request.query_params.get('booking_id')
        
        if not session_id or not booking_id:
            return Response({'error': 'Session ID or Booking ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the checkout session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

            if payment_intent.status == 'succeeded':
                booking = Booking.objects.get(id=booking_id)
                
                booking.paid = True
                booking.status = 'confirmed'  
                booking.save()
                
                transaction = booking.transaction
                transaction.status = 'success'
                transaction.stripe_charge_id = payment_intent.id
                transaction.save()

                # Update doctor's wallet
                doctor_profile = booking.doctor
                doctor_profile.wallet_balance += transaction.amount
                doctor_profile.save()

                return Response({'message': 'Payment successful and booking confirmed'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Payment not successful'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def payment_cancel(self, request):
        return Response({'message': 'Payment was canceled by the user.'}, status=status.HTTP_200_OK)
