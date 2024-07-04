# resource/forms.py
from django import forms

from preference.models import Organisation
from users.utils import get_user_organisations
from .models import OtherResource

class OtherResourceForm(forms.ModelForm):
    class Meta:
        model = OtherResource
        fields = ['title', 'description', 'link', 'organisation']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Expect user to be passed in kwargs
        super(OtherResourceForm, self).__init__(*args, **kwargs)
        if user:
            user_organisations = get_user_organisations(user)
            self.fields['organisation'].queryset = Organisation.objects.filter(id__in=user_organisations)
            print("FORM FIELDS:", self.fields)

class EditResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditResourceForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        self.fields['link'].widget.attrs.update({'class': 'form-control'})
        self.fields['organisation'].widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = OtherResource
        fields = ['title', 'description', 'link', 'organisation']
