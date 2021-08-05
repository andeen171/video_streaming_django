import mimetypes
import re
import os
from wsgiref.util import FileWrapper
from django.http import StreamingHttpResponse
from django.core.exceptions import ValidationError
from django.views.generic.list import ListView
from django.db.models import Q
from django.views import View
from django.shortcuts import render, redirect, HttpResponse
from .models import Video, VideoTag, Tag, Comment
from .forms import UploadForm, SearchForm, CommentForm
from hypertube import settings
import ffmpeg
import sys


# Create your views here.
class Index(ListView):
    template_name = 'tube/index.html'
    form_class = SearchForm
    paginate_by = 3
    context_object_name = 'data'
    model = Video

    def get_queryset(self):
        query = self.request.GET.get('q')
        tag = self.request.GET.get('tag')
        if query:
            # annotate(rank=SearchRank(SearchVector('views'), SearchQuery(query))).order_by('-rank')
            return Video.objects.filter(Q(title__icontains=query))
        elif tag:
            video_tags = VideoTag.objects.filter(Q(tag__name__iexact=tag))
            return list([tag.video for tag in video_tags])
        else:
            return self.model.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', None)
        context['tag'] = self.request.GET.get('tag', None)
        context['videoqnt'] = Video.objects.all().count()
        return context


class Upload(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'tube/upload.html',
                      context={'form': UploadForm, 'user': request.user}
                      )

    def post(self, request, *args, **kwargs):
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                video_file = request.FILES['video']
            except ValidationError:
                return redirect('/tube/upload')
            else:
                title = request.POST['title']
                description = request.POST['description']
                tags_arr = request.POST['tags'].split()
                tags = []
                for s in tags_arr:
                    t = Tag()
                    t.name = s
                    t.save()
                    tags.append(t)

                video_model = Video()
                video_model.title = title
                video_model.file = video_file
                video_model.description = description
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
        video.views += 1
        video.save()
        video_tags = VideoTag.objects.filter(video=video)
        tags = set([video.tag for video in video_tags])
        comments = Comment.objects.filter(video=video)
        form = CommentForm
        context = {'video': video, 'tags': tags, 'form': form, 'comments': comments}
        return render(request, 'tube/view.html', context=context)

    def post(self, request, video_id):
        form = CommentForm(request.POST)
        if form.is_valid():
            content = request.POST['comment']
            comment = Comment()
            comment.text = content
            comment.author = request.user
            video = Video.objects.get(id=video_id)
            comment.video = video
            comment.save()
        return redirect(f'/tube/watch/{video_id}')


class FileViewer(View):

    def file_iterator(self, file_name, chunk_size=8192, offset=0, length=None):
        with open(settings.MEDIA_ROOT + file_name, "rb") as f:
            f.seek(offset, os.SEEK_SET)
            remaining = length
            while True:
                bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
                data = f.read(bytes_length)
                if not data:
                    break
                if remaining:
                    remaining -= len(data)
                yield data

    def get(self, request, file_name):
        """ Forma que eu achei para streamar o video por httpresponse,
         enquanto eu não implemento um proxy nginx """
        path = file_name
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
        range_match = range_re.match(range_header)
        size = os.path.getsize(settings.MEDIA_ROOT + path)
        content_type, encoding = mimetypes.guess_type(path)
        content_type = content_type or 'application/octet-stream'
        if range_match:
            first_byte, last_byte = range_match.groups()
            first_byte = int(first_byte) if first_byte else 0
            last_byte = first_byte + 1024 * 1024 * 8  # 8M per piece, the maximum volume of the response body
            if last_byte >= size:
                last_byte = size - 1
            length = last_byte - first_byte + 1
            resp = StreamingHttpResponse(self.file_iterator(path, offset=first_byte, length=length), status=206,
                                         content_type=content_type)
            resp['Content-Length'] = str(length)
            resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)

        else:
            # When the video stream is not obtained, the entire file is returned in the generator mode to save memory.
            resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
            resp['Content-Length'] = str(size)
        resp['Accept-Ranges'] = 'bytes'
        return resp


class ThumbViewer(View):

    def get(self, request, file_name):
        file = file_name.replace('.mp4', '.png')
        with open(settings.MEDIA_ROOT + file, 'rb') as thumb:
            return HttpResponse(content=thumb, content_type='image/png')


def generate_thumbnail(in_filename, video_model):
    file_name = Video.objects.get(id=video_model.id).file.name
    print(file_name)
    path = settings.MEDIA_ROOT + 'thumb' + file_name.replace('.mp4', '.png').replace(' ', '_')
    print(path)
    try:
        (
            ffmpeg.input(settings.MEDIA_ROOT + in_filename.name, ss='00:00:05')
                  .output(path, vframes=1)
                  .overwrite_output()
                  .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)
