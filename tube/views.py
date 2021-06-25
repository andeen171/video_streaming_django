from django.shortcuts import render, redirect
from django.views import View
from .models import Video, VideoTag, Tag
from .forms import UploadForm


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