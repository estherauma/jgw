from common.const.value_const import NOT_SPECIFIED


def get_or_create_model_instance(model, value):
    if not value:
        instance, _ = model.objects.get_or_create(name=NOT_SPECIFIED)
    else:
        instances = model.objects.filter(name=value)
        if instances.exists():
            # Handle the case when the record(s) exist
            instance = instances.first()
        else:
            # Create a new 'model' object with the desired name
            instance = model.objects.create(name=value)
    return instance