from django import forms

from preference.models import SectorOfWork, SectorsOfWorkMapper


class SectorsOfWorkMapperForm(forms.ModelForm):
    class Meta:
        model = SectorsOfWorkMapper
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        already_existing_mappers = SectorsOfWorkMapper.objects.values_list(
            "sector__translated_name", flat=True
        )

        self.fields["sector"].queryset = SectorOfWork.objects.exclude(
            translated_name__in=already_existing_mappers
        ).distinct("translated_name")
