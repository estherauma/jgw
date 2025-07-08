
import os
import polib
from django.core.management.base import BaseCommand
from content.models import AggregatedContent

class Command(BaseCommand):
    help = 'Export CMS additionalText labels to .po files for English and Spanish'

    def handle(self, *args, **options):
        aggregated = AggregatedContent.objects.latest('created_at')
        if not aggregated:
            self.stdout.write(self.style.ERROR('No AggregatedContent found'))
            return

        content = aggregated.content

        translations = {
            'en-us': {},
            'es-es': {}
        }

        for lang_code, pages in content.items():
            if lang_code not in translations:
                continue 
            
            for page_key, page_data in pages.items():
                if not page_key.startswith('rweb'):
                    continue
                
                additional_text = page_data.get('additional_text', [])
                print(f"[DEBUG] additional_text = {additional_text}")

                if isinstance(additional_text, dict):
                    key = additional_text.get('key')
                    value = additional_text.get('value')
                    if key and value:
                        translations[lang_code][key] = value
                elif isinstance(additional_text, list):
                    for item in additional_text:
                        if isinstance(item, dict):
                            key = item.get('key')
                            value = item.get('value')
                            if key and value:
                                translations[lang_code][key] = value
                        else:
                            self.stdout.write(self.style.WARNING(f'Skipping invalid item in list: {item}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Unexpected additional_text format: {additional_text}'))


        self.update_po_file('en_US', translations['en-us'])
        self.update_po_file('es_ES', translations['es-es'])

        self.stdout.write(self.style.SUCCESS('CMS Labels Exported Successfully'))

    def update_po_file(self, language_code, translations):
        po_path = f'locale/{language_code}/LC_MESSAGES/django.po'

        if not os.path.exists(po_path):
            self.stdout.write(self.style.ERROR(f'{po_path} does not exist'))
            return

        po = polib.pofile(po_path)
        updated_keys = []
        for key, value in translations.items():
            entry = po.find(key)
            if entry:
                entry.msgstr = value
                updated_keys.append(key)

        if updated_keys:
            po.save(po_path)
            self.stdout.write(self.style.SUCCESS(f'Updated {len(updated_keys)} keys in {po_path}'))
        else:
            self.stdout.write(self.style.WARNING(f'No matching keys found in {po_path}. No changes made.'))
