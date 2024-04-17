def save_session(request, key, data):
    """Saves the data to session"""
    request.session[key] = data


def retrieve_session(request, key):
    "retrieves session data by key"
    return request.session.get(key)
