from core.forms import GenericFilterForm


class EventsDataFilterForm(GenericFilterForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
