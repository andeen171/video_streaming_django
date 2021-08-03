from django import forms


class UploadForm(forms.Form):
    video = forms.FileField(label='Select a video')
    title = forms.CharField(label='Title', max_length=255)
    tags = forms.CharField(label='Point tags', max_length=255)
    description = forms.CharField(label='Description, max_length=1024')


class SearchForm(forms.Form):
    q = forms.CharField(label='Search')


class CommentForm(forms.Form):
    comment = forms.CharField(label='Comment')
