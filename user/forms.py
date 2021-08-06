from django import forms


class UploadPhotoForm(forms.Form):
    image = forms.FileField(label='Select a profile picture')


class EditVideoInfoForm(forms.Form):
    title = forms.CharField(label='Title')
    description = forms.CharField(label='Description')
