from django import forms

from preference.models import SectorOfWork, SectorsOfWorkMapper


class SectorsOfWorkMapperForm(forms.ModelForm):
    class Meta:
        model = SectorsOfWorkMapper
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sectors_of_work = SectorsOfWorkMapper.objects.all()

        existing_sectors_list = [sector_of_work.mapper.lower() for sector_of_work in sectors_of_work]

        self.fields["sectors"].queryset = SectorOfWork.objects.exclude(
            translated_name__in=existing_sectors_list
        ).distinct("translated_name")
