from django.core.management.base import BaseCommand

from content.services.partner_configurations import (
    sync_partner_config_options,
)


class Command(BaseCommand):
    help = "Sync partner configuration options from CMS."

    def handle(self, *args, **options):
        self.stdout.write("Syncing partner configuration options from CMS...")
        summary = sync_partner_config_options()

        if summary is None:
            self.stderr.write(
                self.style.ERROR(
                    "Failed to sync partner configuration options. Check STRAPI_API_BASE_URL and STRAPI_API_TOKEN."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "Locales sync complete: "
                f"created={summary['locale_sync']['created']}, "
                f"updated={summary['locale_sync']['updated']}, "
                f"skipped={summary['locale_sync']['skipped']}."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Work sectors sync complete: "
                f"created={summary['work_sector_sync']['created']}, "
                f"updated={summary['work_sector_sync']['updated']}, "
                f"skipped={summary['work_sector_sync']['skipped']}."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Collections sync complete: "
                f"created={summary['collection_sync']['created']}, "
                f"updated={summary['collection_sync']['updated']}, "
                f"skipped={summary['collection_sync']['skipped']}."
            )
        )
