from django.urls import path
from .views import ProfileView, PfpView

urlpatterns = [
    path('profile/<int:userid>/', ProfileView.as_view(), name='profile'),
    path('profile/pfps/<pfpname>/', PfpView.as_view(), name='pfp'),
]
