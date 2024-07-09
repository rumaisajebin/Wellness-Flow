from urllib import response
from rest_framework import generics,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from account.models import CustomUser
from account.serializers import UserSerializer, TokenSerializer, DoctorProfileSerializer, PatientProfileSerializer

class Token(TokenObtainPairView):
    serializer_class = TokenSerializer

class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        user = self.request.user
        if user.role == 'doctor':
            return DoctorProfileSerializer
        elif user.role == 'patient':
            return PatientProfileSerializer
        return UserSerializer

    def get_object(self):
        user = self.request.user
        if user.role == 'doctor':
            return user.doctor_profile
        elif user.role == 'patient':
            return user.patient_profile
        return user

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response(serializer.data, status=status.HTTP_200_OK)