from common.utils.date_utils import django_date_make_aware, string_to_date


def string_date_to_django_model_date(model_field):
    try:
        converted_datetime = string_to_date(model_field, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        converted_datetime = string_to_date(model_field, "%Y-%m-%d")
    
    return django_date_make_aware(converted_datetime)

def bulk_create_in_chunks(model, instances, chunk_size=1000):
    for i in range(0, len(instances), chunk_size):
        model.objects.bulk_create(instances[i:i + chunk_size])