def create_generic_filters_dictionary(
    show_new_user_data=False,
    start_date=None,
    end_date=None,
    destination_countries=None,
    origin_countries=None,
    organisations=None,
    factory_farms=None,
    question_texts=None,
    immigration_status=None,
):
    extra_filters = {}
    if question_texts is not None:
        extra_filters["question_texts"] = question_texts

    return {
        "show_new_user_data": show_new_user_data,
        "start_date": start_date,
        "end_date": end_date,
        "destination_countries": destination_countries,
        "origin_countries": origin_countries,
        "organisations": organisations,
        "factory_farms": factory_farms,
        "immigration_status": immigration_status,
        **extra_filters,
    }


def generic_filter_form_parser(filter_form):
    show_new_user_data = filter_form.cleaned_data["show_new_user_data"]
    start_date = filter_form.cleaned_data["start_date"]
    end_date = filter_form.cleaned_data["end_date"]
    destinations = filter_form.cleaned_data["destination"]
    origins = filter_form.cleaned_data["origin"]
    organisations = filter_form.cleaned_data["organisation"]
    factory_farms = filter_form.cleaned_data["factory_farm"]
    immigration_status = filter_form.cleaned_data["immigration_status"]
    question_texts = filter_form.cleaned_data.get("question_texts")

    return create_generic_filters_dictionary(
        show_new_user_data=show_new_user_data,
        start_date=start_date,
        end_date=end_date,
        destination_countries=destinations,
        origin_countries=origins,
        organisations=organisations,
        factory_farms=factory_farms,
        immigration_status=immigration_status,
        question_texts=question_texts,
    )
