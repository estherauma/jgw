import os
import polib
from django.core.management.base import BaseCommand
from content.models import AggregatedContent
from collections import defaultdict

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

                for item in additional_text:
                    key = item.get('key')
                    value = item.get('value')

                    if not key or not value:
                        continue

                    translations[lang_code][key] = value

        self.update_po_file('en_US', translations['en-us'])
        self.update_po_file('es_ES', translations['es-es'])

        self.stdout.write(self.style.SUCCESS('CMS Labels Exported Successfully'))

    def update_po_file(self, language_code, translations):
        po_path = f'locale/{language_code}/LC_MESSAGES/django.po'

        if not os.path.exists(po_path):
            self.stdout.write(self.style.ERROR(f'{po_path} does not exist'))
            return

        po = polib.pofile(po_path)
        
        # Detect duplicates
        duplicates = self.find_duplicates(po)
        if duplicates:
            self.stdout.write(self.style.WARNING(f'Duplicate msgids found in {po_path}:'))
            for msgid, entries in duplicates.items():
                self.stdout.write(f'  "{msgid}" appears {len(entries)} times at lines: {[e.linenum for e in entries]}')

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
        print_keys_without_translation = self.print_keys_without_translation(po, language_code)
        print(f"[DEBUG] keys_without_translation = {print_keys_without_translation}")

    def find_duplicates(self, po):
        msgid_map = defaultdict(list)
        for entry in po:
            msgid_map[entry.msgid].append(entry)
        return {msgid: entries for msgid, entries in msgid_map.items() if len(entries) > 1}

    def print_keys_without_translation(self, po, language_code):
        untranslated_keys = [entry.msgid for entry in po if not entry.msgstr]
        if untranslated_keys:
            self.stdout.write(self.style.WARNING(f'The following {len(untranslated_keys)} keys are missing translations in {language_code}:'))
            for key in untranslated_keys:
                self.stdout.write(f'  {key}')
        else:
            self.stdout.write(self.style.SUCCESS(f'All keys have translations in {language_code}'))
