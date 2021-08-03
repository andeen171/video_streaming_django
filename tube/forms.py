from django import forms


class UploadForm(forms.Form):
    video = forms.FileField(label='Select a video')
    title = forms.CharField(label='Title')
    tags = forms.CharField(label='Point tags')


class SearchForm(forms.Form):
    q = forms.CharField(label='Search')
