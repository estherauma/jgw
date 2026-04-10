import phonenumbers
import pycountry

def is_super_user(user):
    return not user.is_anonymous and user.is_superuser


def is_in_group(user, group_name):
    return not user.is_anonymous and user.groups.filter(name=group_name).exists()


def is_org_admin(user):
    if is_58_admin(user) or is_super_user(user):
        return False
    return is_in_group(user, "org_admin")

def is_org_staff(user):
    if is_58_admin(user) or is_super_user(user) or is_org_admin(user):
        return False
    return is_in_group(user, "org_staff")


def is_58_admin(user):
    if is_super_user(user):
        return False
    return is_in_group(user, "58_admin")


def is_super_or_58_admin(user):
    return is_super_user(user) or is_58_admin(user)

def is_org_admin_or_staff(user):
    return is_org_admin(user) or is_org_staff(user)

COUNTRY_CODE_CHOICES = None


def get_country_code_choices():
    global COUNTRY_CODE_CHOICES
    if COUNTRY_CODE_CHOICES is not None:
        return COUNTRY_CODE_CHOICES
    choices = []
    for region in sorted(phonenumbers.SUPPORTED_REGIONS):
        country = pycountry.countries.get(alpha_2=region)
        name = country.name if country else region
        code = phonenumbers.country_code_for_region(region)
        if not code:
            continue
        dial = f"+{code}"
        choices.append((region, f"({dial}) {name}"))
    choices.sort(key=lambda item: item[1].split(") ", 1)[-1].lower())
    COUNTRY_CODE_CHOICES = choices
    return choices


def validate_phone_number(phone_number, country_iso):
    if not phone_number:
        return None, "Enter a valid phone number."
    if not country_iso:
        return None, "Select a country code."
    iso_code = phonenumbers.country_code_for_region(country_iso)
    if not iso_code:
        return None, "Select a valid country code."
    raw_number = phone_number.strip()
    try:
        parsed = phonenumbers.parse(raw_number, country_iso)
    except phonenumbers.NumberParseException:
        return None, "Enter a valid phone number."
    if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
        return None, "Enter a valid phone number."
    return parsed, None
