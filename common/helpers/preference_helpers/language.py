def normalize_laguage_name(language: str):
    patterns_to_replace = {
        "burma": "burmese",
        "unknown language [qc]": "mandarin",
        "unknown language [hq]": "indonesian",
        "unknown language [qm]": "malay",
        "unknown language [qf]": "filipino",
    }
    normalize_gender = patterns_to_replace.get(language.lower() if language else language, language)

    return normalize_gender


def non_translatable_languages():
    return ["hindi"]
