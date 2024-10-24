from rest_framework import serializers
from account.models import CustomUser,DoctorProfile,PatientProfile, Notification
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth import authenticate



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password', 'is_active', 'is_verify']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Print the email received from the frontend
        print("Email received from frontend:", validated_data.get('email'))

        user = CustomUser.objects.create_user(**validated_data)

        token_generator = default_token_generator
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        verification_url = f"https://rareblu.shop/account/verify_account/{uid}/{token}"
        subject = "Verify your email"
        message = f"Please verify your email by clicking this link: {verification_url}"
        recipient_list = [user.email]

        # Print the verification URL and recipient list before sending the email
        print("Verification URL:", verification_url)
        print("Email recipient:", recipient_list)

        # Send email
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)

        # Log if email is sent
        print("Email sent to:", user.email)

        return user


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = DoctorProfile
        fields = '__all__'

class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = PatientProfile
        fields = '__all__'

class TokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        
        if user is None:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        
        if not user.is_active:
            raise serializers.ValidationError({"detail": "Account is inactive."})
        
        if not user.is_superuser and not user.is_verify:
            raise serializers.ValidationError({"detail": "Email is not verified. Please check your email."})
        
        data = super().validate(attrs)
        data.update({'role': self.user.role})
        data.update({'profile_id': self.user.role})

        if self.user.role == 'doctor':
            try:
                profile_complete = self.user.doctor_profile.is_complete()
                
            except DoctorProfile.DoesNotExist:
                profile_complete = False
                
        elif self.user.role == 'patient':
            try:
                profile_complete = self.user.patient_profile.is_complete()
                
            except PatientProfile.DoesNotExist:
                profile_complete = False
                
        else:
            profile_complete = False

        data.update({'profile_complete': profile_complete})
        return data
    
    
    

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
