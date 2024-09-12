# views.py

import stripe
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Booking, Transaction
from account.models import DoctorProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentView(viewsets.ViewSet):
    
    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        booking_id = request.data.get('booking_id')
        booking = Booking.objects.get(id=booking_id)
        patient = request.user

        if booking.patient != patient:
            return Response({'error': 'You can only pay for your own booking.'}, status=status.HTTP_403_FORBIDDEN)

        if hasattr(booking, 'transaction'):
            return Response({'error': 'A transaction already exists for this booking.'}, status=status.HTTP_400_BAD_REQUEST)

        
        doctor = booking.doctor
        doctor_profile = DoctorProfile.objects.get(user=doctor)
        
        try:
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
                status='pending'
            )
            print(f"Transaction created with ID: {transaction.id}, status: {transaction.status}")
            return Response({'sessionId': session.id}, status=status.HTTP_200_OK)

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


    @action(detail=False, methods=['post'])
    def refund_payment(self, request):
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response({'error': 'Booking ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the booking and related transaction
            booking = Booking.objects.get(id=booking_id)
            transaction = booking.transaction
            
            if transaction.refund_status == 'refunded':
                return Response({'error': 'This transaction has already been refunded'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Refund the payment via Stripe
            stripe.Refund.create(
                charge=transaction.stripe_charge_id,
                amount=int(transaction.amount * 100)  # Convert amount to cents
            )

            # Update transaction as refunded
            transaction.refund_status = 'refunded'
            transaction.refund_amount = transaction.amount
            transaction.amount = 0.00
            transaction.save()

            # Update patient's wallet
            patient = transaction.patient
            patient.wallet_balance += transaction.refund_amount
            patient.save()

            # Update doctor's wallet
            doctor_profile = booking.doctor
            doctor_profile.wallet_balance -= transaction.refund_amount
            doctor_profile.save()

            return Response({'message': 'Refund processed successfully'}, status=status.HTTP_200_OK)
        
        except stripe.error.StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)