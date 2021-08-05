from django import forms


class UploadPhotoForm(forms.Form):
    image = forms.FileField(label='Select a profile picture')
