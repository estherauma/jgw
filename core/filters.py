def create_generic_filters_dictionary(
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    factory_farms=None,
    question_texts=None,
):
    extra_filters = {}
    if question_texts is not None:
        extra_filters["question_texts"] = question_texts

    return {
        "start_date": start_date,
        "end_date": end_date,
        "destination_countries": destination_countries,
        "origin_countries": origin_countries,
        "organisations": organisations,
        "factory_farms": factory_farms,
        **extra_filters,
    }


def generic_filter_form_parser(filter_form):
    start_date = filter_form.cleaned_data["start_date"]
    end_date = filter_form.cleaned_data["end_date"]
    destinations = filter_form.cleaned_data["destination"]
    origins = filter_form.cleaned_data["origin"]
    organisations = filter_form.cleaned_data["organisation"]
    factory_farms = filter_form.cleaned_data["factory_farm"]
    question_texts = filter_form.cleaned_data.get("question_texts")

    return create_generic_filters_dictionary(
        start_date=start_date,
        end_date=end_date,
        destination_countries=destinations,
        origin_countries=origins,
        organisations=organisations,
        factory_farms=factory_farms,
        question_texts=question_texts,
    )
