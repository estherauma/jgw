from pathlib import Path

import markdown
from django.http import Http404
from django.utils.safestring import mark_safe


DOCS_ROOT = Path(__file__).resolve().parent / "content"
DOC_SECTIONS = {
    "user-management": {
        "title": "User Management",
    },
}

DOC_PAGES = {
    ("user-management", "overview"): {
        "title": "Overview",
        "path": DOCS_ROOT / "user-management" / "overview.md",
    },
    ("user-management", "roles-and-permissions"): {
        "title": "Roles and Permissions",
        "path": DOCS_ROOT / "user-management" / "roles-and-permissions.md",
    },
    ("user-management", "organisation-workflow"): {
        "title": "Organisation Workflow",
        "path": DOCS_ROOT / "user-management" / "organisation-workflow.md",
    },
    ("user-management", "entity-relationships"): {
        "title": "Entity Relationships",
        "path": DOCS_ROOT / "user-management" / "entity-relationships.md",
    },
    ("user-management", "qa-guide"): {
        "title": "QA Guide",
        "path": DOCS_ROOT / "user-management" / "qa-guide.md",
    },
}


class DocsService:
    @staticmethod
    def get_docs_navigation():
        navigation = []
        for (section_slug, page_slug), config in DOC_PAGES.items():
            navigation.append(
                {
                    "section_slug": section_slug,
                    "page_slug": page_slug,
                    "title": config["title"],
                    "url_name": "docs:page",
                }
            )
        return navigation

    @classmethod
    def render_markdown_file(cls, path):
        if not path.exists():
            raise Http404("Documentation page not found.")

        content = path.read_text(encoding="utf-8")
        html = markdown.markdown(
            content,
            extensions=["fenced_code", "tables", "toc"],
        )
        return mark_safe(html)

    @classmethod
    def get_page_context(cls, *, section_slug, page_slug):
        config = DOC_PAGES.get((section_slug, page_slug))
        section_config = DOC_SECTIONS.get(section_slug)

        if not config or not section_config:
            raise Http404("Documentation page not found.")

        return {
            "docs_pages": cls.get_docs_navigation(),
            "doc_title": config["title"],
            "doc_section_title": section_config["title"],
            "doc_html": cls.render_markdown_file(config["path"]),
            "active_doc": (section_slug, page_slug),
        }
