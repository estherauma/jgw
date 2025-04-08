# Translations

See https://docs.djangoproject.com/en/5.1/topics/i18n/translation/ for how translations are managed in Django.

Key points:
 - Templates:
    ```
    {% load i18n %}
    <title>{% translate "This is the title." %}</title>
    ```

 - Python code:
    ```
    from django.utils.translation import gettext as _

    def my_view(request):
        output = _("Welcome to my site.")
        return HttpResponse(output)
    ```

## Generating the translation files

To generate the set of keys that need translations, run:

    ```
    python manage.py makemessages -l <LANGUAGE>
    ```

    eg.

    ```
    python manage.py makemessages -l es_MX
    ```

This will create .po files inside the relevant `locale` directory.

Then, once those are filled in (presumably via another script that pulls from the CMS),
run:
    ```
    python manage.py compilemessages