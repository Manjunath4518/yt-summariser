from django import forms

class YtForm(forms.Form):
    Link = forms.CharField(label="Enter Youtube video link")