from django.views.generic.list import ListView
from tube.models import Video
from django.contrib.auth.models import User
from django.views import View
from django.db.models import Q
from hypertube import settings
from django.shortcuts import HttpResponse, redirect
from .forms import UploadPhotoForm, EditVideoInfoForm


class ProfileView(ListView):
    template_name = 'user/profile.html'
    paginate_by = 3
    context_object_name = 'data'
    model = Video

    def get_queryset(self):
        user_id = self.kwargs['userid']
        user = User.objects.get(pk=user_id)
        videos = Video.objects.filter(Q(author=user))
        return videos

    def get_context_data(self, *, object_list=None, **kwargs):
        user_id = self.kwargs['userid']
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = User.objects.get(id=user_id)
        context['photoform'] = UploadPhotoForm
        context['editform'] = EditVideoInfoForm
        context['name'] = user.username
        context['profile'] = user.profile
        return context

    def post(self, request, userid, *args):
        image = request.FILES['image']
        user = User.objects.get(pk=userid)
        user.profile.pfp = image
        user.save()
        return redirect(f'/user/profile/{userid}')


class PfpView(View):

    def get(self, request, pfpname):
        with open(settings.MEDIA_ROOT + 'pfps/' + pfpname, 'rb') as pfp:
            return HttpResponse(content=pfp, content_type='image/jpeg*')
