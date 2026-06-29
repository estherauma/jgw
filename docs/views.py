from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import DocsService


class DocsPageView(LoginRequiredMixin, TemplateView):
    template_name = "docs/page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            DocsService.get_page_context(
                section_slug=self.kwargs["section_slug"],
                page_slug=self.kwargs["page_slug"],
            )
        )
        return context
