from django.urls import path
from .views import Create_List_profile
urlpatterns = [
    path('patient-profiles/', Create_List_profile.as_view(), name='patient-profile-list-create'),
    
]