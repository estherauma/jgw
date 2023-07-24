from langcodes import Language, LanguageTagError


def get_language_name(entry):
    try:
        code = Language.get(entry).language_name()
    except LanguageTagError:
        try:
            code = Language.find(entry).language_name()
        except (LookupError, AttributeError):
            code = entry
    except AttributeError:
        code = entry
    return code