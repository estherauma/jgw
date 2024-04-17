from django.middleware.csrf import get_token
from common.const.value_const import SESSION_FILTERS_KEY
from common.utils.preferences import dict_to_querydict
from common.utils.session import retrieve_session, save_session
from core.filters import generic_filter_form_parser


def get_form_filter_params(request, form_class):
    csrf_token = get_token(request)
    session_filters = retrieve_session(request=request, key=SESSION_FILTERS_KEY) or {}
    session_filters["csrfmiddlewaretoken"] = csrf_token

    session_filters_query_dict = dict_to_querydict(session_filters)
    post_data = request.POST

    filter_param = post_data if dict(post_data) else session_filters_query_dict

    filter_form = form_class(request=request, data=filter_param)
    if filter_form.is_valid():
        filters = generic_filter_form_parser(filter_form)

        if dict(post_data):
            save_session(request=request, key=SESSION_FILTERS_KEY, data=dict(post_data))

    return {"filters": filters, "filter_form": filter_form}
