from django.urls import path
from .views import Index, Upload, Viewer, FileViewer, ThumbViewer, DeleteVideoView, EditVideoInfoView

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('watch/<int:video_id>/', Viewer.as_view(), name='viewer'),
    path('upload/', Upload.as_view(), name='upload'),
    path('file/<file_name>/', FileViewer.as_view(), name='view'),
    path('thumb/<file_name>/', ThumbViewer.as_view(), name='thumb'),
    path('delete/<int:video_id>/', DeleteVideoView.as_view(), name='delete'),
    path('edit/<int:video_id>/', EditVideoInfoView.as_view(), name='update'),
]
