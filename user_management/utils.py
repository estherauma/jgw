import phonenumbers
import pycountry
from django.core.exceptions import ValidationError

from users.models import User


ROLE_PRECEDENCE = (
    ("super_user", None),
    ("58_admin", "58_admin"),
    ("org_group_admin", "org_group_admin"),
    ("org_admin", "org_admin"),
    ("org_staff", "org_staff"),
)

def is_super_user(user):
    return not user.is_anonymous and user.is_superuser


def is_in_group(user, group_name):
    return not user.is_anonymous and user.groups.filter(name=group_name).exists()


def get_group_names(user):
    if user.is_anonymous:
        return set()
    return {group.name for group in user.groups.all()}


def get_active_role_from_group_names(group_names, is_superuser=False):
    if is_superuser:
        return "super_user"
    group_names = set(group_names)
    for role_name, group_name in ROLE_PRECEDENCE[1:]:
        if group_name in group_names:
            return role_name
    return "none"


def get_active_role(user):
    return get_active_role_from_group_names(
        get_group_names(user),
        is_superuser=is_super_user(user),
    )


def is_org_admin(user):
    return get_active_role(user) == "org_admin"

def is_org_group_admin(user):
    return get_active_role(user) == "org_group_admin"

def is_org_or_group_admin(user):
    return is_org_admin(user) or is_org_group_admin(user)

def is_org_staff(user):
    return get_active_role(user) == "org_staff"


def is_58_admin(user):
    return get_active_role(user) == "58_admin"


def is_super_or_58_admin(user):
    return is_super_user(user) or is_58_admin(user)

def is_org_admin_or_staff(user):
    return is_org_or_group_admin(user) or is_org_staff(user)

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


def normalize_phone_number_for_lookup(phone_number, country_iso=None):
    raw_number = (phone_number or "").strip()
    normalized_country_iso = (country_iso or "").strip().upper()
    if not raw_number:
        return None, None

    if raw_number.startswith("+"):
        try:
            parsed = phonenumbers.parse(raw_number, None)
        except phonenumbers.NumberParseException:
            return None, "Enter a valid phone number."
        if not phonenumbers.is_possible_number(parsed) or not phonenumbers.is_valid_number(parsed):
            return None, "Enter a valid phone number."
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), None

    if not normalized_country_iso:
        return None, "Select a country code."

    parsed, error_message = validate_phone_number(raw_number, normalized_country_iso)
    if error_message:
        return None, error_message
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164), None


def clean_user_email(email, instance=None, required=False):
    normalized_email = (email or "").strip().lower()
    if not normalized_email:
        if required:
            raise ValidationError("Email is required")
        return None

    qs = User.all_objects.filter(email__iexact=normalized_email)
    if instance and instance.pk:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise ValidationError("Email already exists.")
    return normalized_email


def validate_password_confirmation(
    form,
    cleaned_data,
    password_field="password",
    confirmation_field="password_confirm",
):
    password = cleaned_data.get(password_field)
    confirmation = cleaned_data.get(confirmation_field)
    if (password or confirmation) and password != confirmation:
        form.add_error(confirmation_field, "Passwords do not match.")


def validate_user_phone_number(
    form,
    cleaned_data,
    phone_field="phone_number",
    country_field="phone_country_iso",
):
    phone_number = (cleaned_data.get(phone_field) or "").strip()
    country_iso = (cleaned_data.get(country_field) or "").strip()
    if not phone_number:
        cleaned_data[country_field] = None
        return cleaned_data

    if not country_iso:
        form.add_error(country_field, "Select a country code.")
        return cleaned_data

    parsed, error_message = validate_phone_number(phone_number, country_iso)
    if error_message:
        if "country code" in error_message:
            form.add_error(country_field, error_message)
        else:
            form.add_error(phone_field, error_message)
        return cleaned_data

    cleaned_data[phone_field] = phonenumbers.format_number(
        parsed, phonenumbers.PhoneNumberFormat.E164
    )
    phone_qs = User.all_objects.filter(
        phone_number=cleaned_data[phone_field],
        phone_country_iso=country_iso,
    )
    if form.instance and form.instance.pk:
        phone_qs = phone_qs.exclude(pk=form.instance.pk)
    if phone_qs.exists():
        form.add_error(
            phone_field,
            "Phone number already exists for the selected country.",
        )
    return cleaned_data
