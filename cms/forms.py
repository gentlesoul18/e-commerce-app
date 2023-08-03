from django import forms
import cloudinary.uploader
from .models import UploadImage

class UploadForm(forms.Form):
    file = forms.FileField()


class ProductImageUploadForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple':True}))

    class Meta:
        model = UploadImage
        fields = ( 'images',)

    