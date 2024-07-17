# resource/forms.py
from django import forms

from preference.models import Organisation
from django.contrib.auth.models import Group
from users.utils import get_user_organisations
from .models import OtherResource

class OtherResourceForm(forms.ModelForm):
    class Meta:
        model = OtherResource
        fields = ['title', 'description', 'link', 'group']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Expect user to be passed in kwargs
        super(OtherResourceForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = Group.objects.all()
            print("FORM FIELDS:", self.fields)

class EditResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditResourceForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['link'].widget.attrs.update({'class': 'form-control'})
        self.fields['group'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = OtherResource
        fields = ['title', 'description', 'link', 'group']
