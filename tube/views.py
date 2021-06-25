from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from .models import Video, VideoTag, Tag
from .forms import UploadForm
from hypertube import settings


# Create your views here.
class Index(View):

    def get(self, request):

        query = request.GET.get('q')
        tag = request.GET.get('tag')

        if query:
            videos = Video.objects.filter(title__icontains=query)
        elif tag:
            video_tags = VideoTag.objects.filter(tag__name__iexact=tag)
            videos = set([tag.video for tag in video_tags])
        else:
            videos = Video.objects.all()

        context = {
            'tag': tag,
            'videos': videos,
            'user': request.user
        }
        return render(request, 'tube/index.html', context)


class Upload(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'tube/upload.html',
                      context={'form': UploadForm, 'user': request.user}
                      )

    def post(self, request, *args, **kwargs):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            title = request.POST['title']
            tags_arr = request.POST['tags'].split()
            tags = []
            for s in tags_arr:
                t = Tag()
                t.name = s
                t.save()
                tags.append(t)
            video_file = request.FILES['video']
            video_model = Video()
            video_model.title = title
            video_model.file = video_file
            video_model.save()
            for t in tags:
                video_tag = VideoTag()
                video_tag.tag = t
                video_tag.video = video_model
                video_tag.save()
        return redirect('/tube/')


class Viewer(View):

    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        video_tags = VideoTag.objects.filter(video=video)
        tags = set([video.tag for video in video_tags])
        context = {'video': video, 'tags': tags}
        return render(request, 'tube/view.html', context=context)


class FileViewer(View):

    def get(self, request, file_name):
        with open(settings.MEDIA_ROOT + file_name, 'rb') as vid:
            return HttpResponse(content=vid, content_type='video/mp4')
