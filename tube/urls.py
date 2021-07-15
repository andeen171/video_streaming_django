from django.urls import path
from .views import Index, Upload, Viewer, FileViewer, ThumbViewer

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('watch/<int:video_id>/', Viewer.as_view(), name='viewer'),
    path('upload/', Upload.as_view(), name='upload'),
    path('file/<file_name>/', FileViewer.as_view(), name='view'),
    path('thumb/<file_name>/', ThumbViewer.as_view(), name='thumb')
]
