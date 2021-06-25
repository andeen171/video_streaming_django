from django.urls import path
from .views import Index, Upload, Viewer

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('upload/', Upload.as_view(), name='upload'),
    path('<file_name>/', Viewer.as_view(), name='view'),
]