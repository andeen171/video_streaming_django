from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from .models import Video, VideoTag, Tag
from .forms import UploadForm
from hypertube import settings
import ffmpeg
import sys


# Create your views here.
class Index(View):

    def get(self, request):

        query = request.GET.get('q')
        tag = request.GET.get('tag')

        if query:
            videos = Video.objects.filter(title__icontains=query)[:15]
        elif tag:
            video_tags = VideoTag.objects.filter(tag__name__iexact=tag)[:15]
            videos = set([tag.video for tag in video_tags])
        else:
            videos = Video.objects.all()[:15]

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
            video_model.author = request.user
            video_model.save()
            for t in tags:
                video_tag = VideoTag()
                video_tag.tag = t
                video_tag.video = video_model
                video_tag.save()
            generate_thumbnail(video_file, video_model)
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


class ThumbViewer(View):

    def get(self, request, file_name):
        file = file_name.replace('.mp4', '.png')
        with open(settings.MEDIA_ROOT + file, 'rb') as thumb:
            return HttpResponse(content=thumb, content_type='image/png')


def generate_thumbnail(in_filename, video_model):
    file_name = Video.objects.get(id=video_model.id).file.name
    print(file_name)
    path = settings.MEDIA_ROOT + 'thumb' + file_name.replace('.mp4', '').replace(' ', '_') + '.png'
    print(path)
    try:
        (
            ffmpeg.input(in_filename.temporary_file_path(), ss='00:00:05')
                  .output(path, vframes=1)
                  .overwrite_output()
                  .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)
